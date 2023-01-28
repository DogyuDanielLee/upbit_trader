import requests
import time
import pytz
import datetime
import pandas as pd

class UpbitQuotationAPI:
    def __init__(self):
        pass

    def get_1min_ohlcv(self, market:str="KRW-BTC", to:datetime.datetime=None, count=200, period:float=0.5):
        """ 1분 간격으로 캔들 정보(시가/고가/저가/종가/누적거래량/누적거래금액)를 반환

        Parameters:
            - market (str) : 요청 캔들 마켓, (ex. KRW-BTC, KRW-ETH)
            - to (datetime.datetime) : 마지막 캔들의 시간
            - count (int) : 요청하는 캔들의 개수 (200개 초과 시 분할하여 API 요청, 단 2000 초과 불가) 
            - period (float) : 분할 요청 간격
        
        Returns:
            - Pandas Dataframe of columns - [open, high, low, close, volume]
            - If API call fails (400), it will return 'None'.
        """
        MAX_COUNT = 200
        LIMIT = 2000 # 10 requests per sec (2000 count per sec)
        
        if count > LIMIT:
            return None
        
        if to is None:
            to = datetime.datetime.now()
        
        dfs = []

        try:
            while count > 0:
                count_curr =  min(count, MAX_COUNT)
                to_iso = to.strftime("%Y-%m-%d %H:%M:%S")
                url = f"https://api.upbit.com/v1/candles/minutes/1?market={market}&count={count_curr}&to={to_iso}"
                headers = {"accept": "application/json"}
                response = requests.get(url, headers=headers)
                
                datas = response.json()
                dt_list = []
                for data in datas:
                    dt = datetime.datetime.strptime(
                        data['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S"
                    )
                    dt_list.append(dt)
                df = pd.DataFrame(datas,
                                  columns=[
                                    'opening_price',
                                    'high_price',
                                    'low_price',
                                    'trade_price',
                                    'candle_acc_trade_volume',
                                    'candle_acc_trade_price',
                                  ],
                                  index=dt_list)
                df = df.sort_index()
                if df.shape[0] == 0:
                    break
                dfs += [df]

                count -= MAX_COUNT
                to = datetime.datetime.strptime(
                    datas[-1]['candle_date_time_utc'], "%Y-%m-%dT%H:%M:%S")

                if count > 0:
                    time.sleep(period)
            
            df = pd.concat(dfs).sort_index()
            df.rename(columns = {"opening_price": "open",
                                 "high_price": "high",
                                 "low_price": "low",
                                 "trade_price": "close",
                                 "candle_acc_trade_volume": "volume",
                                 "candle_acc_trade_price": "value"},
                      inplace= True)
            return df
        except Exception:
            return None

    def get_1day_ohlcv(self, market:str="KRW-BTC", to:datetime.date=None, count=200, period:float=0.5):
        """ 1일 간격으로 캔들 정보(시가/고가/저가/종가/누적거래량/누적거래금액)를 반환
        Parameters:
            - market (str) : 요청 캔들 마켓, (ex. KRW-BTC, KRW-ETH)
            - to (datetime.date) : 마지막 캔들의 날짜
            - count (int) : 요청하는 캔들의 개수 (200개 초과 시 분할하여 API 요청, 단 2000 초과 불가) 
            - period (float) : 분할 요청 간격
        
        Returns:
            - Pandas Dataframe of columns - [open, high, low, close, volume]
            - If API call fails (400), it will return 'None'.
        """
        MAX_COUNT = 200
        LIMIT = 2000 # 10 requests per sec (2000 count per sec)
        
        if count > LIMIT:
            return None
        
        if to is None:
            to = datetime.datetime.now()
        
        dfs = []

        try:
            while count > 0:
                count_curr =  min(count, MAX_COUNT)
                to_iso = to.strftime("%Y-%m-%d %H:%M:%S")
                url = f"https://api.upbit.com/v1/candles/days?market={market}&count={count_curr}&to={to_iso}"
                headers = {"accept": "application/json"}
                response = requests.get(url, headers=headers)
                
                datas = response.json()
                dt_list = []
                for data in datas:
                    dt = datetime.datetime.strptime(
                        data['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S"
                    )
                    dt_list.append(dt)
                df = pd.DataFrame(datas,
                                columns=[
                                    'opening_price',
                                    'high_price',
                                    'low_price',
                                    'trade_price',
                                    'candle_acc_trade_volume',
                                    'candle_acc_trade_price',
                                ],
                                index=dt_list)
                df = df.sort_index()
                if df.shape[0] == 0:
                    break
                dfs += [df]

                count -= MAX_COUNT
                to = datetime.datetime.strptime(
                    datas[-1]['candle_date_time_utc'], "%Y-%m-%dT%H:%M:%S")

                if count > 0:
                    time.sleep(period)
            
            df = pd.concat(dfs).sort_index()
            df.rename(columns = {"opening_price": "open",
                                "high_price": "high",
                                "low_price": "low",
                                "trade_price": "close",
                                "candle_acc_trade_volume": "volume",
                                "candle_acc_trade_price": "value"},
                      inplace= True)
            return df
        except Exception:
            return None

    def get_live_price(self, market:str="KRW-BTC"):
        """실시간 가격 정보와 최근거래일자 및 시각(UTC)을 반환
        
        Parameters:
            - market (str) : 요청 캔들 마켓, (ex. KRW-BTC, KRW-ETH)
        
        Returns:
            - price (float) : 요청 마켓의 실시간 가격
            - time_utc (datetime.datetime) : 요청 마켓의 최근 거래 일자 및 시각 (UTC)
            - time_now (datetime.datetime) : 해당 HTTP Request 직후의 시각 (UTC)
            - If API call fails (400), it will return (None, None, None)
        """
        try:
            url = f"https://api.upbit.com/v1/ticker?markets={market}"
            headers = {"accept": "application/json"}
            response = requests.get(url, headers=headers)
            data = response.json()
            price = data[0]['trade_price']
            time_utc = data[0]['trade_date'] + data[0]['trade_time']
            time_utc = datetime.datetime(
                year=int(time_utc[0:4]),
                month=int(time_utc[4:6]),
                day=int(time_utc[6:8]),
                hour=int(time_utc[8:10]),
                minute=int(time_utc[10:12]),
                second=int(time_utc[12:14]))
            time_now = datetime.datetime.now(tz=pytz.UTC)
            return float(price), time_utc, time_now

        except Exception:
            return None, None
        

class UpbitExchangeAPI:
    def __init__(self, upbit_access_key, upbit_secret_key):
        self.UPBIT_ACCESS_KEY = upbit_access_key
        self.UPBIT_SECRET_KEY = upbit_secret_key

    def post_bid_order_market(self):
        '''시장가 매수
        '''
        pass

    def post_bid_order_limit(self):
        '''지정가 매수
        '''
        pass

    def post_ask_order_market(self):
        '''시장가 매도
        '''
        pass

    def post_ask_order_limit(self):
        '''지정가 매도
        '''
        pass
