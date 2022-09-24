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

urllib3.disable_warnings()


def RSI(array, n):
    """Relative strength index"""
    # Approximate; good enough
    gain = pd.Series(array).diff()
    loss = gain.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    rs = gain.ewm(n).mean() / loss.abs().ewm(n).mean()
    return 100 - 100 / (1 + rs)


class System(Strategy):
    d_rsi = 30  # Daily RSI lookback periods
    w_rsi = 30  # Weekly
    level = 70
    
    def init(self):
        # Compute moving averages the strategy demands
        self.ma10 = self.I(SMA, self.data.Close, 10)
        self.ma20 = self.I(SMA, self.data.Close, 20)
        self.ma50 = self.I(SMA, self.data.Close, 50)
        self.ma100 = self.I(SMA, self.data.Close, 100)
        
        # Compute daily RSI(30)
        self.daily_rsi = self.I(RSI, self.data.Close, self.d_rsi)
        
        # To construct weekly RSI, we can use `resample_apply()`
        # helper function from the library
        # self.weekly_rsi = resample_apply(
        #     'W-FRI', RSI, self.data.Close, self.w_rsi)
        
        
    def next(self):
        price = self.data.Close[-1]
        
        # If we don't already have a position, and
        # if all conditions are satisfied, enter long.
        # print(self.daily_rsi[-1] > self.level,
        #     self.ma10[-1] > self.ma20[-1] > self.ma50[-1] > self.ma100[-1], price > self.ma10[-1])

        if (not self.position and
            self.daily_rsi[-1] > self.level and
            self.ma10[-1] > self.ma20[-1] > self.ma50[-1] > self.ma100[-1] and price > self.ma10[-1]):
            
            # Buy at market price on next open, but do
            # set 8% fixed stop loss.
            self.buy(sl=.92 * price)
        
        # If the price closes 2% or more below 10-day MA
        # close the position, if any.
        elif price < .98 * self.ma10[-1]:
            self.position.close()

# binance future api
# api_key = "c21f1bb909318f36de0f915077deadac8322ad7df00c93606970441674c1b39b"
# api_secret = "be2d7e74239b2e959b3446b880451cbb4dee2e6be9d391c4c55ae7ca0976f403"
# testnet spot api
# api_key = "6vHuJQ4RvEe2aEf2KJEdM3DuAOvfQ2qDV0AONlkdIG5f5f7poex3empbw8FqxK1W"
# api_secret = "a86J1KCCeSebOneP23pWOviVXImkkRVaFwrJ7gi0eSCTEYOKQGBLNmRIOPlgldzB"
# real api
api_key = "qCplIYtZsWN25xPIrljTBXB8pnRXIdgfiaAn0TypIsBNVyS5CdW1AFfTpjSnqsHv"
api_secret = "3tau8BetzPiO9Tu1c2zfkTCeVD911qKHLZcixGarquR82lwZfIJ0BIwMyIPKpIsh"
client = Client(api_key, api_secret, testnet=False)
balance = client.get_asset_balance(asset='USDT')
print("USDT: ", balance)

avg = []
loss_day = {}
win_day = {}
month = "Apr"
step = 3
for i in range(1,30-step,step):
    print("day ", i)
    klines = client.get_historical_klines(
        "BNBUSDT", '5m', f"{i} {month}, 2021", f"{i + step} {month}, 2021")
    klines = [list(map(float, k)) for k in klines]
    df = pd.DataFrame(klines,
                      columns="Opentime, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of "
                              "trades, "
                              "Taker buy base asset volume, Taker buy quote asset volume, Ignore".split(", "))
    df = df.iloc[:, :-5]
    df.index = pd.to_datetime(df.Opentime, unit='ms') + pd.DateOffset(hours=7)

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
    # print(stats.loc['_trades'])
    # bt.plot()
    print("*******************\n")

print("\n total pnl: ", sum(avg) - 1000*len(avg))
print("win day: ", win_day)
print("loss day: ", loss_day)