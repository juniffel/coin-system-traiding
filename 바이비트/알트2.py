import warnings

warnings.filterwarnings("ignore")
from datetime import datetime as dt
import time as t
import sys
import tele as tg
import pandas as pd
import pybitClass as pc
import indicators as idt
from tabulate import tabulate
import traceback
import asyncio

cl = pc.BybitAPI()

# 종목 선별
def searcher():
    # return pd.concat(c.all_tickers()['symbol'][:10],c.all_tickers()['symbol'][:10])
    tickers =  cl.all_tickers()
    # return tickers
    tickers = tickers[tickers['turnover24h']>1e+07]
    return pd.concat([tickers[:70],tickers[-70:]])

# 전략
def strategy(df, interval):
    o, h, l, c, v = df.open, df.high, df.low, df.close, df.volume
    ch = round(((c / o) - 1) * 100, 3)
    # bb60 = idt.Bollinger_Band(df,60,2.0)
    # bb60_2 = idt.Bollinger_Band(df,60,2.2)
    # ma10 = idt.ma(df,10)

    l_case = (
		(h.iloc[-1]<max(h.iloc[-6:-1]))
	and (c.iloc[-1]<max(c.iloc[-6:-1]))
	and (10>=ch.iloc[-1]>=2)
    and (ch.iloc[-2]<0)
    and (ch.iloc[-3]<0)
    and (c.iloc[-1]>o.iloc[-2])
    and (h.iloc[-1]>h.iloc[-2])
    )

    return l_case,ch.iloc[-1]

# 전략 알림?
def strategy_alert(tickers, interval):
    targets = []
    # start = t.time()
    for idx, i in enumerate(tickers):
        df = cl.klines(i, interval, 70)
        # print(i)
        if len(df) >= 70:
            case = strategy(df, interval)
            if case[0]:
                target = {"종목": i, '%':f'{round(case[1])}%'}
                targets.append(target)

    # end = t.time()
    # print(f"{end - start:.5f} sec")

    return pd.DataFrame(targets)

# 마진타입 레버리지 세팅
def set_margin_leverage(targets, leverage):
        for i in targets.종목:
            cl.set_marginType(i, 1, leverage)
            cl.set_leverage(i,leverage)

def positions():
    posi = cl.position_info(settleCoin = 'USDT')
    if not posi.empty:
        entry = float(posi['avgPrice'][0])
        mark = float(posi['markPrice'][0])
        leverage = float( posi['leverage'][0])
        posi['pnl'] = round((((mark-entry)/mark)*100*leverage),2)
        posi.loc[posi['side']=='Sell','pnl'] = -posi.loc[posi['side']=='Sell','pnl']
        posi = posi[['symbol','pnl']]
        asset = cl.wallet()
        posi = posi.join(asset)
        return posi.transpose()
    return pd.DataFrame()
# 메인함수
def main():
    try:
        asyncio.run(tg.tele_bot('시작'))
        tickersReset = 0
        positionReset = 0
        tickers = pd.DataFrame()
        targets = pd.DataFrame()
        while 1:
            now  = dt.now()
            # 한 시간 단위로 순위, 포지션 재 탐색 시그널
            if 56>now.minute>=55:
                tickersReset = 0
                positionReset = 0
                t.sleep(60)
            # 종목 탐색
            if (now.minute>=58) and (tickersReset==0):
                tickers = searcher()
                # tickers = pd.concat([tickers[:10],tickers[-10:]])
                tickersReset=1
                t.sleep(1)
            # 포지션 확인
            if (now.minute>=58) and (positionReset==0):
                position = positions()
                if not position.empty:
                    asyncio.run(tg.tele_bot(f'''<pre><code class="language-python">{tabulate(
                        position,
                        headers="firstrow",
                        tablefmt="plain",
                        showindex=True,
                        numalign="left",
                        stralign="left",
                        )}</code></pre>'''
                    ))
                positionReset=1
                t.sleep(1)
            # 전략 탐색
            if (now.minute>=59) and (not tickers.empty):
                targets = pd.concat(
                    [targets, strategy_alert(list(tickers["symbol"]), '60')],
                    ignore_index=True,
                )
            # 타겟 알림
            if not targets.empty:
                set_margin_leverage(targets,4)# 마진타입, 레버리지 세팅
                targets['종목'] = targets.종목.str.replace('USDT','')
                targets = targets
                asyncio.run(tg.tele_bot(f'''<pre><code class="language-python">{tabulate(
                    targets,
                    headers="firstrow",
                    tablefmt="plain",
                    showindex=True,
                    numalign="left",
                    stralign="left",
                    )}</code></pre>'''
                ))
                targets = pd.DataFrame()# 타겟 초기화

            if targets.empty:
                t.sleep(60)
            t.sleep(1)

    except Exception as e:
        err_msg = traceback.format_exc()
        # print(err_msg)
        asyncio.run(tg.tele_bot(f'<pre><code class="language-python">에러 발생:{err_msg}</code></pre>'))
        main()

if __name__ == "__main__":
    main()
