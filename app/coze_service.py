import time
import requests
import sqlite3
import os
from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger

COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"

DB_DIR = "/data"
if not os.path.exists(DB_DIR):
    DB_DIR = "."
DB_PATH = os.path.join(DB_DIR, "conversations.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (user_id TEXT PRIMARY KEY, conversation_id TEXT)")
conn.commit()

def ask_coze(user_id: str | int, message: str) -> str:
    user_id_str = str(user_id)
    headers = {"Authorization": f"Bearer {COZE_TOKEN}", "Content-Type": "application/json"}
    
    # --- МАЯЧОК: Проверка базы ---
    cursor.execute("SELECT conversation_id FROM memory WHERE user_id = ?", (user_id_str,))
    row = cursor.fetchone()
    
    payload = {"bot_id": COZE_BOT_ID, "user_id": user_id_str, "stream": False, "auto_save_history": True, "additional_messages": [{"role": "user", "content": message, "content_type": "text"}]}

    if row:
        logger.info(f"MEMORY FOUND: Для пользователя {user_id_str} найден ID {row[0]}")
        payload["conversation_id"] = row[0]
    else:
        logger.info(f"NEW CHAT: Для пользователя {user_id_str} история не найдена, начинаем новый диалог.")

    try:
        response = requests.post(COZE_CHAT_URL, headers=headers, json=payload, timeout=60)
        data = response.json()
        
        chat_data = data.get("data", {}) or {}
        chat_id = chat_data.get("id")
        conversation_id = chat_data.get("conversation_id")

        if not chat_id or not conversation_id:
            return "Ошибка инициализации диалога."

        # Сохраняем в базу
        cursor.execute("INSERT OR REPLACE INTO memory (user_id, conversation_id) VALUES (?, ?)", (user_id_str, conversation_id))
        conn.commit()

        # ... (код ожидания завершения остается прежним, я его пропущу для краткости, чтобы ты просто вставил этот кусок) ...
        # (Просто вставь весь этот код, я ниже допишу остаток)
        
        is_completed = False
        for _ in range(30):
            time.sleep(2)
            retrieve = requests.get(COZE_RETRIEVE_URL, headers=headers, params={"conversation_id": conversation_id, "chat_id": chat_id}, timeout=10)
            status = retrieve.json().get("data", {}).get("status")
            if status == "completed":
                is_completed = True
                break
        
        messages = requests.get(COZE_MESSAGE_URL, headers=headers, params={"conversation_id": conversation_id, "chat_id": chat_id}, timeout=10)
        msg_list = messages.json().get("data") or []
        answer_parts = [item.get("content", "") for item in msg_list if item.get("type") == "answer" and item.get("chat_id") == chat_id]

        if answer_parts:
            return "".join(answer_parts)
        return "Не удалось получить ответ."

    except Exception as error:
        logger.error(f"Error: {error}")
        return "Ошибка соединения."
