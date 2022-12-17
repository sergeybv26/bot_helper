"""Модуль обучения нейросети тренировочными фразами"""
import logging

from environs import Env
from google.cloud import dialogflow

logger = logging.getLogger('bot-helper')


def create_intent(file_path):
    """
    Создает обучающий набор фраз DialogFlow
    :param file_path: Путь к файлу с набором фраз
    :return: None
    """
    env = Env()
    env.read_env()
    project_id = env('PROJECT_ID')

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))
