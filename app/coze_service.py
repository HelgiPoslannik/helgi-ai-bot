def ask_coze(user_id: str, message: str):
    headers = {
        "Authorization": f"Bearer {COZE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "bot_id": COZE_BOT_ID,
        "user_id": str(user_id),
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
    try:
        response = requests.post(
            COZE_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        data = response.json()
        logger.info(f"Coze RAW response: {data}")

        if data.get("code") != 0:
            return "Ошибка Coze"

        chat_id = data["data"]["id"]
        conversation_id = data["data"]["conversation_id"]

        # ждём завершения генерации
        for _ in range(15):
            time.sleep(2)
            retrieve = requests.get(
                COZE_RETRIEVE_URL,
                headers=headers,
                params={"conversation_id": conversation_id, "chat_id": chat_id}
            )
            retrieve_data = retrieve.json()
            logger.info(f"Coze retrieve: {retrieve_data}")

            status = retrieve_data.get("data", {}).get("status")
            if status == "completed":
                break
            if status in ("failed", "requires_action"):
                logger.error(f"Coze chat ended with status={status}")
                return "Ошибка Coze."

        # ВАЖНО: правильный эндпоинт + обязательный chat_id
        messages = requests.get(
            "https://api.coze.com/v3/chat/message/list",
            headers=headers,
            params={"conversation_id": conversation_id, "chat_id": chat_id}
        )
        messages_data = messages.json()
        logger.info(f"Coze messages: {messages_data}")

        # ВАЖНО: фильтруем именно по type == "answer", а не по role
        answer_parts = [
            item.get("content", "")
            for item in messages_data.get("data", [])
            if item.get("type") == "answer"
        ]

        if answer_parts:
            # Coze отдаёт от новых к старым (desc) — переворачиваем в хронологический порядок
            return "".join(reversed(answer_parts))

        return "Ответ не получен."

    except Exception as error:
        logger.error(f"Coze error: {error}")
        return "Ошибка Coze."
