import time
import requests
from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger

COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"

# Хранилище сессий в оперативной памяти (user_id -> conversation_id).
# При перезапуске сервера на Railway память очистится.
USER_CONVERSATIONS = {}


def ask_coze(user_id: str | int, message: str) -> str:
    """
    Отправляет сообщение в Coze API, сохраняя контекст диалога для пользователя.
    """
    headers = {
        "Authorization": f"Bearer {COZE_TOKEN}",
        "Content-Type": "application/json"
    }

    user_id_str = str(user_id)

    payload = {
        "bot_id": COZE_BOT_ID,
        "user_id": user_id_str,
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

    # ВАЖНО: Coze принимает conversation_id ТОЛЬКО как параметр URL (query string),
    # а не как поле внутри JSON. Это и было причиной потери контекста.
    query_params = {}
    if user_id_str in USER_CONVERSATIONS:
        query_params["conversation_id"] = USER_CONVERSATIONS[user_id_str]

    try:
        response = requests.post(
            COZE_CHAT_URL,
            headers=headers,
            params=query_params,
            json=payload,
            timeout=60
        )
        data = response.json()
        logger.info(f"Coze RAW response for user {user_id_str}: {data}")

        if data.get("code") != 0:
            logger.error(f"Coze API Error Code: {data.get('code')}, msg: {data.get('msg')}")
            return "Произошла ошибка при обращении к ИИ. Попробуйте ещё раз."

        chat_data = data.get("data", {}) or {}
        chat_id = chat_data.get("id")
        conversation_id = chat_data.get("conversation_id")

        if not chat_id or not conversation_id:
            logger.error(f"Missing chat_id or conversation_id in response for user {user_id_str}: {data}")
            return "Ошибка инициализации диалога."

        # Сохраняем conversation_id для следующих запросов этого пользователя
        USER_CONVERSATIONS[user_id_str] = conversation_id

        # ждём завершения генерации (30 попыток по 2 секунды = 60 секунд)
        is_completed = False
        for _ in range(30):
            time.sleep(2)
            retrieve = requests.get(
                COZE_RETRIEVE_URL,
                headers=headers,
                params={"conversation_id": conversation_id, "chat_id": chat_id},
                timeout=10
            )
            retrieve_data = retrieve.json()
            status = retrieve_data.get("data", {}).get("status")
            logger.info(f"Coze status for user {user_id_str}: {status}")

            if status == "completed":
                is_completed = True
                break
            if status in ("failed", "requires_action"):
                logger.error(f"Coze chat ended with status={status} for user {user_id_str}")
                return "Не удалось сгенерировать ответ. Попробуйте повторить запрос."

        if not is_completed:
            logger.warning(f"Coze timeout for chat_id={chat_id}, user={user_id_str}")
            return "Генерация ответа занимает слишком много времени. Попробуйте повторить через несколько секунд."

        messages = requests.get(
            COZE_MESSAGE_URL,
            headers=headers,
            params={"conversation_id": conversation_id, "chat_id": chat_id},
            timeout=10
        )
        messages_data = messages.json()

        msg_list = messages_data.get("data") or []
        answer_parts = [
            item.get("content", "")
            for item in msg_list
            if item.get("type") == "answer" and item.get("chat_id") == chat_id
        ]

        if answer_parts:
            return "".join(answer_parts)

        logger.warning(f"No answer parts found for user {user_id_str}, chat_id {chat_id}")
        return "Не удалось получить сформированный ответ."

    except Exception as error:
        logger.error(f"Coze request error for user {user_id_str}: {error}")
        return "Ошибка соединения с сервером ИИ."


def reset_conversation(user_id: str | int) -> bool:
    """
    Сбрасывает историю диалога конкретного пользователя.
    Возвращает True, если контекст был успешно удален.
    """
    user_id_str = str(user_id)
    if user_id_str in USER_CONVERSATIONS:
        del USER_CONVERSATIONS[user_id_str]
        logger.info(f"Conversation reset for user {user_id_str}")
        return True
    return False
