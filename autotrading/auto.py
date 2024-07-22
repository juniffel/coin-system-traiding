from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler # 콜백쿼리 핸들러 클래스 추가
import threading
import trade
from utils import pybitClass as pc
from utils import tele as tg
import asyncio
from tabulate import tabulate
from telegram.constants import ParseMode

cl = pc.BybitAPI()
# token
with open('/home/joon/바탕화면/coin/바이비트/알트토큰.txt') as f:
    lines = f.readlines()
    token = lines[0].strip()
    id = lines[1].strip()

# start 명령어 함수
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 버튼 생성
    keyboard = [
        [InlineKeyboardButton("btc등락율", callback_data='button1')],
        [InlineKeyboardButton("버튼 2", callback_data='button2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 채팅방으로 버튼 전송
    await update.message.reply_text("채팅방 입장을 환영합니다.\n버튼을 선택해 주세요.", reply_markup=reply_markup)


# 버튼 클릭 콜백 처리
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 콜백 정보 저장
    query = update.callback_query

    # 버튼 선택에 따른 기능 구현
    if query.data['action'] == 'buy':
        #매수 로직
        cl.order()
    if query.data['action'] == 'button1':
        try:
            tickers = cl.all_tickers()
            btc = tickers[tickers['symbol']=='BTCUSDT'][['symbol','price24hPcnt']]
            btc = btc.transpose()
            await query.edit_message_text(parse_mode = ParseMode.HTML,
                text = f"""<pre><code class="language-python">{
                tabulate(
                    btc,
                    headers="firstrow",
                    tablefmt="plain",
                    showindex=True,
                    numalign="left",
                    stralign="left",
                    )
                }</code></pre>"""
            )
        except:
            await query.edit_message_text(
                        text=f"""<pre><code class="language-python">
                        에러 발생
                        </code></pre>"""
                    )
    elif query.data == 'button2':
        await query.edit_message_text(text=f"버튼 2를 누름")
    else:
        await query.answer()

if __name__=='__main__':
    # 챗봇 application 인스턴스 생성
    application = ApplicationBuilder().token(token).build()

    # start 핸들러
    start_handler = CommandHandler('menu', start)

    # start 핸들러 추가
    application.add_handler(start_handler)

    # 콜백 핸들러 추가
    application.add_handler(CallbackQueryHandler(button_callback))

    # 스레드 생성
    t1 = threading.Thread(target=trade.trading)

    # 스레드 시작
    t1.start()
    print('시작')
    # 폴링 방식으로 실행
    application.run_polling()
