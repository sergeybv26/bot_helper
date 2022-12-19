"""Модуль с VK-ботом"""
import logging
import random

from environs import Env
from google.cloud import dialogflow
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from log import config

logger = logging.getLogger('bot-helper')


def detect_intent_texts(session_id, text, project_id='dvmn-proj', language_code='ru'):
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
    return response.query_result


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

    vk_session = vk.VkApi(token=vk_token)

    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            dialogflow_response = detect_intent_texts(session_id=event.user_id, text=event.text, project_id=project_id)
            send_msg(event, vk_api, dialogflow_response)


if __name__ == '__main__':
    main()
