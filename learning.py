"""Модуль обучения нейросети тренировочными фразами"""
import json
import logging
import os.path

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
    with open(file_path, 'r', encoding='utf-8') as f:
        intents = json.load(f)
    if not isinstance(intents, dict):
        logger.warning(f'Файл {file_path} не содержит JSON с данными')

    for intent in intents.items():
        display_name = intent[0]
        logger.debug(f'Создается intent {display_name}')
        training_phrases_parts = intent[1].get('questions', [])
        message_texts = (intent[1].get('answer', ''),)
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

        logger.debug("Intent created: {}".format(response))


if __name__ == '__main__':
    print('Начато обучение нейросети')
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, 'jsons/questions.json')
    create_intent('jsons/questions.json')
    print('Обучение нейросети окончено')
