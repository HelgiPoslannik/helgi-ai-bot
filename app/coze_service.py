import requests

from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger


COZE_URL = "https://api.coze.com/v3/chat"


def ask_coze(
    user_id: str,
    message: str
):
    """
    Отправляет сообщение в Coze Agent
    и получает ответ.
    """

    headers = {
        "Authorization": f"Bearer {COZE_TOKEN}",
        "Content-Type": "application/json"
    }


    payload = {
        "bot_id": COZE_BOT_ID,
        "user_id": str(user_id),
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": message,
                "content_type": "text"
            }
        ]
    }


    try:

        response = requests.post(
            COZE_URL,
            headers=headers,
            json=payload,
            timeout=60
        )


        response.raise_for_status()

        data = response.json()


        logger.info(
            f"Coze response user={user_id}"
        )


        # Здесь будет обработка ответа Coze
        # после проверки формата API

        return extract_answer(data)


    except Exception as error:

        logger.error(
            f"Coze error user={user_id}: {error}"
        )

        return (
            "Произошла временная ошибка. "
            "Попробуйте отправить сообщение ещё раз."
        )



def extract_answer(data):

    """
    Извлечение текста ответа Coze.
    """

    try:

        messages = data.get(
            "messages",
            []
        )


        for message in messages:

            if message.get("role") == "assistant":

                return message.get(
                    "content",
                    ""
                )


    except Exception as error:

        logger.error(
            f"Extract answer error: {error}"
        )


    return "Ответ не получен."
