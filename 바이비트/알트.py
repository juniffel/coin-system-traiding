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
    return tickers[tickers['turnover24h']>4e+06].reset_index(drop = True)[:150]

# 전략
def strategy(df, interval):
    o, h, l, c, v = df.open, df.high, df.low, df.close, df.volume
    ch = round(((c / o) - 1) * 100, 3)
    bb60 = idt.Bollinger_Band(df,60)

    l_case = (
		(h.iloc[-2]<bb60.upper.iloc[-2]) 
	and (c.iloc[-1]>bb60.upper.iloc[-1]) 
	and (ch.iloc[-1]>1)
	)
    s_case = (
		(l.iloc[-2]>bb60.lower.iloc[-2]) 
	and (c.iloc[-1]<bb60.lower.iloc[-1]) 
	and (ch.iloc[-1]<-1)
	)
    return l_case,s_case

# 전략 알림?
def strategy_alert(tickers, interval):
    targets = []
    start = t.time()
    for idx, i in enumerate(tickers):
        df = cl.klines(i, interval, 70)
        # print(i)
        if len(df) >= 70:
            case = strategy(df, interval)
            if case[0]:
                target = {"종목": i, "순위": f'{idx + 1}위', '단위':interval, '전략':'롱'}
                targets.append(target)
            if case[1]:
                target = {"종목": i, "순위": f'{idx + 1}위', '단위':interval, '전략':'숏'}
                targets.append(target)
    end = t.time()
    print(f"{end - start:.5f} sec")
    
    return pd.DataFrame(targets)

# 마진타입 레버리지 세팅
def set_margin_leverage(targets, leverage):
        for i in targets.종목:
            cl.set_marginType(i, 1, leverage)
            cl.set_leverage(i,leverage)
            
def positions():
    posi = cl.position_info(settleCoin = 'USDT')
    entry = float(posi['avgPrice'][0])
    mark = float(posi['markPrice'][0])
    leverage = float( posi['leverage'][0])
    side =  1 if posi['side'][0] =='Buy' else -1 
    if side=='Buy':
        posi['pnl'] = round((((mark-entry)/mark)*100*leverage),2)
    elif side=='Sell':
        posi['pnl'] = -round((((mark-entry)/mark)*100*leverage),2)
    return posi[['symbol','pnl']].transpose()
# 메인함수
def main():
    try:
        asyncio.run(tg.tele_bot('시작'))
        tickersReset = 0
        positionReset = 0
        targets = pd.DataFrame()
        while 1:
            now  = dt.now()
            # 한 시간 단위로 순위, 포지션 재 탐색 시그널
            if 56>now.minute>=55:
                tickersReset = 0
                positionReset = 0
                t.sleep(60)
            if (now.minute>=58) and (tickersReset==0):
                tickers = cl.all_tickers()
                tickers = pd.concat([tickers[:10],tickers[-10:]]) 
                print('선정된 종목')
                print('-'*50)
                print(tickers[['symbol',  'price24hPcnt', 'turnover24h', 'volume24h', ]])  
                print('-'*50) 
                tickersReset=1       
                t.sleep(1)
                
            if (now.minute>=58) and (positionReset==0):
                position = positions()
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
                
            if (now.minute>=59) and (not tickers.empty):
                targets = pd.concat(
                    [targets, strategy_alert(list(tickers["symbol"]), 60)],
                    ignore_index=True,
                )
            
            if not targets.empty:
                set_margin_leverage(targets,10)# 마진타입, 레버리지 세팅
                targets['종목'] = targets.종목.str.replace('USDT','')
                targets = targets.transpose()
                asyncio.run(tg.tele_bot(f'''<pre><code class="language-python">{tabulate(
                    targets,
                    headers="firstrow",
                    tablefmt="plain",
                    showindex=True,
                    numalign="left",
                    stralign="left",
                    )}</code></pre>'''
                ))
                targets = pd.DataFrame()
                
            if targets.empty:
                t.sleep(60)# 타겟 초기화
            t.sleep(1)
            
    except Exception as e:
        err_msg = traceback.format_exc()
        # print(err_msg)
        asyncio.run(tg.tele_bot(f'<pre><code class="language-python">에러 발생:{err_msg}</code></pre>'))
        main()

if __name__ == "__main__":
    main()
