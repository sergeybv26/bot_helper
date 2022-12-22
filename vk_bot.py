"""Модуль с VK-ботом"""
import logging
import logging.config
import random

from environs import Env
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from google_dialogflow_api import detect_intent_texts
from log.config import log_config
from log.log_handlers import TelegramLogsHandler

logger = logging.getLogger('bot-helper')


def send_msg(event, vk_api, dialogflow_response):
    if dialogflow_response.intent.is_fallback:
        return None
    help_msg = dialogflow_response.fulfillment_text
    vk_api.messages.send(
        user_id=event.user_id,
        message=help_msg,
        random_id=random.randint(1, 1000)
    )


def main() -> None:
    """Запуск бота"""
    env = Env()
    env.read_env()
    vk_token = env('VK_KEY')
    project_id = env('PROJECT_ID')
    tg_adm_bot_token = env('TG_ADM_BOT_TOKEN')
    tg_adm_chat_id = env('TG_ADM_CHAT_ID')

    logging.config.dictConfig(log_config)
    tg_log_handler = TelegramLogsHandler(tg_adm_chat_id, tg_adm_bot_token)
    logger.addHandler(tg_log_handler)

    logger.info('ВК-бот запущен')

    try:
        vk_session = vk.VkApi(token=vk_token)

        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                dialogflow_response = detect_intent_texts(session_id=event.user_id,
                                                          text=event.text, project_id=project_id)
                send_msg(event, vk_api, dialogflow_response)
    except Exception as err:
        logger.critical(f'Бот упал с ошибкой: {err}')


if __name__ == '__main__':
    main()

