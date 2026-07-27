import time
from telegram import Bot

from app.config import BOT_TOKEN, CHANNEL_ID, CACHE_TIME
from app.logger import logger


bot = Bot(token=BOT_TOKEN)


subscription_cache = {}


async def check_subscription(user_id: int) -> bool:
    """
    Проверка подписки пользователя на закрытый Telegram-канал.
    Результат сохраняется в кэше на CACHE_TIME секунд.
    """

    current_time = time.time()

    # Проверяем кэш
    if user_id in subscription_cache:
        data = subscription_cache[user_id]

        if current_time - data["time"] < CACHE_TIME:
            return data["status"]


    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )

        status = member.status


        allowed = status in [
            "member",
            "administrator",
            "creator"
        ]


        # сохраняем результат
        subscription_cache[user_id] = {
            "status": allowed,
            "time": current_time
        }


        logger.info(
            f"Subscription check: user={user_id}, status={status}"
        )


        return allowed


    except Exception as error:

        logger.error(
            f"Subscription error user={user_id}: {error}"
        )

        return False
