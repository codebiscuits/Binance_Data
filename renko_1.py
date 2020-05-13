import pandas as pd
from pathlib import Path
import time
import statistics
import math
# import tqdm
import matplotlib.pyplot as plt
# TODO multiprocessing would be good in this
pair = 'BNBUSDT'

start = time.perf_counter()

### load one file
# data = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_8.csv'), usecols=['price'])

### load all files
def load_files(pair):
    price_list = []
    stored_files_path = Path(f'Data/trades/{pair}/')
    files_list = list(stored_files_path.glob(f'{pair}*.csv'))
    for i in range(len(files_list)):
        print(f'reading file {i}')
        df = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'), usecols=['price'])
        price_list.extend(list(df['price']))
        del df
    df = pd.DataFrame(price_list, columns=['price'])
    return df
data = load_files(pair)

def calc_stats(signals):
    startcash = 1000
    cash = startcash
    asset = 0
    fees = 0.00075
    # fees = client.get_trade_fee(symbol=pair) # when i get this working, it will be more reliable than a constant
    # fees = fees.get('tradeFee')[0]
    # fees = fees.get('taker')
    # print(f'fees: {fees}')
    comm = 1 - fees
    print(f'signals[0]: {signals[0]}')
    if signals[0][2] == 's':
        signals = signals[1:]
    eq_curve = []
    for i in signals:
        if i[2] == 'b':
            asset = comm * cash / i[1]
            # print(f'bought {asset:.2f} units at {i[1]}, commision: {(fees * cash):.3f}')
        else:
            cash = comm * asset * i[1]
            eq_curve.append(cash)
            # print(f'sold {asset:.2f} units at {i[1]}, commision: {(fees * cash):.3f}')

    profit = (100 * (cash - startcash) / startcash)
    # print(f'Settings: {name}, {len(equity_curve)} trades, Profit: {profit:.6}%')
    pnl_series = [(eq_curve[i]-eq_curve[i-1]) / eq_curve[i-1] for i in range(1, len(eq_curve))]
    if len(pnl_series) > 1: # to avoid StatisticsError: variance requires at least two data points
        eq_std = statistics.stdev(pnl_series)
        sqn = math.sqrt(len(eq_curve)) * statistics.mean(pnl_series) / statistics.stdev(pnl_series)
    else:
        eq_std = 0
        sqn = -1

    wins = 0
    losses = 0
    for i in range(1, len(pnl_series)):
        if i > 0:
            wins += 1
        else:
            losses += 1
    winrate = round(100 * wins / (wins+losses))


    return profit, eq_std, len(eq_curve), sqn, winrate

tr_list = []
atr_list = []
pnl_list = []
std_dev_list = []
num_trades_list = []
sqn_list = []
winrate_list = []

### Parameter ranges
x_range = (100, 1000, 30)
z_list = [round(1.5 / i**2, 4) for i in range(15, 0, -1)]
### [0.0067, 0.0077, 0.0089, 0.0104, 0.0124, 0.015, 0.0185, 0.0234, 0.0306, 0.0417, 0.06, 0.0938, 0.1667, 0.375, 1.5]
# x_range = (760, 1000, 500)
# z_list = [0.015]
test_total = math.ceil((x_range[1] - x_range[0]) / x_range[2]) * len(z_list)

signals = {}
test = 0

print(f'Number of tests to complete: {test_total}')
print(f'Starting tests at {time.ctime()[11:-8]}')
for z in z_list:
    for x in range(x_range[0], x_range[1], x_range[2]):
        print('-' * 40)
        tr_period = (x**2)+10
        data['tr'] = (data['price'].rolling(tr_period).max() - data['price'].rolling(tr_period).min()) / data['price'] # relative true range
        data = data[tr_period:]
        atr_period = round(tr_period*z)
        test += 1
        data['atr'] = data['tr'].rolling(atr_period).mean()
        data = data[atr_period:]
        y_data = list(data['price'])

        print(f'test {test}: tr {tr_period}, atr {atr_period} (x={x} z={z})')
        if not data.empty: # sometimes data just magically becomes empty and causes an exception
            delta = data.iloc[0, 2]      # delta factor
            pre = data.iloc[0, 0]   # first data-point;
            increment = 0
            x_positive = []
            y_positive = []
            x_negative = []
            y_negative = []
            tracker = []
            t = 0
            for i, point in enumerate(y_data): # y_data contains BTCUSD prices
                # print(f'i: {i}')
                increment += point-pre
                increment_perc = increment/pre
                pre = point
                if tracker:
                    pos = tracker[t-1] == 1
                    neg = tracker[t-1] == 0
                    if increment_perc > delta:
                        if neg:
                            x_positive.append(i)
                            y_positive.append(point)
                            tracker.append(1)
                            t += 1
                        increment = 0
                        delta = data.iloc[i, 2]
                    if increment_perc < -delta:
                        if pos:
                            x_negative.append(i)
                            y_negative.append(point)
                            tracker.append(0)
                            t += 1
                        increment = 0
                        delta = data.iloc[i, 2]
                else:
                    if increment_perc > delta:
                        x_positive.append(i)
                        y_positive.append(point)
                        increment = 0
                        delta = data.iloc[i, 2]
                        tracker.append(1)
                        t += 1
                    if increment_perc < -delta:
                        x_negative.append(i)
                        y_negative.append(point)
                        increment = 0
                        delta = data.iloc[i, 2]
                        tracker.append(0)
                        t += 1

            buys = list('b' * len(x_positive)) # create a list of 'b'
            sells = list('s' * len(x_negative)) # create a list of 's'
            positive = list(zip(x_positive, y_positive, buys))
            negative = list(zip(x_negative, y_negative, sells))
            both = positive + negative
            signals_list = sorted(both, key=lambda x: x[0]) # sort by values from x_positive/x_negative (trade IDs)
            print(f'signals_list length: {len(signals_list)}')
            if len(signals_list) > 10: # if no signals are produced, it causes an exception here
                pnl, std_dev, num_trades, sqn, winrate = calc_stats(signals_list)
                tr_list.append(tr_period)
                atr_list.append(z)
                pnl_list.append(pnl)
                std_dev_list.append(std_dev)
                num_trades_list.append(num_trades)
                sqn_list.append(sqn)
                winrate_list.append(winrate)
                data.drop(['tr', 'atr'], axis=1)
                print(f'{round(100 * test / test_total)}% done.')


all_results = zip(tr_list, atr_list, pnl_list, num_trades_list, sqn_list, winrate_list)
results_df = pd.DataFrame(all_results, columns=['tr period', 'atr mult', 'pnl', 'num trades', 'sqn', 'winrate'])
results_path = Path(f'Data/renko_idea_1_results/{pair}.csv')
results_df.to_csv(results_path)

end = time.perf_counter()
if round(end-start) // 60 <=60:
    print(f'Time taken: {round(end-start) // 60}m {round(end-start) % 60}s')
else:
    print(f'Time taken: {round(end - start) // 3600}h {(round(end - start) // 60) % 60}m {round(end - start) % 60}s')