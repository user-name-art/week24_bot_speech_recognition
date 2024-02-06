import json
import argparse
from google.cloud import dialogflow
from environs import Env


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type."""
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
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    response = intents_client.create_intent(
        request={'parent': parent, 'intent': intent}
    )

    print('Intent created: {}'.format(response))


def main():
    env = Env()
    env.read_env()

    project_id = env.str('GOOGLE_PROJECT_ID')

    parser = argparse.ArgumentParser(description='Скрипт передает в DialogFlow данные для обучения.')
    parser.add_argument(
        'file',
        nargs='?',
        default='questions.json',
        help='путь к файлу с данными; если не указан - скрипт ищет questions.json в той же папке, где находится сам.'
    )
    file = parser.parse_args().file

    try:
        with open(file, 'r') as f:
            questions_json = f.read()

        learning_texts = json.loads(questions_json)
        for subject, dialog in learning_texts.items():
            create_intent(project_id, subject, dialog['questions'], [dialog['answer']])
    except Exception as err:
        print(err)


if __name__ == '__main__':
    main()
