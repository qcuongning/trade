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
from sklearn.cluster import KMeans
import plotly
from plotly import graph_objects as go
import matplotlib.pyplot as plt

urllib3.disable_warnings()
pd.options.plotting.backend = 'plotly'

btc = pd.read_csv("./btc-2018now1d.csv", index_col=0, parse_dates=True, infer_datetime_format=True)
print(btc)

btc_prices = np.array(btc["Close"])
print("BTC Prices:\n", btc_prices)


# Perform cluster analysis
K = 6
kmeans = KMeans(n_clusters=6).fit(btc_prices.reshape(-1, 1))
# predict which cluster each price is in
clusters = kmeans.predict(btc_prices.reshape(-1, 1))
print("Clusters:\n", clusters)


# Arbitrarily 6 colors for our 6 clusters
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo']
clust_color = [colors[i] for i in clusters]
# Create Scatter plot, assigning each point a color based
# on it's grouping where group_number == index of color.
min_max_values = []


for i in range(K):
    price_cl1 = btc_prices[clusters == i]
    min_max_values.append([ min(price_cl1), max(price_cl1)])

output = []
# Sort based on cluster minimum
s = sorted(min_max_values, key=lambda x: x[0])
# For each cluster get average of
for i, (_min, _max) in enumerate(s):
    # Append min from first cluster
    if i == 0:
        output.append(_min)
    # Append max from last cluster
    if i == len(min_max_values) - 1:
        output.append(_max)
    # Append average from cluster and adjacent for all others
    else:
        output.append(sum([_max, s[i+1][0]]) / 2)

# Print resulting values
for cluster_avg in output[1:-1]:
    plt.hlines(y=cluster_avg, xmin=btc.index[0],xmax = btc.index[-1], colors="blue")

print(min_max_values)

plt.scatter(x = btc.index, y = btc_prices, color=clust_color, marker='.')
plt.show()
