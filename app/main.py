from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from app.config import BOT_TOKEN
from app.subscription import check_subscription
from app.coze_service import ask_coze
from app.logger import logger

app = FastAPI()

telegram_app = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .build()
)

TELEGRAM_MAX_LENGTH = 4000  # с небольшим запасом от лимита Telegram в 4096


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
    if await check_subscription(user.id):
        await update.message.reply_text(
            "✅ Доступ подтверждён.\n"
            "Задавай свой вопрос."
        )
    else:
        await update.message.reply_text(
            "❌ Нет активной подписки."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not await check_subscription(user.id):
        await update.message.reply_text(
            "❌ Доступ закрыт. Нужна активная подписка."
        )
        return

    logger.info(
        f"User {user.id}: {text}"
    )

    answer = ask_coze(
        user_id=user.id,
        message=text
    )

    await send_long_message(update.message, answer)


telegram_app.add_handler(
    CommandHandler(
        "start",
        start_command
    )
)
telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)


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
