from environs import Env
import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from utils import detect_intent_texts

env = Env()
env.read_env()

vk_token = env.str('VK_TOKEN')
PROJECT_ID = env.str('GOOGLE_PROJECT_ID')
LANGUAGE_CODE = 'ru-RU'


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000)
    )


def smart_answer(event, vk_api):
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
    vk_session = vk_api.VkApi(token=vk_token)

    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            smart_answer(event, vk_api)
