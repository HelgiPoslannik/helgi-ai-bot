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


        chat_id = data["data"]["id"]


        # ждём пока Agent закончит генерацию
        time.sleep(5)


        messages_response = requests.get(
            COZE_MESSAGE_URL,
            headers=headers,
            params={
                "chat_id": chat_id
            },
            timeout=60
        )


        messages_data = messages_response.json()


        logger.info(
            f"Coze messages: {messages_data}"
        )


        if messages_data.get("code") != 0:
            return "Ответ не получен."


        messages = messages_data.get(
            "data",
            []
        )


        for item in messages:

            if item.get("role") == "assistant":

                return item.get(
                    "content",
                    "Ответ пустой."
                )


        return "Ответ не получен."


    except Exception as error:

        logger.error(
            f"Coze error: {error}"
        )

        return "Произошла ошибка Coze."
