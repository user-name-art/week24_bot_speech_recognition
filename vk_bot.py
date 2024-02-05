import random
import vk_api
import logging

from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType
from google_dialogflow_api import detect_intent_texts
from log_handler import TelegramLogsHandler


env = Env()
env.read_env()

PROJECT_ID = env.str('GOOGLE_PROJECT_ID')
LANGUAGE_CODE = 'ru-RU'
SESSION_ID = env.str('TG_USER_ID')
BOT_TOKEN = env.str('TG_BOT_TOKEN')


def answer_to_message(event, vk_api):
    question_is_unclear, smart_answer = detect_intent_texts(
        PROJECT_ID,
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
    logger = logging.getLogger('Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(BOT_TOKEN, SESSION_ID))

    vk_token = env.str('VK_TOKEN')
    vk_session = vk_api.VkApi(token=vk_token)
    logger.info('vk bot started')

    while True:
        try:
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    answer_to_message(event, vk_api)
        except Exception as err:
            logger.error('У VK-бота возникла следующая ошибка:')
            logger.exception(err)
