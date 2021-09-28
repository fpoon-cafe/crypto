from exchange_config import EXCHANGE_CONFIG

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ccxt
import datetime as dt
import time
import random
from matplotlib.ticker import FuncFormatter

def toFloat(df):
    return pd.to_numeric(df, downcast='float')

def getTS(date_str):
    return int(time.mktime(dt.datetime.strptime(date_str, "%Y-%m-%d").timetuple()))

def getFundingRates(crypto, start_time, ndays):

    future = crypto + "-PERP"
    funding_df = pd.DataFrame(
        exch.public_get_funding_rates({'limit': 5000, 'future': future, 'start_time': start_time})['result'])

    funding_df['rate'] = toFloat(funding_df['rate']) * 24 * 365
    funding_df = funding_df.sort_values(by='time', ascending=True)
    funding_df['time'] = pd.to_datetime(funding_df['time'])

    # print(funding_df.head(10))
    # print(funding_df.dtypes)

    funding_df = funding_df.set_index('time')
    funding_df['rate_4h'] = funding_df.rate.rolling(4).mean()
    funding_df['rate_12h'] = funding_df.rate.rolling(12).mean()
    funding_df['rate_1d'] = funding_df.rate.rolling(24).mean()
    funding_df['rate_3d'] = funding_df.rate.rolling(72).mean()
    funding_df['rate_5d'] = funding_df.rate.rolling(120).mean()
    funding_df = funding_df.tail(ndays * 24)

    return funding_df


def plot(ax, label, df):

    ax.clear()
    ax.set_title(label, size=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

    df['rate'].plot.bar(y=label, ax=ax, label="1h")
    ax.plot(np.arange(len(df)) + 0.5, df['rate_4h'], color='pink', linewidth=2.0, label='4h')
    ax.plot(np.arange(len(df)) + 0.5, df['rate_1d'], color='orange', linewidth=2.0,label='1d')
    ax.plot(np.arange(len(df)) + 0.5, df['rate_5d'], color='brown', linewidth=2.0, label='5d')
    ax.set_xticks([])
    ax.set(xlabel=None)
    ax.legend(loc="lower left", ncol=4, fontsize=7)
    ax.autoscale_view(True, True, True)  # Autoscale

exchange_class = getattr(ccxt, 'ftx')
start_date = '2021-09-01'

crypto_list = EXCHANGE_CONFIG.CRYPTO_LIST
NCOLS = 3
NROWS = int(len(crypto_list) / NCOLS)

start_time = getTS(start_date)

api_key = EXCHANGE_CONFIG.KEY
api_secret = EXCHANGE_CONFIG.SECRET
ndays = 2

exch = exchange_class({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})

fig, ax = plt.subplots(NROWS,NCOLS, figsize=(13,8))
plt.style.use("seaborn")
plt.tight_layout()

while True:
    print('refreshing ' + str(dt.datetime.now()))
    idx=0
    for row in range(NROWS):
        for col in range(NCOLS):
            if idx >= len(crypto_list):
                break

            funding_df = getFundingRates(crypto_list[idx], start_time, ndays)
            plot(ax[row,col], crypto_list[idx], funding_df)
            idx += 1

    delta = dt.timedelta(hours=EXCHANGE_CONFIG.FUNDING_INTERVAL)
    now = dt.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=2)
    wait_seconds = (next_hour - now).seconds
    print("next hourly refresh in " + str(wait_seconds) + "s")

    plt.pause(wait_seconds)
    plt.draw()
    random.shuffle(crypto_list)
