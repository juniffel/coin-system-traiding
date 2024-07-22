
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("포지션 정보", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [
            InlineKeyboardButton("Option 5", callback_data="5"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # print(type(query.data))
    if query.data == '1':
        await query.edit_message_text(text=f"포지션정보는...")
    await query.answer()


def main() -> None:
    # token
    with open('/home/joon/바탕화면/coin/바이비트/알트토큰.txt') as f:
        lines = f.readlines()
        token = lines[0].strip()
        id = lines[1].strip()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
