import asyncio

from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from app.config import BOT_TOKEN
from app.subscription import check_subscription
from app.coze_service import ask_coze, close_client
from app.texts import TEXTS, LANG_NAMES, detect_lang
from app.logger import logger

app = FastAPI()

# concurrent_updates(True): бот обрабатывает много сообщений одновременно,
# а не по очереди
telegram_app = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .concurrent_updates(True)
    .build()
)

TELEGRAM_MAX_LENGTH = 4000  # с небольшим запасом от лимита Telegram в 4096

FREE_MESSAGE_LIMIT = 5
# Счётчик бесплатных сообщений в оперативной памяти (user_id -> количество использованных).
# При перезапуске сервера на Railway счётчик обнулится.
USER_FREE_MESSAGES = {}

SUBSCRIBE_URL = "https://t.me/tribute/app?startapp=s11Qp"
SUPPORT_URL = "https://t.me/divina_conscientia"


def build_keyboard(t):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t["btn_join"], url=SUBSCRIBE_URL)],
        [InlineKeyboardButton(t["btn_support"], url=SUPPORT_URL)],
    ])


def tag_message(user, text: str) -> str:
    """
    Добавляет к сообщению техническую пометку с языком Telegram пользователя,
    чтобы ИИ в Coze знал, на каком языке отвечать.
    """
    code = (user.language_code or "").lower()
    if not code:
        return text
    base = code.replace("_", "-").split("-")[0]
    name = LANG_NAMES.get(base)
    label = f"{code} ({name})" if name else code
    return f"[user_language: {label}]\n{text}"


async def keep_typing(bot, chat_id, stop_event: asyncio.Event):
    """Показывает «печатает…», пока ИИ готовит ответ."""
    while not stop_event.is_set():
        try:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=4)
        except asyncio.TimeoutError:
            pass


async def send_long_message(message, text: str):
    """
    Отправляет длинный текст, разбивая его на несколько сообщений,
    если он превышает лимит Telegram на длину одного сообщения.
    """
    if len(text) <= TELEGRAM_MAX_LENGTH:
        await message.reply_text(text)
        return

    chunks = []
    current = ""
    for paragraph in text.split("\n"):
        candidate = f"{current}\n{paragraph}" if current else paragraph
        if len(candidate) > TELEGRAM_MAX_LENGTH:
            if current:
                chunks.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        chunks.append(current)

    for chunk in chunks:
        await message.reply_text(chunk)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    t = TEXTS[detect_lang(user.language_code)]

    if await check_subscription(user.id):
        await update.message.reply_text(t["start_subscribed"])
    else:
        await update.message.reply_text(
            t["start"].format(limit=FREE_MESSAGE_LIMIT),
            parse_mode="HTML",
            reply_markup=build_keyboard(t)
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id_str = str(user.id)
    t = TEXTS[detect_lang(user.language_code)]

    is_subscribed = await check_subscription(user.id)
    used_after = None

    if not is_subscribed:
        used = USER_FREE_MESSAGES.get(user_id_str, 0)
        if used >= FREE_MESSAGE_LIMIT:
            await update.message.reply_text(
                t["paywall"],
                parse_mode="HTML",
                reply_markup=build_keyboard(t)
            )
            return
        used_after = used + 1
        USER_FREE_MESSAGES[user_id_str] = used_after

    logger.info(f"User {user.id} ({user.language_code}): {text}")

    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(
        keep_typing(context.bot, update.effective_chat.id, stop_typing)
    )
    try:
        answer = await ask_coze(
            user_id=user.id,
            message=tag_message(user, text)
        )
    finally:
        stop_typing.set()
        await typing_task

    if answer is None:
        # Ответ не получился: возвращаем человеку потраченный бесплатный вопрос
        if used_after is not None:
            USER_FREE_MESSAGES[user_id_str] = max(
                0, USER_FREE_MESSAGES.get(user_id_str, 1) - 1
            )
        await update.message.reply_text(t["error"])
        return

    await send_long_message(update.message, answer)

    # Напоминание: после предпоследнего бесплатного вопроса
    if used_after is not None and FREE_MESSAGE_LIMIT - used_after == 1:
        await update.message.reply_text(t["reminder"])


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Unhandled error: {context.error!r}")


telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
telegram_app.add_error_handler(error_handler)


@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(
        drop_pending_updates=True
    )
    logger.info("Telegram bot started")


@app.on_event("shutdown")
async def shutdown():
    if telegram_app.updater:
        await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()
    await close_client()


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(
        data,
        telegram_app.bot
    )
    await telegram_app.process_update(update)
    return {
        "ok": True
    }


@app.get("/")
async def home():
    return {
        "status": "Helgi AI Bot is running"
    }
