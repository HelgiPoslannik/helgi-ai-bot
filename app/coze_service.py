import time
import requests
from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger

COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"

# Хранилище сессий в оперативной памяти (user_id -> conversation_id).
# При перезапуске сервера на Railway память очистится.
# Для долгосрочного хранения лучше использовать Redis или БД (PostgreSQL/SQLite).
USER_CONVERSATIONS = {}


def ask_coze(user_id: str, message: str):
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
    
    # 1. СОХРАНЕНИЕ КОНТЕКСТА: передаем conversation_id, если диалог уже велся
    if user_id_str in USER_CONVERSATIONS:
        payload["conversation_id"] = USER_CONVERSATIONS[user_id_str]

    try:
        response = requests.post(
            COZE_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        data = response.json()
        logger.info(f"Coze RAW response: {data}")

        if data.get("code") != 0:
            return "Ошибка Coze"

        chat_id = data["data"]["id"]
        conversation_id = data["data"]["conversation_id"]

        # Сохраняем conversation_id для следующих запросов пользователя
        USER_CONVERSATIONS[user_id_str] = conversation_id

        # 2. УБИРАЕМ ОБРЫВЫ: увеличиваем таймаут до 60 секунд (30 попыток по 2 сек)
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
            logger.info(f"Coze status: {status}")

            if status == "completed":
                is_completed = True
                break
            if status in ("failed", "requires_action"):
                logger.error(f"Coze chat ended with status={status}")
                return "Ошибка генерации ответа."

        # Если за 60 секунд генерация не завершилась — не забираем обрубок!
        if not is_completed:
            logger.warning(f"Coze timeout for chat_id={chat_id}")
            return "Запрос занимает слишком много времени. Попробуйте повторить через несколько секунд."

        # 3. ПОЛУЧЕНИЕ ПОЛНОГО ОТВЕТА
        messages = requests.get(
            COZE_MESSAGE_URL,
            headers=headers,
            params={"conversation_id": conversation_id, "chat_id": chat_id},
            timeout=10
        )
        messages_data = messages.json()
        logger.info(f"Coze messages: {messages_data}")

        # Фильтруем сообщения именно текущего chat_id с типом answer
        answer_parts = [
            item.get("content", "")
            for item in messages_data.get("data", [])
            if item.get("type") == "answer" and item.get("chat_id") == chat_id
        ]

        if answer_parts:
            return "".join(answer_parts)

        return "Ответ не получен."

    except Exception as error:
        logger.error(f"Coze error: {error}")
        return "Ошибка соединения с сервисом."
