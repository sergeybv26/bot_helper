"""Модуль с телеграм-ботом"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from environs import Env
from telegram import Bot, Update, ForceReply
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler, Filters
from google.cloud import dialogflow

logger = logging.getLogger('bot-helper')


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


def start(update: Update, context: CallbackContext) -> None:
    """Отправляет приветственное сообщение, когда введена команда /start"""
    user = update.effective_user
    update.message.reply_markdown_v2(fr'Здравствуйте, {user.mention_markdown_v2()}\!',
                                     reply_markup=ForceReply(selective=True)
                                     )


def echo(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение пользователю на основе его запроса"""
    user_id = update.effective_chat['id']
    user_msg = update.message.text
    message = detect_intent_texts(session_id=user_id, text=user_msg, language_code='ru')
    update.message.reply_text(message)


def main() -> None:
    """Запуск бота"""
    env = Env()
    env.read_env()
    bot_token = env('BOT_TOKEN')
    chat_id = env('CHAT_ID')
    adm_bot_token = env('ADM_BOT_TOKEN')
    project_id = env('PROJECT_ID')

    adm_bot = Bot(token=adm_bot_token)

    log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)s %(message)s')

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, 'bot-app.log')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)

    log_file = RotatingFileHandler(path, maxBytes=20000, backupCount=2, encoding='utf-8')
    log_file.setFormatter(log_formatter)

    log_tlg = TelegramLogsHandler(tg_bot=adm_bot, chat_id=chat_id)
    log_tlg.setLevel(logging.INFO)

    logger.addHandler(stream_handler)
    logger.addHandler(log_file)
    logger.addHandler(log_tlg)
    logger.setLevel(logging.DEBUG)

    logger.info('Телеграм-бот хэлпер запущен!')

    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
