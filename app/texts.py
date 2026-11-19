DEFAULT_LANG = "ru"

# Языки Telegram, для которых бот показывает русский интерфейс
RU_FALLBACK = {"be", "kk", "ky", "uz", "tg", "hy", "az", "ka", "tt"}

# Названия языков (подсказка для ИИ, на каком языке отвечать)
LANG_NAMES = {
    "ru": "Russian", "uk": "Ukrainian", "be": "Belarusian", "kk": "Kazakh",
    "en": "English", "de": "German", "es": "Spanish", "fr": "French",
    "it": "Italian", "pl": "Polish", "pt": "Portuguese", "nl": "Dutch",
    "tr": "Turkish", "cs": "Czech", "sk": "Slovak", "ro": "Romanian",
    "bg": "Bulgarian", "hu": "Hungarian", "el": "Greek", "sv": "Swedish",
    "no": "Norwegian", "nb": "Norwegian", "da": "Danish", "fi": "Finnish",
    "lt": "Lithuanian", "lv": "Latvian", "et": "Estonian", "sr": "Serbian",
    "hr": "Croatian", "sl": "Slovenian", "ar": "Arabic", "he": "Hebrew",
    "fa": "Persian", "hi": "Hindi", "zh": "Chinese", "ja": "Japanese",
    "ko": "Korean", "id": "Indonesian", "vi": "Vietnamese", "th": "Thai",
    "uz": "Uzbek", "az": "Azerbaijani", "ka": "Georgian", "hy": "Armenian",
}


def detect_lang(language_code):
    """Возвращает язык интерфейса бота по языку Telegram пользователя."""
    if not language_code:
        return DEFAULT_LANG
    base = language_code.lower().replace("_", "-").split("-")[0]
    if base in TEXTS:
        return base
    if base in RU_FALLBACK:
        return "ru"
    return "en"


TEXTS = {
    # ======================= РУССКИЙ =======================
    "ru": {
        "start_subscribed": "✅ Доступ подтверждён.\nЗадавай свой вопрос.",
        "start": """👋 <b>Привет! Я ИИ-ассистент по психосоматике.</b>

Напиши, что тебя беспокоит: симптом, эмоцию или ситуацию, и я помогу разобраться в психологических причинах.

🎁 У тебя есть <b>{limit} бесплатных вопросов</b>.

А если хочешь больше, можно сразу вступить в закрытый клуб <b>«Центр управления здоровьем»</b>:
🤖 безлимитный ИИ-ассистент
🎥 закрытые эфиры с разборами
📚 материалы и 🧘 практики

<b>Первый час в клубе бесплатно.</b> Нужно только привязать карту. Отменишь в течение часа — ничего не спишется. Останешься — подписка продлится автоматически (первый месяц 9€, дальше 11€/мес, год 120€).

👇 Задай свой первый вопрос или нажми кнопку, чтобы вступить в клуб сейчас.""",
        "reminder": "💡 У тебя остался 1 бесплатный вопрос. Задай тот, который волнует тебя сильнее всего. А когда он закончится, сможешь открыть клуб: первый час бесплатно.",
        "error": "Сейчас много обращений, и ответ не получился. Попробуй написать ещё раз через минуту.",
        "btn_join": "🎁 Вступить в клуб: 1-й час бесплатно",
        "btn_support": "💬 Не получается оплатить? Написать мне",
        "paywall": """🛑 <b>Твои 5 бесплатных вопросов закончились</b>

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

👇 Нажми кнопку ниже, и твой бесплатный час начнётся.""",
    },

    # ======================= ENGLISH =======================
    "en": {
        "start_subscribed": "✅ Access confirmed.\nAsk your question.",
        "start": """👋 <b>Hi! I'm your AI assistant for psychosomatics.</b>

Tell me what's troubling you: a symptom, an emotion or a situation, and I'll help you explore the psychological causes.

🎁 You have <b>{limit} free questions</b>.

Want more? You can join the closed club <b>«Центр управления здоровьем» (Health Management Center)</b> right away:
🤖 unlimited AI assistant
🎥 closed broadcasts with deep dives
📚 materials and 🧘 practices

<b>The first hour in the club is free.</b> You only need to add a card. Cancel within the hour and nothing is charged. Stay, and the subscription renews automatically (first month €9, then €11/month, or €120 per year).

ℹ️ Broadcasts and materials are currently in Russian.

👇 Ask your first question or tap the button to join the club now.""",
        "reminder": "💡 You have 1 free question left. Ask the one that matters to you most. When it's used up, you can open the club: the first hour is free.",
        "error": "There are a lot of requests right now and I couldn't answer. Please try again in a minute.",
        "btn_join": "🎁 Join the club: 1st hour free",
        "btn_support": "💬 Can't pay? Message me",
        "paywall": """🛑 <b>Your 5 free questions are over</b>

Five questions in a row show that this topic matters to you. In the club you can go much deeper.

🎁 <b>First hour in the club — free</b>
Add a card to activate access. Cancel within the hour and nothing is charged. Stay, and the subscription renews automatically: €9 for the first month, then €11/month (or €120 for a year). You can cancel any time.

✨ <b>Inside the club</b>
🤖 Unlimited AI assistant, 24/7
🎥 10 recordings of closed broadcasts
📚 17 materials: tables, diagrams, checklists
🧘 8 practices
🩺 300+ conditions and their psychological causes
ℹ️ Broadcasts and materials are currently in Russian.

🙋 <b>Can't pay?</b> Write to me: @divina_conscientia

👇 Tap the button to start your free hour.""",
    },

    # ======================= УКРАЇНСЬКА =======================
    "uk": {
        "start_subscribed": "✅ Доступ підтверджено.\nСтав своє запитання.",
        "start": """👋 <b>Привіт! Я ШІ-асистент із психосоматики.</b>

Напиши, що тебе турбує: симптом, емоцію чи ситуацію, і я допоможу розібратися в психологічних причинах.

🎁 У тебе є <b>{limit} безкоштовних запитань</b>.

А якщо хочеш більше, можна одразу вступити до закритого клубу <b>«Центр управления здоровьем» (Центр управління здоров'ям)</b>:
🤖 безлімітний ШІ-асистент
🎥 закриті ефіри з розборами
📚 матеріали та 🧘 практики

<b>Перша година в клубі безкоштовно.</b> Потрібно лише прив'язати картку. Скасуєш упродовж години — нічого не спишеться. Залишишся — підписка продовжиться автоматично (перший місяць 9€, далі 11€/міс, рік 120€).

ℹ️ Ефіри та матеріали наразі російською мовою.

👇 Постав своє перше запитання або натисни кнопку, щоб вступити до клубу зараз.""",
        "reminder": "💡 У тебе залишилося 1 безкоштовне запитання. Постав те, що хвилює тебе найбільше. А коли воно закінчиться, ти зможеш відкрити клуб: перша година безкоштовно.",
        "error": "Зараз багато звернень, і відповісти не вийшло. Спробуй написати ще раз за хвилину.",
        "btn_join": "🎁 Вступити до клубу: 1-ша година безкоштовно",
        "btn_support": "💬 Не виходить оплатити? Написати мені",
        "paywall": """🛑 <b>Твої 5 безкоштовних запитань закінчилися</b>

П'ять запитань поспіль означають, що ця тема для тебе жива. У клубі можна піти значно глибше.

🎁 <b>Перша година в клубі — безкоштовно</b>
Щоб активувати доступ, потрібно прив'язати картку. Не сподобається — скасуй упродовж години, і нічого не спишеться. Сподобається — просто залишайся: підписка продовжиться автоматично (перший місяць 9€, далі 11€/міс, або 120€ за рік). Скасувати можна будь-коли.

✨ <b>Що всередині клубу</b>
🤖 Безлімітний ШІ-асистент 24/7
🎥 10 записів закритих ефірів
📚 17 матеріалів: таблиці, схеми, чек-листи
🧘 8 практик
🩺 300+ захворювань та їхні психологічні причини
ℹ️ Ефіри та матеріали наразі російською мовою.

🙋 <b>Не виходить оплатити?</b> Напиши мені: @divina_conscientia

👇 Натисни кнопку, і твоя безкоштовна година почнеться.""",
    },

    # ======================= DEUTSCH =======================
    "de": {
        "start_subscribed": "✅ Zugang bestätigt.\nStell deine Frage.",
        "start": """👋 <b>Hallo! Ich bin dein KI-Assistent für Psychosomatik.</b>

Schreib mir, was dich beschäftigt: ein Symptom, ein Gefühl oder eine Situation, und ich helfe dir, die psychologischen Ursachen zu verstehen.

🎁 Du hast <b>{limit} kostenlose Fragen</b>.

Du möchtest mehr? Du kannst dem geschlossenen Club <b>„Центр управления здоровьем“ (Zentrum für Gesundheitsmanagement)</b> sofort beitreten:
🤖 unbegrenzter KI-Assistent
🎥 geschlossene Live-Streams mit Analysen
📚 Materialien und 🧘 Praxisübungen

<b>Die erste Stunde im Club ist kostenlos.</b> Du musst nur eine Karte hinterlegen. Kündigst du innerhalb der Stunde, wird nichts abgebucht. Bleibst du, verlängert sich das Abo automatisch (erster Monat 9 €, danach 11 €/Monat, oder 120 € pro Jahr).

ℹ️ Die Streams und Materialien sind derzeit auf Russisch.

👇 Stell deine erste Frage oder tippe auf den Button, um dem Club jetzt beizutreten.""",
        "reminder": "💡 Du hast noch 1 kostenlose Frage. Stell die, die dir gerade am wichtigsten ist. Wenn sie aufgebraucht ist, kannst du den Club öffnen: Die erste Stunde ist kostenlos.",
        "error": "Im Moment gibt es viele Anfragen, und ich konnte nicht antworten. Bitte versuche es in einer Minute noch einmal.",
        "btn_join": "🎁 Club beitreten: 1. Stunde gratis",
        "btn_support": "💬 Zahlung klappt nicht? Schreib mir",
        "paywall": """🛑 <b>Deine 5 kostenlosen Fragen sind aufgebraucht</b>

Fünf Fragen hintereinander zeigen: Das Thema bewegt dich. Im Club kannst du viel tiefer gehen.

🎁 <b>Die erste Stunde im Club ist kostenlos</b>
Zum Aktivieren des Zugangs musst du eine Karte hinterlegen. Gefällt es dir nicht, kündige innerhalb der Stunde, dann wird nichts abgebucht. Gefällt es dir, bleib einfach dabei: Das Abo verlängert sich automatisch (erster Monat 9 €, danach 11 €/Monat, oder 120 € für ein Jahr). Du kannst jederzeit kündigen.

✨ <b>Das erwartet dich im Club</b>
🤖 Unbegrenzter KI-Assistent, rund um die Uhr
🎥 10 Aufzeichnungen geschlossener Live-Streams
📚 17 Materialien: Tabellen, Schemata, Checklisten
🧘 8 Praxisübungen
🩺 300+ Krankheitsbilder und ihre psychologischen Ursachen
ℹ️ Die Streams und Materialien sind derzeit auf Russisch.

🙋 <b>Zahlung klappt nicht?</b> Schreib mir: @divina_conscientia

👇 Tippe auf den Button, und deine Gratisstunde beginnt.""",
    },

    # ======================= ESPAÑOL =======================
    "es": {
        "start_subscribed": "✅ Acceso confirmado.\nHaz tu pregunta.",
        "start": """👋 <b>¡Hola! Soy tu asistente de IA de psicosomática.</b>

Cuéntame qué te preocupa: un síntoma, una emoción o una situación, y te ayudaré a entender sus causas psicológicas.

🎁 Tienes <b>{limit} preguntas gratis</b>.

¿Quieres más? Puedes unirte ahora mismo al club privado <b>«Центр управления здоровьем» (Centro de gestión de la salud)</b>:
🤖 asistente de IA ilimitado
🎥 directos privados con análisis
📚 materiales y 🧘 prácticas

<b>La primera hora en el club es gratis.</b> Solo tienes que vincular una tarjeta. Si cancelas dentro de la hora, no se cobra nada. Si te quedas, la suscripción se renueva automáticamente (primer mes 9 €, después 11 €/mes, o 120 € al año).

ℹ️ Los directos y los materiales están, por ahora, en ruso.

👇 Haz tu primera pregunta o pulsa el botón para unirte al club ahora.""",
        "reminder": "💡 Te queda 1 pregunta gratis. Haz la que más te importe. Cuando se acabe, podrás abrir el club: la primera hora es gratis.",
        "error": "Ahora mismo hay muchas consultas y no he podido responder. Inténtalo de nuevo en un minuto.",
        "btn_join": "🎁 Unirme al club: 1.ª hora gratis",
        "btn_support": "💬 ¿No puedes pagar? Escríbeme",
        "paywall": """🛑 <b>Tus 5 preguntas gratis se han terminado</b>

Cinco preguntas seguidas demuestran que este tema te importa. En el club puedes profundizar mucho más.

🎁 <b>La primera hora en el club es gratis</b>
Para activar el acceso solo tienes que vincular una tarjeta. Si no te gusta, cancela dentro de la hora y no se cobrará nada. Si te gusta, simplemente quédate: la suscripción se renueva automáticamente (primer mes 9 €, después 11 €/mes, o 120 € al año). Puedes cancelar en cualquier momento.

✨ <b>Qué hay dentro del club</b>
🤖 Asistente de IA ilimitado, 24/7
🎥 10 grabaciones de directos privados
📚 17 materiales: tablas, esquemas y listas de verificación
🧘 8 prácticas
🩺 Más de 300 afecciones y sus causas psicológicas
ℹ️ Los directos y los materiales están, por ahora, en ruso.

🙋 <b>¿No puedes pagar?</b> Escríbeme: @divina_conscientia

👇 Pulsa el botón y empieza tu hora gratis.""",
    },

    # ======================= FRANÇAIS =======================
    "fr": {
        "start_subscribed": "✅ Accès confirmé.\nPose ta question.",
        "start": """👋 <b>Bonjour ! Je suis ton assistant IA en psychosomatique.</b>

Dis-moi ce qui te préoccupe : un symptôme, une émotion ou une situation, et je t'aiderai à comprendre ses causes psychologiques.

🎁 Tu as <b>{limit} questions gratuites</b>.

Tu veux aller plus loin ? Tu peux rejoindre tout de suite le club privé <b>«Центр управления здоровьем» (Centre de gestion de la santé)</b> :
🤖 assistant IA illimité
🎥 lives privés avec analyses
📚 ressources et 🧘 pratiques

<b>La première heure dans le club est gratuite.</b> Il suffit d'enregistrer une carte. Si tu annules dans l'heure, rien n'est débité. Si tu restes, l'abonnement se renouvelle automatiquement (9 € le premier mois, puis 11 €/mois, ou 120 € par an).

ℹ️ Les lives et les ressources sont pour l'instant en russe.

👇 Pose ta première question ou appuie sur le bouton pour rejoindre le club maintenant.""",
        "reminder": "💡 Il te reste 1 question gratuite. Pose celle qui compte le plus pour toi. Quand elle sera utilisée, tu pourras ouvrir le club : la première heure est offerte.",
        "error": "Il y a beaucoup de demandes en ce moment et je n'ai pas pu répondre. Réessaie dans une minute.",
        "btn_join": "🎁 Rejoindre le club : 1re heure offerte",
        "btn_support": "💬 Paiement impossible ? Écris-moi",
        "paywall": """🛑 <b>Tes 5 questions gratuites sont terminées</b>

Cinq questions d'affilée montrent que ce sujet compte pour toi. Dans le club, tu peux aller beaucoup plus loin.

🎁 <b>La première heure dans le club est gratuite</b>
Il suffit d'enregistrer une carte pour activer l'accès. Si ça ne te plaît pas, annule dans l'heure et rien ne sera débité. Si ça te plaît, reste simplement : l'abonnement se renouvelle automatiquement (9 € le premier mois, puis 11 €/mois, ou 120 € par an). Tu peux annuler à tout moment.

✨ <b>Ce que contient le club</b>
🤖 Assistant IA illimité, 24h/24
🎥 10 enregistrements de lives privés
📚 17 ressources : tableaux, schémas, check-lists
🧘 8 pratiques
🩺 Plus de 300 pathologies et leurs causes psychologiques
ℹ️ Les lives et les ressources sont pour l'instant en russe.

🙋 <b>Paiement impossible ?</b> Écris-moi : @divina_conscientia

👇 Appuie sur le bouton pour commencer ton heure gratuite.""",
    },

    # ======================= ITALIANO =======================
    "it": {
        "start_subscribed": "✅ Accesso confermato.\nFai la tua domanda.",
        "start": """👋 <b>Ciao! Sono il tuo assistente IA di psicosomatica.</b>

Scrivimi cosa ti preoccupa: un sintomo, un'emozione o una situazione, e ti aiuterò a capirne le cause psicologiche.

🎁 Hai <b>{limit} domande gratuite</b>.

Vuoi di più? Puoi entrare subito nel club riservato <b>«Центр управления здоровьем» (Centro di gestione della salute)</b>:
🤖 assistente IA illimitato
🎥 dirette riservate con analisi
📚 materiali e 🧘 pratiche

<b>La prima ora nel club è gratuita.</b> Basta collegare una carta. Se annulli entro l'ora, non viene addebitato nulla. Se resti, l'abbonamento si rinnova automaticamente (primo mese 9 €, poi 11 €/mese, oppure 120 € all'anno).

ℹ️ Le dirette e i materiali sono per ora in russo.

👇 Fai la tua prima domanda o tocca il pulsante per entrare subito nel club.""",
        "reminder": "💡 Ti resta 1 domanda gratuita. Fai quella che ti sta più a cuore. Quando sarà finita, potrai aprire il club: la prima ora è gratis.",
        "error": "In questo momento ci sono molte richieste e non è stato possibile rispondere. Riprova tra un minuto.",
        "btn_join": "🎁 Entra nel club: 1ª ora gratis",
        "btn_support": "💬 Non riesci a pagare? Scrivimi",
        "paywall": """🛑 <b>Le tue 5 domande gratuite sono finite</b>

Cinque domande di fila dimostrano che questo tema ti sta a cuore. Nel club puoi andare molto più a fondo.

🎁 <b>La prima ora nel club è gratuita</b>
Per attivare l'accesso basta collegare una carta. Se non ti piace, annulla entro l'ora e non verrà addebitato nulla. Se ti piace, resta semplicemente: l'abbonamento si rinnova automaticamente (primo mese 9 €, poi 11 €/mese, oppure 120 € all'anno). Puoi annullare in qualsiasi momento.

✨ <b>Cosa c'è nel club</b>
🤖 Assistente IA illimitato, 24 ore su 24
🎥 10 registrazioni di dirette riservate
📚 17 materiali: tabelle, schemi e checklist
🧘 8 pratiche
🩺 Oltre 300 patologie e le loro cause psicologiche
ℹ️ Le dirette e i materiali sono per ora in russo.

🙋 <b>Non riesci a pagare?</b> Scrivimi: @divina_conscientia

👇 Tocca il pulsante e la tua ora gratuita inizia.""",
    },

    # ======================= POLSKI =======================
    "pl": {
        "start_subscribed": "✅ Dostęp potwierdzony.\nZadaj swoje pytanie.",
        "start": """👋 <b>Cześć! Jestem Twoim asystentem AI od psychosomatyki.</b>

Napisz, co Cię martwi: objaw, emocję lub sytuację, a pomogę Ci zrozumieć psychologiczne przyczyny.

🎁 Masz <b>{limit} darmowych pytań</b>.

Chcesz więcej? Możesz od razu dołączyć do zamkniętego klubu <b>«Центр управления здоровьем» (Centrum zarządzania zdrowiem)</b>:
🤖 nielimitowany asystent AI
🎥 zamknięte transmisje z omówieniami
📚 materiały i 🧘 praktyki

<b>Pierwsza godzina w klubie jest darmowa.</b> Wystarczy dodać kartę. Jeśli anulujesz w ciągu godziny, nic nie zostanie pobrane. Jeśli zostaniesz, subskrypcja odnowi się automatycznie (pierwszy miesiąc 9 €, potem 11 €/mies., albo 120 € za rok).

ℹ️ Transmisje i materiały są na razie po rosyjsku.

👇 Zadaj pierwsze pytanie albo kliknij przycisk, aby dołączyć do klubu teraz.""",
        "reminder": "💡 Zostało Ci 1 darmowe pytanie. Zadaj to, które jest dla Ciebie najważniejsze. Gdy się skończy, możesz otworzyć klub: pierwsza godzina jest darmowa.",
        "error": "Teraz jest dużo zapytań i nie udało mi się odpowiedzieć. Spróbuj ponownie za minutę.",
        "btn_join": "🎁 Dołącz do klubu: 1. godzina gratis",
        "btn_support": "💬 Nie możesz zapłacić? Napisz do mnie",
        "paywall": """🛑 <b>Twoje 5 darmowych pytań dobiegło końca</b>

Pięć pytań z rzędu pokazuje, że ten temat jest dla Ciebie ważny. W klubie możesz zajść znacznie głębiej.

🎁 <b>Pierwsza godzina w klubie jest darmowa</b>
Aby aktywować dostęp, wystarczy dodać kartę. Jeśli Ci się nie spodoba, anuluj w ciągu godziny, a nic nie zostanie pobrane. Jeśli się spodoba, po prostu zostań: subskrypcja odnowi się automatycznie (pierwszy miesiąc 9 €, potem 11 €/mies., albo 120 € za rok). Możesz zrezygnować w każdej chwili.

✨ <b>Co jest w klubie</b>
🤖 Nielimitowany asystent AI, całą dobę
🎥 10 nagrań zamkniętych transmisji
📚 17 materiałów: tabele, schematy i checklisty
🧘 8 praktyk
🩺 Ponad 300 schorzeń i ich psychologiczne przyczyny
ℹ️ Transmisje i materiały są na razie po rosyjsku.

🙋 <b>Nie możesz zapłacić?</b> Napisz do mnie: @divina_conscientia

👇 Kliknij przycisk, a Twoja darmowa godzina się zacznie.""",
    },
}
