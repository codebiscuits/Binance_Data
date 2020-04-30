import pandas as pd
from binance.client import Client
import time
import keys
from pathlib import Path
import math

#TODO Turn the whole thing into a function or something so that
# i can for-loop the whole process for every pair i want to download

start = time.perf_counter()

client = Client(api_key=keys.Pkey, api_secret=keys.Skey)
pair = 'BTCUSDT'
j_range = 5 # number of iterations for middle for-loop, ~100MB per iteration, currently 20 for btc, 5 for everything else
cols = ['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker', 'isBestMatch']

### get api request limit from binance to ensure it isn't being exceeded by this program
info = client.get_exchange_info()
limits = info.get('rateLimits')
request_limit = limits[0].get('limit') # this is the number used by the inner-most for-loop for its iterations

### get id of most recent trade on binance
recent = client.get_historical_trades(symbol=pair, limit=1)
last = recent[0].get('id') # last trade id in the entire list of trades available to download
print(f'latest id on binance: {last}')

### calculate how many files i should end up with
requests_per_file = request_limit * j_range
trades_per_file = requests_per_file * 1000
total_requests = last // 1000
i_range = math.ceil(total_requests/requests_per_file)
i_list = list(range(i_range))

### verify downloaded files have correct trade ranges and get id for last downloaded trade
stored_files_path = Path(f'Data/trades/{pair}/')
files_list = list(stored_files_path.glob(f'{pair}*.csv'))
print(f'verifying {pair} files')
completed = 0
done_list = []
for i in range(len(files_list)):
    file_path = Path(f'Data/trades/{pair}/{pair}_{i}.csv')
    from_id = i * j_range * request_limit * 1000
    to_id = ((i+1) * j_range * request_limit * 1000) - 1
    df = pd.read_csv(file_path)
    first_id = df.iloc[0, 1]
    last_id = df.iloc[-1, 1]
    if from_id == first_id and to_id == last_id and last_id - first_id == trades_per_file -1:
        print(f'file {i} complete')
        completed += 1
        done_list.append(i)
    elif from_id != first_id and to_id == last_id:
        print(f'file {i} not correct, should start {from_id} but started {first_id}')
    elif from_id == first_id and to_id > last_id:
        print(f'file {i} incomplete, should end {to_id} but ended {last_id}')
    else:
        print(f'file {i} should start {from_id} but started {first_id}, should end {to_id} but ended {last_id}')
    df = ''
print('-' * 40)

### remove from the list those which have already been completed
# done_list = [file.stem for file in files_list]
# done_list = [int(entry[-1]) for entry in done_list]
new_i_list = [i for i in i_list if i not in done_list]
i_list = new_i_list
print(f'Files in list: {i_list}')


def dl_loop(pair, file_cont=False):
    s = 1 # part of the percentage counter in the inner loop
    for i in i_list:
        j = 0 # initialise counter for while loop
        ### this loop determines how many files are produced. each one ends up ~2GB
        big_start = time.perf_counter()
        print(f'Starting file {i} at {time.ctime()[11:-8]}')
        ### define first trade ID to download for this file
        if file_cont:
            print(f'continuing file {i}')
            all_trades = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'), usecols=cols)
            trade_count = all_trades.iloc[-1, 0]
            start_id = trade_count + 1
        else:
            start_id = i*j_range*request_limit*1000 # using short-circuiting to ignore start_id if 0 and ignore range otherwise
            trades = client.get_historical_trades(symbol=pair, limit=1000, fromId=start_id, requests_params={'timeout': 60})  # returns a list of dictionaries
            all_trades = pd.DataFrame(trades, columns=cols)
            trade_count = all_trades.iloc[-1, 0]
        # start_id = 0 # short-circuit start_id in case there are more files which will need their own first_id
        while trade_count < (last - 1000) and j < j_range:
            k = 0 # initialise third counter for while loop
            ### this middle loop multiplies the iterations of the inner loop to make it up to a full download ~2GB
            start = time.perf_counter()
            j_loop_trades = pd.DataFrame(columns=cols)
            # print(f'Major loop {j+1} of {j_range}')
            if j == 0:
                k_range = request_limit-1
            else:
                k_range = request_limit
            while trade_count < last and k < k_range:
                ### this inner loop is rate limited by the middle loop to prevent too many api calls per minute
                #TODO Percentage progress meter is not quite right yet, it needs to differentiate between files
                # that are being filled from beginning to end, files that are being filled from half-way through
                # to the end, beginning to half-way through, and part-way through to part-way through.
                total_trades = last - start_id          # this line and the one below track progress through a resumed download
                progress = trade_count - start_id
                total_loops = j_range * request_limit   # this line and the one below track progress through a download from scratch
                current_loop = (j * k_range) + k
                if file_cont:
                    r = round((progress / total_trades) * 100)      # resumed download
                else:
                    r = round((current_loop / total_loops) * 100)   # download from scratch
                if (r-s) and (r % 10 == 0): # if current percentage is same as previous percentage, this will eval to false and be skipped
                    print(f'{r}% completed')
                if file_cont:
                    s = round((progress / total_trades) * 100)      # resumed download
                else:
                    s = round((current_loop / total_loops) * 100)   # download from scratch
                # if the ReadTimeout problem persists, the following line could be put in a try/except clause within a while loop to keep trying it until it works
                trades = client.get_historical_trades(symbol=pair, limit=1000, fromId=trade_count + 1, requests_params={'timeout': 60})
                new_trades = pd.DataFrame(trades, columns=cols)
                j_loop_trades = j_loop_trades.append(new_trades, ignore_index=True, sort=True)
                k += 1
                trade_count += 1000
                #TODO could try re-assigning 'last' here, if it doesn't cause an issue, it would allow the download to
                # continue right up to the latest trades that have happened since the download started.
            all_trades = all_trades.append(j_loop_trades, ignore_index=True, sort=True)
            end = time.perf_counter()
            loop_time = round(end - start)
            if loop_time < 61:
                time.sleep(61 - loop_time)
            inclusive_end = time.perf_counter()
            total_loop_time = round(inclusive_end - start)
            # download_rate = k_range / (total_loop_time / 60)
            # print(f'Download rate was {round((download_rate / request_limit) * 100)}% of request limit.')
            # print(all_trades.iloc[-1])
            # print(f'Loop time: {loop_time//60}m {loop_time%60}s, Including sleep: {total_loop_time//60}m {total_loop_time%60}s')
            # print('-' * 40)
            j += 1
        file_path = Path(f'Data/trades/{pair}/{pair}_{i}.csv')
        all_trades.to_csv(file_path)
        big_end = time.perf_counter()
        big_time = round(big_end - big_start)
        print(f'File {i} took {big_time//60}m {big_time%60}s')
        print('-' * 40)
        file_cont = False  # reset file_cont in case there are more files to download from the beginning


if len(files_list) == 0 or to_id == last_id:    # if there are no files in the folder or if the last downloaded trade has
                                                # the same id as the end of the last file
    print(f'downloading all available trades for {pair}')
    dl_loop(pair)
else:
    print(f'{last-last_id} trades to download')
    if last < to_id:
        print(f'all new trades will fit in current file, downloading id {last_id+1} to id {last}')
    if last > to_id:
        print('more than one file needed to fit all new trades, downloading id {last_id+1} to id {last}')
    dl_loop(pair, True)

end = time.perf_counter()
total_mins = round((end - start) / 60)
print(f'Download completed, time taken: {total_mins} minutes')