'''
08:50에 종목선별 -> 59분에 타겟 서치 -> 타겟 알림 -> 매수 원하는 종목 전달 -> 지정가로 종가에 매수
-> 매수 되면 알림(하루동안 주문 안되면 주문취소 처리)-> 2음봉뜨면 스위칭 or 3배기준 3% 이상이면 익절

'''
import datetime
import pybitClass
import time
import indicators as idt
import pandas as pd
import asyncio
import tele as tg
from tabulate import tabulate
import traceback
import ntp
import warnings
warnings.filterwarnings("ignore")

cl = pybitClass.BybitAPI()

# 종목 선별
def select_tickers():
    df = cl.all_tickers()
    return df[df['change']>3].sort_values('turnover24h', ascending=False).reset_index(drop = True)[:100]

# 타겟 선별
def select_targets(tickers):
    targets = []
    for idx, i in enumerate(tickers):
        print(f'target함수 for문 확인용 : {idx,i}')
        df  = cl.klines(i, 'D', 100)
        o,h,l,c,v,ch = df,open, df.high, df.low, df.close, df.volume, df.change
        bb20 = idt.Bollinger_Band(df,20,2)
        if (c.iloc[-6:-1]<bb20.iloc[-6:-1])and(o.iloc[-6:-1]<bb20.iloc[-6:-1])and((c.iloc[-1]>bb20.iloc[-1]))and(ch.iloc[-1]>3):
            targets.append({'종목':i, '등락율':f'{ch.iloc[-1]}%'})
    return pd.DataFrame(targets)

# 마진타입 레버리지 세팅
def set_margin_leverage(targets, leverage):
    for i in targets.종목:
        cl.set_marginType(i, 1, leverage)
        cl.set_leverage(i, leverage)

def main():
    asyncio.run(tg.tele_bot("시작"))
    while 1:
        now = datetime.datetime.now()

        if now.hour==8 and now.minute==50:
            ntp.ntp_sync()
            # 종목 선별
            tickers = select_tickers()
            time.sleep(60)

        if now.hour==8 and now.minute==59:
            # 타겟 선별
            targets = select_targets(tickers)
            # 마진타입, 레버리지 세팅
            if not targets.empty:
                set_margin_leverage(targets,3)
                targets["종목"] = targets.종목.str.replace("USDT", "")
                targets = targets
                asyncio.run(
                    tg.tele_bot(
                        f"""<pre><code class="language-python">{tabulate(
                        targets,
                        headers="firstrow",
                        tablefmt="plain",
                        showindex=True,
                        numalign="left",
                        stralign="left",
                        )}</code></pre>"""
                    )
                )
                targets = pd.DataFrame()  # 타겟 초기화
            time.sleep(60)
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        err_msg = traceback.format_exc()
        print(err_msg)
        asyncio.run(tg.tele_bot(f'<pre><code>에러 발생</code></pre>'))
        main()
