import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import time

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
    df = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'),
                             usecols=['price'])
    price_list.extend(list(df['price']))
    del df

data = pd.DataFrame(price_list, columns=['price'])

results = {}
for x in range(46, 48):
    tr_period = (x**2)+10
    data['tr'] = (data['price'].rolling(tr_period).max() - data['price'].rolling(tr_period).min()) / data['price'] # relative true range
    data = data[tr_period:]
    y_data = list(data['price'])
    # TODO add another for-loop to test a range of tr/atr ratios
    atr_period = round(tr_period/10)
    data['atr'] = data['tr'].rolling(atr_period).mean()
    data = data[atr_period:]

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

    positive = list(zip(x_positive, y_positive))
    negative = list(zip(x_negative, y_negative))
    both = positive + negative
    results_list = sorted(both, key=lambda x: x[0])
    results[f'{tr_period}-{atr_period}'] = results_list
    data.drop(['tr', 'atr'], axis=1)
    print(f'{x}% done.')

maxim = max(len(v) for k, v in results.items())
for k, v in results.items():
    while len(v) < maxim:
        v.append(None)
results_df = pd.DataFrame.from_dict(results)
results_path = Path(f'Data/renko_idea_1_results/{pair}.csv')
results_df.to_csv(results_path)
end = time.perf_counter()
print(f'Time taken: {round(end-start) // 60}m {round(end-start) % 60}s')

# plt.plot(data['price'])
# plt.plot(x_positive,y_positive, 'bo')
# plt.plot(x_negative,y_negative, 'ro')
# plt.show()

# print(results)