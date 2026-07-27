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


    await update.message.reply_text(
        answer
    )


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

    if telegram_app.updater:
        await telegram_app.updater.start_polling()

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
