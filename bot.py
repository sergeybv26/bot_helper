"""Модуль с ботом"""
import logging
import os
import random
import sys
from logging.handlers import RotatingFileHandler

from environs import Env
from telegram import Bot
from google.cloud import dialogflow
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

logger = logging.getLogger('bot-helper')

log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)s %(message)s')

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'bot-app.log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)

log_file = RotatingFileHandler(path, maxBytes=20000, backupCount=2, encoding='utf-8')
log_file.setFormatter(log_formatter)

logger.addHandler(stream_handler)
logger.addHandler(log_file)

logger.setLevel(logging.DEBUG)


class TelegramLogsHandler(logging.Handler):
    """Обработчик логов. Отправляет логи в Телеграм"""

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record) -> None:
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(session_id, text, language_code, project_id='dvmn-proj'):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    logger.debug("Session path: {}\n".format(session))

    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    logger.debug("Query text: {}".format(response.query_result.query_text))
    logger.debug(
        "Detected intent: {} (confidence: {})\n".format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence,
        )
    )
    logger.debug("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
    return response.query_result.fulfillment_text


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000)
    )


def main() -> None:
    """Запуск бота"""
    env = Env()
    env.read_env()
    vk_token = env('VK_KEY')
    chat_id = env('CHAT_ID')
    adm_bot_token = env('ADM_BOT_TOKEN')
    project_id = env('PROJECT_ID')

    adm_bot = Bot(token=adm_bot_token)

    log_tlg = TelegramLogsHandler(tg_bot=adm_bot, chat_id=chat_id)
    log_tlg.setLevel(logging.INFO)
    logger.addHandler(log_tlg)

    vk_session = vk.VkApi(token=vk_token)

    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)


if __name__ == '__main__':
    main()
