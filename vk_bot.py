import random
import vk_api
import logging

from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType
from google_dialogflow_api import detect_intent_texts
from log_handler import TelegramLogsHandler


LANGUAGE_CODE = 'ru-RU'


def answer_to_message(event, vk_api, project_id):
    question_is_unclear, smart_answer = detect_intent_texts(
        project_id,
        event.user_id,
        event.text,
        LANGUAGE_CODE
    )
    if not question_is_unclear:
        vk_api.messages.send(
            user_id=event.user_id,
            message=smart_answer,
            random_id=random.randint(1, 1000)
        )


if __name__ == '__main__':
    env = Env()
    env.read_env()

    project_id = env.str('GOOGLE_PROJECT_ID')
    admin_session_id = env.str('TG_ADMIN_ID')
    bot_token = env.str('TG_BOT_TOKEN')

    logger = logging.getLogger('Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_token, admin_session_id))

    vk_token = env.str('VK_TOKEN')
    vk_session = vk_api.VkApi(token=vk_token)
    logger.info('vk bot started')

    while True:
        try:
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    answer_to_message(event, vk_api, project_id)
        except Exception as err:
            logger.error('У VK-бота возникла следующая ошибка:')
            logger.exception(err)
