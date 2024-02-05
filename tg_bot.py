import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from google_dialogflow_api import detect_intent_texts
from log_handler import TelegramLogsHandler
from functools import partial


logger = logging.getLogger('Logger')

LANGUAGE_CODE = 'ru-RU'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def answer_to_message(update: Update, context: CallbackContext, project_id) -> None:
    try:
        session_id = update.message.from_user.id
        question_is_unclear, smart_answer = detect_intent_texts(
            project_id,
            session_id,
            update.message.text,
            LANGUAGE_CODE
        )
        update.message.reply_text(smart_answer)
    except Exception as err:
        logger.error('У Telegram-бота возникла следующая ошибка:')
        logger.exception(err)


def main() -> None:
    env = Env()
    env.read_env()

    bot_token = env.str('TG_BOT_TOKEN')
    project_id = env.str('GOOGLE_PROJECT_ID')
    admin_session_id = env.str('TG_ADMIN_ID')

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_token, admin_session_id))

    updater = Updater(bot_token)
    logger.info('tg bot started')
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            partial(answer_to_message, project_id=project_id)
        )
    )

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
