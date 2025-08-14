import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Переменные окружения
TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши описание проблемы, можно с фото.")

# Обработка сообщений и фото
async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"🆕 Заявка от {update.message.from_user.full_name}:\n{update.message.text}"
        )
    elif update.message.photo:
        photo_id = update.message.photo[-1].file_id
        caption = f"🆕 Фото-заявка от {update.message.from_user.full_name}"
        await context.bot.send_photo(chat_id=CHAT_ID, photo=photo_id, caption=caption)
    await update.message.reply_text("Заявка отправлена в ИТ-чат!")

# Основная функция
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, relay))

    app.run_polling()

if __name__ == "__main__":
    main()
