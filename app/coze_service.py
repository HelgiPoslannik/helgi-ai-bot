import time
import requests

from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger


COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"


def ask_coze(user_id: str, message: str):

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

            logger.error(
                f"Coze chat error: {data}"
            )

            return "Ошибка Coze."



        chat_id = data["data"]["id"]

        conversation_id = data["data"]["conversation_id"]



        # Ждём завершения генерации

        for i in range(15):

            time.sleep(2)


            retrieve = requests.get(
                COZE_RETRIEVE_URL,
                headers=headers,
                params={
                    "conversation_id": conversation_id,
                    "chat_id": chat_id
                },
                timeout=60
            )


            retrieve_data = retrieve.json()


            logger.info(
                f"Coze retrieve {i+1}: {retrieve_data}"
            )


            status = (
                retrieve_data
                .get("data", {})
                .get("status")
            )


            if status == "completed":

                break


            if status in (
                "failed",
                "requires_action"
            ):

                logger.error(
                    f"Coze generation failed: {retrieve_data}"
                )

                return "Ошибка Coze."



        messages = requests.get(
            COZE_MESSAGE_URL,
            headers=headers,
            params={
                "conversation_id": conversation_id,
                "chat_id": chat_id
            },
            timeout=60
        )


        messages_data = messages.json()


        logger.info(
            f"Coze messages: {messages_data}"
        )



        if messages_data.get("code") != 0:

            logger.error(
                f"Coze messages error: {messages_data}"
            )

            return "Ответ не получен."



        # Получаем только финальный ответ ассистента

        for item in messages_data.get("data", []):

            if (
                item.get("role") == "assistant"
                and item.get("type") == "answer"
            ):

                answer = item.get(
                    "content",
                    ""
                )


                if answer:

                    logger.info(
                        f"FINAL ANSWER LENGTH: {len(answer)}"
                    )


                    return answer



        logger.error(
            "Assistant answer not found in Coze response"
        )


        return "Ответ не получен."



    except Exception as error:


        logger.error(
            f"Coze exception: {error}"
        )


        return "Ошибка Coze."
