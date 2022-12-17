"""Модуль с телеграм-ботом"""
import logging

from environs import Env
from telegram import Update, Bot, ForceReply
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler, Filters

from bot import detect_intent_texts

logger = logging.getLogger('bot-helper')


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
    dialogflow_response = detect_intent_texts(session_id=user_id, text=user_msg)
    message = dialogflow_response.fulfillment_text
    update.message.reply_text(message)


def main() -> None:
    """Запуск бота"""
    env = Env()
    env.read_env()
    bot_token = env('BOT_TOKEN')

    logger.info('Телеграм-бот хэлпер запущен!')

    updater = Updater(bot_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
