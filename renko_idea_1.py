import pandas as pd
from pathlib import Path
import time
# TODO multiprocessing would be good in this
pair = 'BNBUSDT'

start = time.perf_counter()

### load one file
data = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_8.csv'), usecols=['price'])

### load all files
# price_list = []
# stored_files_path = Path(f'Data/trades/{pair}/')
# files_list = list(stored_files_path.glob(f'{pair}*.csv'))
# for i in range(len(files_list)):
#     print(f'reading file {i}')
#     df = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'), usecols=['price'])
#     price_list.extend(list(df['price']))
#     del df
# data = pd.DataFrame(price_list, columns=['price'])

tr_column = []
atr_column = []
res_column = []
z_list = [0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10]
# results = {}
for z in z_list[:2]:
    for x in range(100, 150, 30):
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
        results_list = sorted(both, key=lambda x: x[0]) # sort by values from x_positive/x_negative (trade IDs)
        tr_column.append(tr_period)
        atr_column.append(atr_period)
        res_column.append(results_list)
        # results[f'{tr_period}-{atr_period}'] = results_list
        data.drop(['tr', 'atr'], axis=1)
        print(f'{x}% done.')

# maxim = max(len(v) for k, v in results.items()) # this is to make all tuple sequences the same length
# for k, v in results.items():
#     while len(v) < maxim:
#         v.append(None)
# results_df = pd.DataFrame.from_dict(results)
results_df = pd.DataFrame([tr_column, atr_column, res_column])
results_path = Path(f'Data/renko_idea_1_results/{pair}.csv')
results_df.to_csv(results_path)
end = time.perf_counter()
print(f'Time taken: {round(end-start) // 60}m {round(end-start) % 60}s')

# plt.plot(data['price'])
# plt.plot(x_positive,y_positive, 'bo')
# plt.plot(x_negative,y_negative, 'ro')
# plt.show()

# print(results)