import pandas as pd
from pathlib import Path
import time
import statistics
import math
import matplotlib.pyplot as plt
# TODO multiprocessing would be good in this
pair = 'BNBUSDT'

start = time.perf_counter()

### load one file
# data = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_8.csv'), usecols=['price'])

### load all files
price_list = []
stored_files_path = Path(f'Data/trades/{pair}/')
files_list = list(stored_files_path.glob(f'{pair}*.csv'))
for i in range(len(files_list)):
    print(f'reading file {i}')
    df = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'), usecols=['price'])
    price_list.extend(list(df['price']))
    del df
data = pd.DataFrame(price_list, columns=['price'])

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
    eq_series = [(eq_curve[i]-eq_curve[i-1]) / eq_curve[i-1] for i in range(1, len(eq_curve))]
    if len(eq_series) > 1: # to avoid StatisticsError: variance requires at least two data points
        eq_std = statistics.stdev(eq_series)
        sqn = math.sqrt(len(eq_curve)) * statistics.mean(eq_series) / statistics.stdev(eq_series)
    else:
        eq_std = 0
        sqn = -1


    return profit, eq_std, len(eq_curve), sqn

tr_list = []
atr_list = []
pnl_list = []
std_dev_list = []
num_trades_list = []
sqn_list = []

x_range = (100, 600, 30)
signals = {}
test = 0
z_list = [round(1 / i**2, 4) for i in range(10, 0, -1)] # [0.01, 0.0123, 0.0156, 0.0204, 0.0278, 0.04, 0.0625, 0.1111, 0.25, 1.0]
for z in z_list:
    for x in range(x_range[0], x_range[1], x_range[2]):
        test_total = math.ceil((x_range[1] - x_range[0]) / x_range[2]) * len(z_list)
        tr_period = (x**2)+10
        data['tr'] = (data['price'].rolling(tr_period).max() - data['price'].rolling(tr_period).min()) / data['price'] # relative true range
        data = data[tr_period:]
        atr_period = round(tr_period*z)
        print(f'tr: {tr_period}, atr: {atr_period}')
        data['atr'] = data['tr'].rolling(atr_period).mean()
        data = data[atr_period:]
        y_data = list(data['price'])

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
        pnl, std_dev, num_trades, sqn = calc_stats(signals_list)
        tr_list.append(tr_period)
        atr_list.append(z)
        pnl_list.append(pnl)
        std_dev_list.append(std_dev)
        num_trades_list.append(num_trades)
        sqn_list.append(sqn)
        ### this is where the list of signals get stored in a dict
        # signals[f'{tr_period}-{atr_period}'] = signals_list
        data.drop(['tr', 'atr'], axis=1)
        test += 1
        print(f'test {test}')
        print(f'{round(100 * test / test_total)}% done.')


all_results = zip(tr_list, atr_list, pnl_list, num_trades_list, sqn_list)
results_df = pd.DataFrame(all_results, columns=['tr period', 'atr mult', 'pnl', 'num trades', 'sqn'])
print(results_df.head())
results_path = Path(f'Data/renko_idea_1_results/{pair}.csv')
results_df.to_csv(results_path)

end = time.perf_counter()
print(f'Time taken: {round(end-start) // 60}m {round(end-start) % 60}s')