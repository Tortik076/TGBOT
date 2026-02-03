import os

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    ChatJoinRequestHandler,
    CallbackQueryHandler
)

# ================== НАСТРОЙКИ ==================

TOKEN = os.environ.get("API_TOKEN")


# Хранилище заявок:
# user_id -> chat_id
pending_requests = {}

# ================== ЛОГИ ==================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== ХЕНДЛЕРЫ ==================

# 1️⃣ Пользователь подал заявку в канал
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_request = update.chat_join_request
    user = join_request.from_user
    chat = join_request.chat

    # сохраняем, в какой канал подана заявка
    pending_requests[user.id] = chat.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤷‍♂️ Я человек", callback_data="human_check")]
    ])
    user_name = user.first_name or "Друг"

    await context.bot.send_message(
        chat_id=user.id,
        text=(
			f"{user_name}, спасибо за подписку на канал магазина ne:BRAND!\n\n"
            "Я анти-спам бот.\n\n"
            "Для подтверждения того, что вы живой человек, нажмите кнопку ниже:\n"
            "«Я человек»"
        ),
        reply_markup=keyboard
    )

    logging.info(f"Заявка от {user.id} ({user_name}) в канал {chat.id}")
    
# 2️⃣ Пользователь нажал кнопку
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    await query.answer()

    chat_id = pending_requests.get(user.id)

    if not chat_id:
        await query.edit_message_text(
            "❌ Заявка не найдена или уже обработана."
        )
        logging.warning(f"Заявка не найдена для пользователя {user.id}")
        return

    try:
        await context.bot.approve_chat_join_request(
            chat_id=chat_id,
            user_id=user.id
        )

        await query.edit_message_text(
            "✅ Спасибо! Заявка одобрена, добро пожаловать в магазин ne:BRAND!"
        )

        logging.info(f"Пользователь {user.id} одобрен в канал {chat_id}")

    except Exception as e:
        await query.edit_message_text(
            "⚠️ Ошибка при одобрении заявки. Попробуйте позже."
        )
        logging.error(f"Ошибка одобрения: {e}")

    finally:
        # очищаем память
        pending_requests.pop(user.id, None)

# ================== ЗАПУСК ==================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Бот запущен и ждёт заявок...")
    app.run_polling()

if __name__ == "__main__":
    main()





