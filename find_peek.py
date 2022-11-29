from turtle import color
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks
# import ipdb

btc = pd.read_csv("./btc-2018now1d.csv", index_col=0, parse_dates=True, infer_datetime_format=True)

btc_prices = np.array(btc["Close"])
btc_prices = btc_prices[:1000]
inv_price = - btc_prices
inv_indices = find_peaks(inv_price)[0]
# print("BTC Prices:\n", btc_prices)

indices = find_peaks(btc_prices)[0]

fit_buy = []

for buy_id in inv_indices:
    try:
        next_sell = indices[np.where(indices > buy_id)[0][0]]
        # print(buy_id, next_sell)
        if btc_prices[next_sell] > btc_prices[buy_id] * 1.1:
            fit_buy.append(buy_id)
    except:
        print("something")


plt.plot(btc_prices, '-')
plt.scatter(fit_buy, [btc_prices[j] for j in fit_buy], marker="^", color="r")
# plt.scatter(indices, [btc_prices[j] for j in indices], marker="^", color="r")
# plt.scatter(inv_indices, [btc_prices[j] for j in inv_indices], marker="x", color="g")

plt.show()