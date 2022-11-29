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

        
        
api_key = "qCplIYtZsWN25xPIrljTBXB8pnRXIdgfiaAn0TypIsBNVyS5CdW1AFfTpjSnqsHv"
api_secret = "3tau8BetzPiO9Tu1c2zfkTCeVD911qKHLZcixGarquR82lwZfIJ0BIwMyIPKpIsh"
client = Client(api_key, api_secret, testnet=False)
balance = client.get_asset_balance(asset='USDT')
print("USDT: ", balance)


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

