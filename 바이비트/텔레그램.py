import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime as dt
import pybitClass as pc
import indicators as idt
import pandas as pd
from tabulate import tabulate
# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# # set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)

# logger = logging.getLogger(__name__)

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     await update.message.reply_html(
#         rf"Hi {user.mention_html()}!",
#         reply_markup=ForceReply(selective=True),
#     )

async def targets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    cl = pc.BybitAPI()
    tickers = cl.all_tickers()
    # list(tickers['symbol'])
    targets = []
    for idx, i in enumerate(list(tickers['symbol'])):
        df = cl.klines(i,'D',60)
        o, h, l, c, v, ch = df.open, df.high, df.low, df.close, df.volume, df.change
        bb20 = idt.Bollinger_Band(df,20)
        l_case = ((sum(c.iloc[-6:-2]>bb20['upper'].iloc[-6:-2])==0)
        and (sum(o.iloc[-6:-2]>bb20['upper'].iloc[-6:-2])==0)
        and (sum(o.iloc[-6:-2]<bb20['lower'].iloc[-6:-2])==0)
        and (sum(c.iloc[-6:-2]<bb20['lower'].iloc[-6:-2])==0)
        and (c.iloc[-2]>bb20['upper'].iloc[-2])
        and (ch.iloc[-2]>3))
        if l_case:
            targets.append({'ticker':i})
    targets = pd.DataFrame(targets)
    await update.message.reply_text(f"""<pre><code class="language-python">{tabulate(
                        targets,
                        headers="firstrow",
                        tablefmt="plain",
                        showindex=True,
                        numalign="left",
                        stralign="left",
                        )}</code></pre>""")


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Echo the user message."""
#     await update.message.reply_text(update.message.text)

def main() -> None:
    # token
    with open('/home/joon/바탕화면/coin/바이비트/알트토큰.txt') as f:
        lines = f.readlines()
        token = lines[0].strip()
        id = lines[1].strip()

    application = Application.builder().token(token).build()

    # application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("targets", targets))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
