import warnings
warnings.filterwarnings("ignore")
import os
import pandas as pd
from pybit.unified_trading import HTTP, WebSocket
pd.set_option("display.max_columns", None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
########  Defines ###########################
testnet = False
###############################################
class BybitAPI:

    def __init__(self):
        with open('key.txt') as f:
            lines = f.readlines()
            api_key = lines[0].strip()
            secret = lines[1].strip()
        self.session = HTTP(testnet = testnet, api_key = api_key,api_secret = secret, logging_level = 10)
        
    def all_tickers(self,symbol=None):
        #종목들
        df = pd.DataFrame(self.session.get_tickers(
                category="linear",
                symbol=symbol
            )['result']['list'])
        
        df = df[df['symbol'].str.endswith('USDT')].reset_index(drop = True)
        df = df.astype({'lastPrice':float, 'indexPrice':float, 'markPrice':float, 
                        'prevPrice24h':float, 'price24hPcnt':float, 
                        'highPrice24h':float, 'lowPrice24h':float, 
                        'prevPrice1h':float, 'openInterest':float, 
                        'openInterestValue':float, 'turnover24h':float, 
                        'volume24h':float, 'fundingRate':float, 
                        'nextFundingTime':float, 'deliveryTime':float, 
                        'ask1Size':float, 'bid1Price':float, 
                        'ask1Price':float, 'bid1Size':float})
        return df.sort_values('price24hPcnt', ascending=False).reset_index(drop = True)

    def klines(self, symbol, interval, limit, category='linear' ):
        df = pd.DataFrame(self.session.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval, 
                        limit= limit  
                        )['result']['list'])
        # 열에 이름 지정 
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        # 타임스탬프를 날짜 형식으로 변환하고 ohlcv가 모두 숫자인지 확인합니다. 
        df['date'] = pd.to_datetime(df['date'], unit='ms') 
        for col in df.columns[1:]: 
            df[col ] = pd.to_numeric(df[col])
        return df
    
    def coin_info(self, symbol):
        return pd.DataFrame(self.session.get_instruments_info(
                            category="linear",
                            symbol=symbol,
                        )['result']['list'])
        
    def order(self,symbol, side, orderType, qty, price, isLeverage, orderFilter0):
        # 주문 하기
        return self.session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType=orderType,
            qty=qty,
            price=price,
            timeInForce="PostOnly",
            orderLinkId="linear-postonly",
            isLeverage=isLeverage,
            orderFilter=orderFilter0,
        )
        
    def cancel_order(self,symbol, orderId):
        # 주문 취소
        return self.session.cancel_order(
            category="linear",
            symbol=symbol,
            orderId=orderId,
        )
    def position_info(self, symbol=None, settleCoin = None):
        # 포지션 정보
        return pd.DataFrame(self.session.get_positions(
            category="linear",
            symbol=symbol,
            settleCoin  = settleCoin
        )['result']['list'])
    
    def set_leverage(self, symbol, leverage):
        #레버리지 설정
        try:
            return self.session.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage),
            )
        except:
            pass
    def set_marginType(self,symbol, type, leverage):
        '''
        ## MarginType: cross:0, isolated:1
        '''
        #마진 설정
        try:
            return self.session.switch_margin_mode(
                    category="linear",
                    symbol=symbol,
                    tradeMode=type, # cross:0, isolated:1
                    buyLeverage=str(leverage),
                    sellLeverage=str(leverage),
                )
        except:
            pass
        
    def traiding_stop(
        self,symbol, takeProfit,stopLoss, tpTriggerBy, slTriggerB, 
        tpSize, slSize,tpLimitPrice,slLimitPrice,positionIdx
        ):
        #트레이딩 스탑
        return self.session.set_trading_stop(
            category="linear",
            symbol=symbol,
            takeProfit=takeProfit,
            stopLoss=stopLoss,
            tpTriggerBy=tpTriggerBy,
            slTriggerB=slTriggerB,
            tpslMode="Partial",
            tpOrderType="Limit",
            slOrderType="Limit",
            tpSize=tpSize,
            slSize=slSize,
            tpLimitPrice=tpLimitPrice,
            slLimitPrice=slLimitPrice,
            positionIdx=positionIdx,
        )
        
    def wallet(self,):
        #자산 정보
        return pd.DataFrame(self.session.get_wallet_balance(
            accountType="CONTRACT",
            coin="BTC",
        )['result']['list'][0]['coin'])
    
    
    def account_info(self,):
        return  pd.DataFrame([self.session.get_account_info()['result']])
    
    def asset_info(self,coin, type='SPOT'):
        # 자산정보
        '''
        accountType	true	string	Account type. SPOT
        coin	false	string	USDT,USDC,USD...
        '''
        return self.session.get_spot_asset_info(
            accountType=type,
            coin=coin,
        )['result']['spot']['assets']