from utils import pybitClass as pc
import time
import asyncio
from datetime import datetime as dt
import utils.tele as tg
from tabulate import tabulate
from utils import indicators as idt
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

cl = pc.BybitAPI()

# 종목 서칭
def strategy(ticker):
    df = cl.klines(ticker,'D',100)
    o, h, l, c, v, ch = df.open, df.high, df.low, df.close, df.volume, df.change
    bb20 = idt.Bollinger_Band(df,20)['upper']
    case = (
        (ch.iloc[-1]>1) and (c.iloc[-1]>bb20.iloc[-1])
    and (sum(c.iloc[-6:-1]>bb20.iloc[-6:-1])==0)
    and (sum(o.iloc[-6:-1]>bb20.iloc[-6:-1])==0)
    )
    return {'case':case, '매수가':c.iloc[-1], '등락율':ch.iloc[-1],'매수시점':df.date[-1], '1차 스위칭':o.iloc[-1], }

# 종목 거름망
def search():
    tickers = cl.all_tickers()
    tickers = tickers[tickers["turnover24h"] > 4e+06].reset_index(drop = True).drop_duplicates()
    targets = []
    for idx, i in enumerate(tickers['symbol']):
        # print(idx,i)
        dict = strategy(i)
        if dict['case']:
            targets.append({'종목':i, '매수가':dict['매수가'], '등락율':dict['등락율']})
    return pd.DataFrame(targets)

# 포지션 현황
def position():
    cl.position_info()

#
def trading():
    asyncio.run(tg.tele_bot('시작합니다.'))
    # print('시작')
    while 1:
        now = dt.now()
        # 포지션이 없고 08시 59분이면 매수할 종목 서칭
        if ((now.minute+1)%15==0) and now.second>=30 and cl.position_info().empty:
            # start = time.time()
            targets = search()
            # end = time.time()
            # print(f'경과 시간:{end - start:.5f} sec')
            # 타겟이 있으면 타겟이름을 버튼으로 만들어서 매수 진행
            if not targets.empty:
                keyboard = []
                for i in targets['종목']:
                    keyboard.append([InlineKeyboardButton(i, callback_data=
                                                {
                                                    'action':'buy',
                                                    'ticker':i,
                                                    'lastPrice':targets[targets['종목']==i]['매수가'],
                                                }
                                            )
                                        ]
                                    )
                keyboard.append([InlineKeyboardButton("취소", callback_data={'action':'cancel'})])
                reply_markup = InlineKeyboardMarkup(keyboard)
                asyncio.run(tg.tele_bot('매수할 종목을 선택하세요.', reply_markup))

        # 08시 58분에 포지션이 있으면 손익 확인하고 스위칭 or 익절 or 패스
        if ((now.minute+1)%15==0) and (not cl.position_info().empty):
            # 포지션 손익 확인
            posi = cl.position_info()
            entry = float(posi["avgPrice"][0])
            mark = float(posi["markPrice"][0])
            leverage = float(posi["leverage"][0])
            posi["pnl"] = round((((mark - entry) / mark) * 100 * leverage), 2)
            posi.loc[posi["side"] == "Sell", "pnl"] = -posi.loc[posi["side"] == "Sell", "pnl"]
            posi = posi[["symbol", "pnl"]]
            asset = cl.wallet()
            posi = posi.join(asset)
            # 익절할만한 퍼센트면 자동익절 하고 익절 완료 메세지
            if posi.pnl[-1]>10:
                # 익절 매커니즘
            # 손실이거나 익절가까지 안왔으면 현재 손익율 알림 메세지
            else:
                # 스위칭1(매수시점의 시가를 깼을때)

                # 스위칭2(bb20선 아래로 내려온 음봉보다 더 아래로 내려간 음봉이 발생 할 때)

                # 패스

            # 청산가에 매도 가능한지 확인하고 안되면 청산방지 주문 다시하기
            time.sleep(60)
        time.sleep(1)
