import pandas as pd
from binance.client import Client
import time
import keys
from pathlib import Path
import math

client = Client(api_key=keys.Pkey, api_secret=keys.Skey)
pair = 'ETHUSDT'

### get api request limit from binance to ensure it isn't being exceeded by this program
info = client.get_exchange_info()
limits = info.get('rateLimits')
request_limit = limits[0].get('limit') # this is the number used by the inner-most for-loop for its iterations

j_range = 5 # number of iterations for middle for-loop
s = 1 # just declaring this here to avoid calling before declaring later

### get id of most recent trade on binance
recent = client.get_historical_trades(symbol=pair, limit=1)
last = recent[0].get('id') # last trade id in the entire list of trades available to download
total_requests = last // 1000
### calculate how many files need to be made
requests_per_file = request_limit * j_range
i_range = math.ceil(total_requests/requests_per_file)
i_list = list(range(i_range))
### remove from the list those which have already been completed
stored_files_path = Path(f'Data/trades/')
files_list = stored_files_path.glob('*.csv')
done_list = [file.stem for file in files_list]
done_list = [int(entry[-1]) for entry in done_list]
new_i_list = [i for i in i_list if i not in done_list]
i_list = new_i_list
print(f'Files in list: {i_list}')

for i in i_list:
    j = 0 # initialise counter for while loop
    ### this loop determines how many files are produced. each one ends up ~2GB
    big_start = time.perf_counter()
    print(f'Downloading trades for file {i} at {time.gmtime()[3]}:{time.gmtime()[4]}')
    ### first define first trade ID included in this file
    first_id = i*j_range*request_limit*1000
    trades = client.get_historical_trades(symbol='BTCUSDT', limit=1000, fromId=first_id, requests_params={'timeout': 60})  # returns a list of dictionaries
    all_trades = pd.DataFrame(trades, columns=['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
    trade_count = all_trades.iloc[-1, 0]
    while trade_count < (last - 1000) and j < j_range:
        k = 0 # initialise third counter for while loop
        ### this middle loop multiplies the iterations of the inner loop to make it up to a full download ~2GB
        start = time.perf_counter()
        j_loop_trades = pd.DataFrame(columns=['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
        # print(f'Major loop {j+1} of {j_range}')
        if j == 0:
            k_range = request_limit-1
        else:
            k_range = request_limit
        while trade_count < last and k < k_range:
            ### this inner loop is rate limited by the middle loop to prevent too many api calls per minute
            total_loops = j_range * request_limit
            current_loop = (j*k_range) + k
            r = round((current_loop / total_loops) * 100)
            if (r-s) and (r % 10 == 0): # if current percentage is same as previous percentage, this will eval to false and be skipped, also must be divisible by 5
                print(f'{r}% completed')
            s = round((current_loop / total_loops) * 100)
            # if the ReadTimeout problem persists, the following line could be put in a try/except clause within a while loop to keep trying it until it works
            trades = client.get_historical_trades(symbol='BTCUSDT', limit=1000, fromId=trade_count + 1, requests_params={'timeout': 60})
            new_trades = pd.DataFrame(trades, columns=['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch'])
            j_loop_trades = j_loop_trades.append(new_trades, ignore_index=True, sort=True)
            k += 1
            trade_count += 1000
        all_trades = all_trades.append(j_loop_trades, ignore_index=True, sort=True)
        end = time.perf_counter()
        loop_time = round(end - start)
        if loop_time < 61:
            time.sleep(61 - loop_time)
        inclusive_end = time.perf_counter()
        total_loop_time = round(inclusive_end - start)
        download_rate = k_range / (total_loop_time / 60)
        # print(f'Download rate was {round((download_rate / request_limit) * 100)}% of request limit.')
        # print(all_trades.iloc[-1])
        # print(f'Loop time: {loop_time//60}m {loop_time%60}s, Including sleep: {total_loop_time//60}m {total_loop_time%60}s')
        # print('-' * 40)
        j += 1
    file_path = Path(f'Data/trades/{pair}_{i}.csv')
    all_trades.to_csv(file_path)
    big_end = time.perf_counter()
    big_time = round(big_end - big_start)
    print(f'File {i} took {big_time//60}m {big_time%60}s')
    print('-' * 40)
