import os
import asyncio
from fastapi import FastAPI
import uvicorn
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Переменные окружения ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# --- Статус заявок ---
tickets = {}
ticket_counter = 1

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши описание своей проблемы. Можно с фото."
    )

# --- Обработка сообщений и фото ---
async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ticket_counter
    ticket_id = ticket_counter
    ticket_counter += 1

    status = "Новая"
    tickets[ticket_id] = {"user": update.message.from_user.full_name, "status": status}

    text = f"🆕 Заявка #{ticket_id} от {update.message.from_user.full_name}\nСтатус: {status}\n"
    if update.message.text:
        text += f"Описание: {update.message.text}"
        await context.bot.send_message(chat_id=CHAT_ID, text=text)
    elif update.message.photo:
        photo_id = update.message.photo[-1].file_id
        caption = f"{text}\nФото-заявка"
        await context.bot.send_photo(chat_id=CHAT_ID, photo=photo_id, caption=caption)

    # Кнопки для пользователя
    keyboard = [
        [InlineKeyboardButton("Проверить статус заявки", callback_data=f"status_{ticket_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Заявка отправлена! Можно проверить статус ниже:", reply_markup=reply_markup)

# --- Обработка кнопок ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("status_"):
        ticket_id = int(data.split("_")[1])
        ticket = tickets.get(ticket_id)
        if ticket:
            await query.edit_message_text(f"Заявка #{ticket_id} от {ticket['user']}\nСтатус: {ticket['status']}")
        else:
            await query.edit_message_text("Заявка не найдена.")

# --- FastAPI для обхода Render in progress ---
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

# --- Запуск бота ---
async def start_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, relay))
    application.add_handler(CallbackQueryHandler(button))
    await application.run_polling()

# --- Главная функция ---
if __name__ == "__main__":
    # Запускаем FastAPI и бота одновременно
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
