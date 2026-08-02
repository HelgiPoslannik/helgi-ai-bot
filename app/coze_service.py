import time
import requests
import sqlite3
import os
from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger

COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"

# База данных лежит в /data, так как этот путь теперь примонтирован в Railway
DB_PATH = "/data/conversations.db"

# Инициализация базы данных
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (user_id TEXT PRIMARY KEY, conversation_id TEXT)")
conn.commit()

def ask_coze(user_id: str | int, message: str) -> str:
    user_id_str = str(user_id)
    headers = {
        "Authorization": f"Bearer {COZE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Пытаемся достать ID из базы
    cursor.execute("SELECT conversation_id FROM memory WHERE user_id = ?", (user_id_str,))
    row = cursor.fetchone()
    
    payload = {
        "bot_id": COZE_BOT_ID,
        "user_id": user_id_str,
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": message, "content_type": "text"}]
    }
    
    if row:
        payload["conversation_id"] = row[0]
        logger.info(f"Использую сохраненный диалог для {user_id_str}: {row[0]}")

    try:
        response = requests.post(COZE_CHAT_URL, headers=headers, json=payload, timeout=60)
        data = response.json()
        
        chat_data = data.get("data", {}) or {}
        conversation_id = chat_data.get("conversation_id")
        chat_id = chat_data.get("id")

        if not chat_id or not conversation_id:
            return "Ошибка инициализации диалога."

        # Сохраняем conversation_id в базу для будущих обращений
        cursor.execute("INSERT OR REPLACE INTO memory (user_id, conversation_id) VALUES (?, ?)", (user_id_str, conversation_id))
        conn.commit()

        # Ожидание завершения
        is_completed = False
        for _ in range(30):
            time.sleep(2)
            retrieve = requests.get(COZE_RETRIEVE_URL, headers=headers, params={"conversation_id": conversation_id, "chat_id": chat_id}, timeout=10)
            if retrieve.json().get("data", {}).get("status") == "completed":
                is_completed = True
                break
        
        # Получение сообщения
        messages = requests.get(COZE_MESSAGE_URL, headers=headers, params={"conversation_id": conversation_id, "chat_id": chat_id}, timeout=10)
        msg_list = messages.json().get("data") or []
        answer_parts = [item.get("content", "") for item in msg_list if item.get("type") == "answer" and item.get("chat_id") == chat_id]

        return "".join(answer_parts) if answer_parts else "Не удалось получить ответ."

    except Exception as error:
        logger.error(f"Error: {error}")
        return "Ошибка соединения."

def reset_conversation(user_id: str | int) -> bool:
    user_id_str = str(user_id)
    cursor.execute("DELETE FROM memory WHERE user_id = ?", (user_id_str,))
    conn.commit()
    logger.info(f"История сброшена для {user_id_str}")
    return True
