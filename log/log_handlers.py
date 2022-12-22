"""В данном модуле содержатся обработчики логов"""
import logging

from telegram import Bot


class TelegramLogsHandler(logging.Handler):
    """Обработчик логов. Отправляет логи в Телеграм"""

    def __init__(self, tg_chat_id, tg_adm_bot_token):
        super().__init__()
        self.chat_id = tg_chat_id
        self.adm_bot_token = tg_adm_bot_token
        self.tg_bot = Bot(token=self.adm_bot_token)

    def emit(self, record) -> None:
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)
