import urllib3
from backtesting import Strategy, Backtest
import pandas as pd
import numpy as np
from binance import Client
from backtesting.lib import crossover

from backtesting.test import SMA
import ipdb
urllib3.disable_warnings()


def RSI(array, n):
    """Relative strength index"""
    # Approximate; good enough
    gain = pd.Series(array).diff()
    loss = gain.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    rs = gain.rolling(n).mean() / loss.abs().rolling(n).mean()
    return 100 - 100 / (1 + rs)

def stoch_rsi(array, n = 14):
    rsi = RSI(array, n)    
    min_rsi = rsi.rolling(n).min()
    max_rsi = rsi.rolling(n).max()
    stoch_rsi = (rsi-min_rsi)/(max_rsi-min_rsi +1e-3)*100
    return stoch_rsi


class System(Strategy):
    # def init(self):
    #     self.d_rsi = 14
    #     price = self.data.Close
    #     self.rsi = self.I(RSI, price, self.d_rsi)
    #     self.smooth_rsi = self.I(SMA, self.rsi, 3)
        
    # def next(self):
    #     long = self.smooth_rsi<30 and self.smooth_rsi>self.smooth_rsi[-2]
    #     short = self.smooth_rsi>70 and self.smooth_rsi<self.smooth_rsi[-2]
    #     if long and not long[-2]:
    #         self.buy()
            
    #     if short and not short[-2]:
    #         self.sell()
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()
        
        
api_key = "qCplIYtZsWN25xPIrljTBXB8pnRXIdgfiaAn0TypIsBNVyS5CdW1AFfTpjSnqsHv"
api_secret = "3tau8BetzPiO9Tu1c2zfkTCeVD911qKHLZcixGarquR82lwZfIJ0BIwMyIPKpIsh"
client = Client(api_key, api_secret, testnet=False)
balance = client.get_asset_balance(asset='USDT')
print("USDT: ", balance)

symbol = "ADAUSDT"
plot = True
klines = client.get_historical_klines(symbol, '1h', f"1 Aug, 2022", f"27 Nov, 2022")
klines = [list(map(float, k)) for k in klines]
df = pd.DataFrame(klines,
                    columns="Opentime, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of "
                            "trades, "
                            "Taker buy base asset volume, Taker buy quote asset volume, Ignore".split(", "))
df = df.iloc[:, :-5]
df.index = pd.to_datetime(df.Opentime, unit='ms') + pd.DateOffset(hours=7)
ipdb.set_trace()
bt = Backtest(df, System, commission=.001,
                exclusive_orders=True, cash=100.0)
stats = bt.run()
if plot:
    print(stats.loc['_trades'])
    bt.plot()
print("*******************\n")

