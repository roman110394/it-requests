import os
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

def start(update, context):
    update.message.reply_text("Привет! Напиши описание проблемы, можно с фото.")

def relay(update, context):
    if update.message.text:
        context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"🆕 Заявка от {update.message.from_user.full_name}:\n{update.message.text}"
        )
    elif update.message.photo:
        photo_id = update.message.photo[-1].file_id
        caption = f"🆕 Фото-заявка от {update.message.from_user.full_name}"
        context.bot.send_photo(chat_id=CHAT_ID, photo=photo_id, caption=caption)
    update.message.reply_text("Заявка отправлена в ИТ-чат!")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo, relay))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
