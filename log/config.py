"""Конфигурация логгера"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from environs import Env
from telegram import Bot


class TelegramLogsHandler(logging.Handler):
    """Обработчик логов. Отправляет логи в Телеграм"""

    def __init__(self):
        super().__init__()
        env = Env()
        env.read_env()
        self.chat_id = env('CHAT_ID')
        self.adm_bot_token = env('ADM_BOT_TOKEN')
        self.tg_bot = Bot(token=self.adm_bot_token)

    def emit(self, record) -> None:
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)s %(message)s')

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'bot-app.log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)

log_file = RotatingFileHandler(path, maxBytes=20000, backupCount=2, encoding='utf-8')
log_file.setFormatter(log_formatter)

log_tlg = TelegramLogsHandler()
log_tlg.setLevel(logging.INFO)

logger = logging.getLogger('bot-helper')

logger.addHandler(log_tlg)
logger.addHandler(stream_handler)
logger.addHandler(log_file)


logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.critical('Critical message')
