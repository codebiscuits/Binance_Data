import pandas as pd
import math
import os.path
from binance.client import Client
from datetime import datetime
import time
from dateutil import parser
import keys
from pathlib import Path

client = Client(api_key=keys.Pkey, api_secret=keys.Skey)
pair = 'BTCUSDT'

info = client.get_exchange_info()
limits = info.get('rateLimits')
request_limit = limits[0].get('limit')

i_range = 10
j_range = 20

for i in range(i_range):
    big_start = time.perf_counter()
    print(f'Downloading trades for file {i} at {time.gmtime()[3]}:{time.gmtime()[4]}')
    ### first define range of trade IDs included in this file
    first_id = i*j_range*request_limit
    trades = client.get_historical_trades(symbol='BTCUSDT', limit=1000, fromId=first_id)  # returns a list of dictionaries
    all_trades = pd.DataFrame(trades, columns=['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
    last_old_trade = all_trades.iloc[-1, 0]
    for j in range(j_range):
        start = time.perf_counter()
        print(f'Major loop {j+1} of {j_range}')
        if j == 0:
            k_range = request_limit-1
        else:
            k_range = request_limit
        for k in range(k_range):
            if (k+1) % 200 == 0:
                print(f'Minor loop: {k + 1}')
            trades = client.get_historical_trades(symbol='BTCUSDT', limit=1000, fromId=last_old_trade+1)
            new_trades = pd.DataFrame(trades, columns=['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
            all_trades = all_trades.append(new_trades, ignore_index=True, sort=True)
            last_old_trade = all_trades.iloc[-1, 0]
        end = time.perf_counter()
        loop_time = end - start
        if loop_time < 61:
            time.sleep(61 - loop_time)
        inclusive_end = time.perf_counter()
        total_loop_time = inclusive_end - start
        print(all_trades.iloc[-1])
        print(f'Loop time: {loop_time}, Loop time including sleep: {total_loop_time}')
        print('-' * 40)
    file_path = Path(f'Data/trades/{pair}_{i}.csv')
    all_trades.to_csv(file_path)
    big_end = time.perf_counter()
    big_time = big_end - big_start
    print(f'File {i} took {big_time//60}m {big_time%60}s')


# trades = client.get_historical_trades(symbol='BTCUSDT', limit=1)
# print(trades[0].get('id'))
