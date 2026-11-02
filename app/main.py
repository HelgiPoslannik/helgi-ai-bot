from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

FREE_MESSAGE_LIMIT = 5
# Счётчик бесплатных сообщений в оперативной памяти (user_id -> количество использованных).
# При перезапуске сервера на Railway счётчик обнулится.
USER_FREE_MESSAGES = {}

SUBSCRIBE_URL = "https://t.me/tribute/app?startapp=s11Qp"
SUPPORT_URL = "https://t.me/divina_conscientia"

SUBSCRIBE_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎁 Начать бесплатный час", url=SUBSCRIBE_URL)],
    [InlineKeyboardButton("💬 Не получается оплатить? Написать мне", url=SUPPORT_URL)],
])

LAST_FREE_REMINDER = (
    "💡 У тебя остался 1 бесплатный вопрос. Задай тот, который волнует тебя "
    "сильнее всего. А когда он закончится, сможешь открыть клуб: первый час бесплатно."
)

SUBSCRIBE_MESSAGE = """🛑 <b>Твои 5 бесплатных вопросов закончились</b>

Ты задал 5 вопросов подряд, значит, эта тема для тебя живая. Это хороший знак: ассистент попал в точку, и дальше можно идти намного глубже.

🎁 <b>Первый час в клубе — бесплатно</b>
Нужно только привязать карту, чтобы активировать доступ. Не понравится — отмени в течение часа, и ничего не спишется. Понравится — просто оставайся: подписка продлится автоматически (первый месяц 9€, дальше 11€/мес). Отменить можно в любой момент.

✨ <b>Что откроется сразу после входа</b>
🤖 Безлимитный ИИ-ассистент: разбирай сколько угодно вопросов, когда угодно
🎥 Закрытые эфиры с разборами: 10 записей уже ждут тебя
📚 17 материалов: таблицы, схемы и чек-листы
🧘 8 практик, с которыми можно работать прямо сегодня
🩺 База 300+ заболеваний и их психологических причин, включая таблицу «эмоции → гормоны → тело»
🎓 Обучение эмоциональному интеллекту и психосоматике

⏱ <b>Что успеешь за бесплатный час</b>
1. Разобрать свой запрос с ассистентом без лимита
2. Посмотреть эфир «Сила принятия» или «Обида. Как избавиться навсегда?»
3. Пройти практику «Избавление от страхов и тревог»
4. Найти свой симптом в «Таблице болезней и их причин»

🎥 <b>Записи эфиров</b>
• Сила принятия
• Самодостаточность
• Ценности
• Сила благодарности
• Любовь: её важность и значение
• Самоуважение
• Страх: как он работает и как с ним справиться
• Обида. Как избавиться навсегда?
• Доверие и его сила
• Избавление от чувства вины

📚 <b>Материалы клуба</b>
• Таблица болезней и их причин
• Чек-лист по фиксации эмоций
• Эндокринная система
• Где живут непрожитые эмоции
• Дневник эмоций
• Как формируется болезнь (схема)
• Таблица эмоций и причин их возникновения
• Карта сохранения энергии
• Топография чакр, органов и психосоматических блоков
• Иерархическая модель личности и сознания
• Чек-лист: уверенное и неуверенное поведение
• Чек-лист: доверие к себе
• Эмпатия: определение
• Высокий и низкий уровень управления эмоциями
• Забота: что это?
• Что провоцирует депрессию?
• Убеждения для снятия обид и ожиданий

🧘 <b>Практики</b>
1. Наполнение любовью
2. Освобождение прошлых версий
3. Избавление от страхов и тревог
4. Избавление от страха смерти и болезней
5. Два вида мотивации: как начать действовать
6. Возврат энергии из прошлого
7. 5 стратегий решения конфликтов
8. Калибровка внутреннего голоса

💳 <b>Условия</b>
• Первый час — бесплатно (нужна привязка карты)
• Первый месяц — 9€
• Далее — 11€/мес
• Год сразу — 120€ (это 10€ в месяц, доступ 24/7)

Для сравнения: одна консультация специалиста нередко стоит дороже, чем целый год клуба.

🙋 <b>Не получается оплатить?</b>
Если карта не привязывается или возникают проблемы с оплатой, напиши мне лично: @divina_conscientia. Подберём другой способ оплаты.

👇 Нажми кнопку ниже, и твой бесплатный час начнётся."""


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
            "Привет! Я твой ИИ-ассистент по психосоматике.\n\n"
            f"У тебя есть {FREE_MESSAGE_LIMIT} бесплатных вопросов — можешь сразу "
            "написать, что тебя беспокоит."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id_str = str(user.id)

    is_subscribed = await check_subscription(user.id)
    used_after = None

    if not is_subscribed:
        used = USER_FREE_MESSAGES.get(user_id_str, 0)
        if used >= FREE_MESSAGE_LIMIT:
            await update.message.reply_text(
                SUBSCRIBE_MESSAGE,
                parse_mode="HTML",
                reply_markup=SUBSCRIBE_KEYBOARD
            )
            return
        used_after = used + 1
        USER_FREE_MESSAGES[user_id_str] = used_after

    logger.info(
        f"User {user.id}: {text}"
    )

    answer = ask_coze(
        user_id=user.id,
        message=text
    )

    await send_long_message(update.message, answer)

    # Напоминание: после предпоследнего бесплатного вопроса
    if used_after is not None and FREE_MESSAGE_LIMIT - used_after == 1:
        await update.message.reply_text(LAST_FREE_REMINDER)


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
