import pandas as pd
from binance.client import Client
import time
import keys
from pathlib import Path

client = Client(api_key=keys.Pkey, api_secret=keys.Skey)
pair = 'BTCUSDT'

### get api request limit from binance to ensure it isn't being exceeded by this program
info = client.get_exchange_info()
limits = info.get('rateLimits')
request_limit = limits[0].get('limit')

i_range = 10
j_range = 20
s = 1 # just declaring this here to avoid calling before declaring later

for i in range(i_range):
    ### this loop determines how many files are produced. each one ends up ~2GB
    big_start = time.perf_counter()
    print(f'Downloading trades for file {i} at {time.gmtime()[3]}:{time.gmtime()[4]}')
    ### first define range of trade IDs included in this file
    first_id = i*j_range*request_limit
    trades = client.get_historical_trades(symbol='BTCUSDT', limit=1000, fromId=first_id)  # returns a list of dictionaries
    all_trades = pd.DataFrame(trades, columns=['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
    last_old_trade = all_trades.iloc[-1, 0]
    for j in range(j_range):
        ### this middle loop multiplies the iterations of the inner loop to make it up to a full download ~2GB
        start = time.perf_counter()
        print(f'Major loop {j+1} of {j_range}')
        if j == 0:
            k_range = request_limit-1
        else:
            k_range = request_limit
        for k in range(k_range):
            ### this inner loop is rate limited by the middle loop to prevent too many api calls per minute
            total_loops = j_range * request_limit
            current_loop = (j*k_range) + k
            r = round((current_loop / total_loops) * 100)
            if r-s:
                print(f'{r}% completed')
            s = round((current_loop / total_loops) * 100)
            trades = client.get_historical_trades(symbol='BTCUSDT', limit=1000, fromId=last_old_trade+1)
            new_trades = pd.DataFrame(trades, columns=['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
            all_trades = all_trades.append(new_trades, ignore_index=True, sort=True)
            last_old_trade = all_trades.iloc[-1, 0]
        end = time.perf_counter()
        loop_time = round(end - start)
        if loop_time < 61:
            time.sleep(61 - loop_time)
        inclusive_end = time.perf_counter()
        total_loop_time = round(inclusive_end - start)
        # print(all_trades.iloc[-1])
        print(f'Loop time: {loop_time//60}m {loop_time%60}s, Including sleep: {total_loop_time//60}m {total_loop_time%60}s')
        print('-' * 40)
    file_path = Path(f'Data/trades/{pair}_{i}.csv')
    all_trades.to_csv(file_path)
    big_end = time.perf_counter()
    big_time = big_end - big_start
    print(f'File {i} took {big_time//60}m {big_time%60}s')


# trades = client.get_historical_trades(symbol='BTCUSDT', limit=1)
# print(trades[0].get('id'))
# TODO use this most recent trade id to write an automatic stop into the loop

# TODO add some code to check the data folder for files already created
