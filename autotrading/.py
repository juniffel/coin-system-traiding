import utils.tele as tg
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
# 버튼 생성
keyboard = [
    [InlineKeyboardButton("btc등락율", callback_data='button1')],
    [InlineKeyboardButton("버튼 2", callback_data='button2')],
]
reply_markup = InlineKeyboardMarkup(keyboard)
asyncio.run(tg.tele_bot('버튼을 클릭해주세요.', reply_markup))
