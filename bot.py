import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Токен и ID чата
TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# Хранилище заявок
tickets = {}
ticket_counter = 1

# Команда /start для пользователя
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ПО", callback_data="type_software")],
        [InlineKeyboardButton("Оборудование", callback_data="type_hardware")],
        [InlineKeyboardButton("Сеть", callback_data="type_network")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выбери тип проблемы:", reply_markup=reply_markup)

# Выбор типа проблемы
async def type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['type'] = query.data.split('_')[1]  # сохраняем выбор
    await query.edit_message_text(text=f"Ты выбрал {context.user_data['type']}. Теперь опиши проблему.")

# Обработка сообщений и фото
async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ticket_counter
    user_type = context.user_data.get('type', 'Не указан')
    ticket_id = ticket_counter
    ticket_counter += 1

    ticket = {
        "user": update.message.from_user.full_name,
        "text": update.message.text or "",
        "photo": update.message.photo[-1].file_id if update.message.photo else None,
        "status": "Новая",
        "type": user_type
    }
    tickets[ticket_id] = ticket

    keyboard = [
        [
            InlineKeyboardButton("В работе", callback_data=f"status_{ticket_id}_in_progress"),
            InlineKeyboardButton("Исполнена", callback_data=f"status_{ticket_id}_done")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = f"🆕 Заявка #{ticket_id}\nТип: {ticket['type']}\nСтатус: {ticket['status']}\nОт: {ticket['user']}\nОписание: {ticket['text']}"

    if ticket['photo']:
        await context.bot.send_photo(chat_id=CHAT_ID, photo=ticket['photo'], caption=msg, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=CHAT_ID, text=msg, reply_markup=reply_markup)

    await update.message.reply_text(f"Заявка #{ticket_id} отправлена! Статус: {ticket['status']}")

# Смена статуса заявки
async def status_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    ticket_id = int(data[1])
    new_status = "В работе" if data[2] == "in" else "Исполнена"

    if ticket_id in tickets:
        tickets[ticket_id]['status'] = new_status
        ticket = tickets[ticket_id]
        msg = f"📝 Заявка #{ticket_id}\nТип: {ticket['type']}\nСтатус: {ticket['status']}\nОт: {ticket['user']}\nОписание: {ticket['text']}"
        await query.edit_message_text(text=msg)
    else:
        await query.edit_message_text("Заявка не найдена.")

# Главная функция
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(type_choice, pattern="^type_"))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, relay))
    app.add_handler(CallbackQueryHandler(status_change, pattern="^status_"))

    # Запуск как воркер — long polling
    print("Бот запущен как Render worker...")
    app.run_polling()

if __name__ == "__main__":
    main()
