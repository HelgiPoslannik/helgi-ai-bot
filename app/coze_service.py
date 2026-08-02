import time
import requests
import sqlite3
import os
from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger

COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"

# ==========================================
# НАСТРОЙКА БАЗЫ ДАННЫХ ДЛЯ ПАМЯТИ
# ==========================================
# Указываем путь к базе данных. На Railway это будет папка /data (постоянный диск)
DB_DIR = "/data"
# Если папки /data нет (например, сервер еще не настроен), создаем базу в текущей папке
if not os.path.exists(DB_DIR):
    DB_DIR = "."
    
DB_PATH = os.path.join(DB_DIR, "conversations.db")

# Создаем или подключаем базу данных
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        user_id TEXT PRIMARY KEY,
        conversation_id TEXT
    )
""")
conn.commit()
# ==========================================

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
    
    # 1. СОХРАНЕНИЕ КОНТЕКСТА: Читаем из базы
    cursor.execute("SELECT conversation_id FROM memory WHERE user_id = ?", (user_id_str,))
    row = cursor.fetchone()
    if row:
        payload["conversation_id"] = row[0]

    try:
        response = requests.post(
            COZE_CHAT_URL,
            headers=headers,
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

        # Записываем новый или обновляем старый conversation_id в базу
        cursor.execute(
            "INSERT OR REPLACE INTO memory (user_id, conversation_id) VALUES (?, ?)", 
            (user_id_str, conversation_id)
        )
        conn.commit()

        # 2. ОЖИДАНИЕ ЗАВЕРШЕНИЯ ГЕНЕРАЦИИ (30 попыток по 2 секунды = 60 секунд)
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

        # Если за 60 секунд генерация не завершилась
        if not is_completed:
            logger.warning(f"Coze timeout for chat_id={chat_id}, user={user_id_str}")
            return "Генерация ответа занимает слишком много времени. Попробуйте повторить через несколько секунд."

        # 3. ПОЛУЧЕНИЕ ПОЛНОГО ОТВЕТА
        messages = requests.get(
            COZE_MESSAGE_URL,
            headers=headers,
            params={"conversation_id": conversation_id, "chat_id": chat_id},
            timeout=10
        )
        messages_data = messages.json()
        
        # Фильтруем сообщения именно текущего chat_id с типом answer
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
    """
    user_id_str = str(user_id)
    cursor.execute("SELECT 1 FROM memory WHERE user_id = ?", (user_id_str,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM memory WHERE user_id = ?", (user_id_str,))
        conn.commit()
        logger.info(f"Conversation reset for user {user_id_str}")
        return True
    return False
