import time
import requests
import redis
from app.config import COZE_TOKEN, COZE_BOT_ID, REDIS_URL
from app.logger import logger

COZE_CHAT_URL = "https://api.coze.com/v3/chat"
COZE_RETRIEVE_URL = "https://api.coze.com/v3/chat/retrieve"
COZE_MESSAGE_URL = "https://api.coze.com/v3/chat/message/list"

# Ключи в Redis будут вида: conv:{user_id} -> conversation_id
CONV_KEY_PREFIX = "conv:"
CONV_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 дней

_redis_client = None
_redis_broken_logged = False

# Запасной вариант в памяти — используется, если Redis недоступен,
# чтобы контекст не терялся хотя бы в рамках жизни контейнера (как было раньше).
_FALLBACK_CONVERSATIONS = {}


def get_redis():
    """
    Ленивая инициализация клиента Redis. Бросает исключение, если REDIS_URL не задан
    или подключиться не удалось — вызывающий код должен это перехватывать.
    """
    global _redis_client
    if _redis_client is None:
        if not REDIS_URL:
            raise RuntimeError("REDIS_URL не задан в переменных окружения")
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)
        _redis_client.ping()
    return _redis_client


def _get_conversation_id(user_id_str: str):
    global _redis_broken_logged
    try:
        client = get_redis()
        value = client.get(f"{CONV_KEY_PREFIX}{user_id_str}")
        if value:
            return value
        return _FALLBACK_CONVERSATIONS.get(user_id_str)
    except Exception as error:
        if not _redis_broken_logged:
            logger.error(f"Redis недоступен, используется запасная память в процессе: {error}")
            _redis_broken_logged = True
        return _FALLBACK_CONVERSATIONS.get(user_id_str)


def _set_conversation_id(user_id_str: str, conversation_id: str) -> None:
    global _redis_broken_logged
    _FALLBACK_CONVERSATIONS[user_id_str] = conversation_id
    try:
        client = get_redis()
        client.set(f"{CONV_KEY_PREFIX}{user_id_str}", conversation_id, ex=CONV_TTL_SECONDS)
    except Exception as error:
        if not _redis_broken_logged:
            logger.error(f"Redis недоступен, используется запасная память в процессе: {error}")
            _redis_broken_logged = True


def ask_coze(user_id: str | int, message: str) -> str:
    """
    Отправляет сообщение в Coze API, сохраняя контекст диалога для пользователя.
    Приоритет — Redis (переживает рестарты), при его недоступности — память процесса.
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

    query_params = {}
    existing_conversation_id = _get_conversation_id(user_id_str)
    if existing_conversation_id:
        query_params["conversation_id"] = existing_conversation_id

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

        _set_conversation_id(user_id_str, conversation_id)

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
    Сбрасывает историю диалога конкретного пользователя (Redis + запасная память).
    """
    user_id_str = str(user_id)
    had_any = user_id_str in _FALLBACK_CONVERSATIONS
    _FALLBACK_CONVERSATIONS.pop(user_id_str, None)
    try:
        deleted = get_redis().delete(f"{CONV_KEY_PREFIX}{user_id_str}")
        if deleted or had_any:
            logger.info(f"Conversation reset for user {user_id_str}")
            return True
        return False
    except Exception as error:
        logger.error(f"Redis DELETE error for user {user_id_str}: {error}")
        return had_any
