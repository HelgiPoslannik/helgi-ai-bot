import time
import requests

from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger


COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"


def ask_coze(
    user_id: str,
    message: str
):

    headers = {
        "Authorization": f"Bearer {COZE_TOKEN}",
        "Content-Type": "application/json"
    }


    payload = {
        "bot_id": COZE_BOT_ID,
        "user_id": str(user_id),
        "stream": False,
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
            COZE_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        data = response.json()

        logger.info(
            f"Coze RAW response: {data}"
        )


        if data.get("code") != 0:
            return "Ошибка Coze"


        conversation_id = data["data"]["conversation_id"]


        time.sleep(5)


        messages_response = requests.get(
            COZE_MESSAGE_URL,
            headers=headers,
            params={
                "conversation_id": conversation_id
            },
            timeout=60
        )


        messages_data = messages_response.json()


        logger.info(
            f"Coze messages: {messages_data}"
        )


        for item in messages_data.get("data", []):

            if item.get("role") == "assistant":

                return item.get(
                    "content",
                    "Ответ пустой"
                )


        return "Ответ не получен."


    except Exception as error:

        logger.error(
            f"Coze error: {error}"
        )

        return "Произошла ошибка Coze."
