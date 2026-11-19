import asyncio
import time

import httpx

from app.config import COZE_TOKEN, COZE_BOT_ID
from app.logger import logger

COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"

# ---------------- Настройки нагрузки ----------------
# Сколько запросов в секунду бот отправляет в Coze.
# Если у вас на Coze куплено 2 млн токенов и больше, можно поставить 12.
COZE_MAX_RPS = 4
# Сколько ответов генерируется одновременно.
COZE_MAX_CONCURRENT_CHATS = 30
# Сколько секунд максимум ждём один ответ.
COZE_TIMEOUT_SECONDS = 150
# Коды ошибок Coze «слишком много запросов».
RATE_LIMIT_CODES = {4013, 710005002}
# Паузы между проверками готовности ответа (секунды), дальше всегда POLL_DELAY_MAX.
POLL_DELAYS = [2, 2, 3, 3]
POLL_DELAY_MAX = 4

# Сессии в оперативной памяти (user_id -> conversation_id).
# При перезапуске сервера на Railway память очистится.
USER_CONVERSATIONS = {}
_user_locks = {}

_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0, connect=10.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=50),
)
_chat_slots = asyncio.Semaphore(COZE_MAX_CONCURRENT_CHATS)
_rate_lock = asyncio.Lock()
_next_slot_time = 0.0


def _headers():
    return {
        "Authorization": f"Bearer {COZE_TOKEN}",
        "Content-Type": "application/json",
    }


async def _rate_gate():
    """Не даёт отправлять в Coze больше COZE_MAX_RPS запросов в секунду."""
    global _next_slot_time
    async with _rate_lock:
        now = time.monotonic()
        wait = _next_slot_time - now
        if wait > 0:
            await asyncio.sleep(wait)
            now = time.monotonic()
        _next_slot_time = now + 1.0 / COZE_MAX_RPS


async def _request(method, url, **kwargs):
    """Один запрос к Coze. Возвращает JSON или None при сетевой ошибке."""
    await _rate_gate()
    try:
        response = await _client.request(method, url, headers=_headers(), **kwargs)
    except httpx.HTTPError as error:
        logger.warning(f"Coze network error: {error!r}")
        return None
    if response.status_code == 429:
        return {"code": 4013, "msg": "HTTP 429"}
    try:
        return response.json()
    except ValueError:
        logger.warning(f"Coze returned non-JSON (HTTP {response.status_code})")
        return None


async def ask_coze(user_id, message: str):
    """
    Отправляет сообщение в Coze и возвращает текст ответа.
    Возвращает None, если ответ получить не удалось.
    """
    user_id_str = str(user_id)

    # Сообщения одного и того же человека обрабатываем по очереди,
    # а разных людей — параллельно.
    lock = _user_locks.get(user_id_str)
    if lock is None:
        lock = _user_locks[user_id_str] = asyncio.Lock()

    async with lock:
        async with _chat_slots:
            try:
                return await _ask_coze(user_id_str, message)
            except Exception as error:
                logger.error(f"Coze request error for user {user_id_str}: {error!r}")
                return None


async def _ask_coze(user_id_str: str, message: str):
    payload = {
        "bot_id": COZE_BOT_ID,
        "user_id": user_id_str,
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": message,
                "content_type": "text",
            }
        ],
    }

    # conversation_id передаём параметром URL, чтобы Coze помнил историю диалога
    params = {}
    if user_id_str in USER_CONVERSATIONS:
        params["conversation_id"] = USER_CONVERSATIONS[user_id_str]

    # 1. Создаём чат (с повторами, если Coze просит подождать)
    data = None
    for attempt in range(4):
        data = await _request("POST", COZE_CHAT_URL, params=params, json=payload)
        if data is None:
            await asyncio.sleep(2 * (attempt + 1))
            continue
        if data.get("code") in RATE_LIMIT_CODES:
            logger.warning(f"Coze rate limit on create (attempt {attempt + 1}) for user {user_id_str}")
            await asyncio.sleep(3 * (2 ** attempt))
            continue
        break

    if not data or data.get("code") != 0:
        logger.error(f"Coze create chat failed for user {user_id_str}: {data}")
        return None

    chat_data = data.get("data") or {}
    chat_id = chat_data.get("id")
    conversation_id = chat_data.get("conversation_id")
    if not chat_id or not conversation_id:
        logger.error(f"Missing chat_id/conversation_id for user {user_id_str}: {data}")
        return None

    USER_CONVERSATIONS[user_id_str] = conversation_id

    # 2. Ждём, пока Coze закончит генерацию
    started = time.monotonic()
    delays = iter(POLL_DELAYS)
    while True:
        if time.monotonic() - started > COZE_TIMEOUT_SECONDS:
            logger.warning(f"Coze timeout for chat_id={chat_id}, user={user_id_str}")
            return None

        await asyncio.sleep(next(delays, POLL_DELAY_MAX))

        info = await _request(
            "GET",
            COZE_RETRIEVE_URL,
            params={"conversation_id": conversation_id, "chat_id": chat_id},
        )
        if info is None:
            continue
        code = info.get("code")
        if code in RATE_LIMIT_CODES:
            continue
        if code != 0:
            logger.error(f"Coze retrieve error for user {user_id_str}: {info}")
            return None

        status = (info.get("data") or {}).get("status")
        if status == "completed":
            break
        if status in ("failed", "requires_action", "canceled"):
            logger.error(f"Coze chat ended with status={status} for user {user_id_str}. Full response: {info}")
            return None

    # 3. Забираем готовый ответ
    messages_data = None
    for attempt in range(3):
        messages_data = await _request(
            "GET",
            COZE_MESSAGE_URL,
            params={"conversation_id": conversation_id, "chat_id": chat_id},
        )
        if messages_data is not None and messages_data.get("code") not in RATE_LIMIT_CODES:
            break
        await asyncio.sleep(2 * (attempt + 1))

    if not messages_data or messages_data.get("code") != 0:
        logger.error(f"Coze messages error for user {user_id_str}: {messages_data}")
        return None

    msg_list = messages_data.get("data") or []
    answer_parts = [
        item.get("content", "")
        for item in msg_list
        if item.get("type") == "answer" and item.get("chat_id") == chat_id
    ]

    if answer_parts:
        return "".join(answer_parts)

    logger.warning(f"No answer parts found for user {user_id_str}, chat_id {chat_id}")
    return None


async def close_client():
    await _client.aclose()


def reset_conversation(user_id) -> bool:
    """
    Сбрасывает историю диалога конкретного пользователя.
    Возвращает True, если контекст был успешно удалён.
    """
    user_id_str = str(user_id)
    if user_id_str in USER_CONVERSATIONS:
        del USER_CONVERSATIONS[user_id_str]
        logger.info(f"Conversation reset for user {user_id_str}")
        return True
    return False
