from calendar import month
import urllib3
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
from backtesting.test import SMA
import pandas as pd
import os
import numpy as np
from binance import Client
from backtesting.lib import resample_apply
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
    d_rsi = 14  # Daily RSI lookback periods
    level_up = 75
    level_do = 10
    def init(self):
        self.d_rsi = 1
        
    def next(self):
        if self.position:
            self.position.close()
        change_pr = (self.data.Close[-1] - self.data.Open[-1]) > 0
        change_pr2 = (self.data.Close[-2] - self.data.Open[-2]) > 0
        
        if change_pr and change_pr2:
            self.sell()
        
        
api_key = "qCplIYtZsWN25xPIrljTBXB8pnRXIdgfiaAn0TypIsBNVyS5CdW1AFfTpjSnqsHv"
api_secret = "3tau8BetzPiO9Tu1c2zfkTCeVD911qKHLZcixGarquR82lwZfIJ0BIwMyIPKpIsh"
client = Client(api_key, api_secret, testnet=False)
balance = client.get_asset_balance(asset='USDT')
print("USDT: ", balance)

avg = []
loss_day = {}
win_day = {}
month = "Jul"
year = 2022
step = 25
plot = False

klines_m = client.get_historical_klines("BNBUSDT", '1M', f"1 {month}, {year}", f"30 {month}, {year}")
O,H,L,C = klines_m[0][1:5]

for i in range(1,30-step,step):
# for i in range(16,17,step):
    plot = True
    print("day ", i)
    klines = client.get_historical_klines(
        "BNBUSDT", '1h', f"{i} {month}, {year}", f"{i + step} {month}, {year}")
    klines = [list(map(float, k)) for k in klines]
    df = pd.DataFrame(klines,
                      columns="Opentime, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of "
                              "trades, "
                              "Taker buy base asset volume, Taker buy quote asset volume, Ignore".split(", "))
    df = df.iloc[:, :-5]
    df.index = pd.to_datetime(df.Opentime, unit='ms') + pd.DateOffset(hours=7)
    ipdb.set_trace()
    bt = Backtest(df, System, commission=.001,
                  exclusive_orders=True, cash=1000.0)
    stats = bt.run()
    print("stat peak ", stats.loc["Equity Peak [$]"])
    print("stat final: ", stats.loc["Equity Final [$]"])
    if stats.loc["Equity Final [$]"] > 1000:
        win_day[str(i)] = stats.loc["Equity Final [$]"]
    elif stats.loc["Equity Final [$]"] < 1000:
        loss_day[str(i)] = stats.loc["Equity Final [$]"]
    avg.append(float(stats.loc["Equity Final [$]"]))
    if plot:
        print(stats.loc['_trades'])
        bt.plot()
    print("*******************\n")

print(f"in {month} - {year} price change {100* (float(C)/float(O) - 1) :.3f}%")
print("\n total pnl: ", sum(avg) - 1000*len(avg))
print("win day: ", win_day)
print("loss day: ", loss_day)