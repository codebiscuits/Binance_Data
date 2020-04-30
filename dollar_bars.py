import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

pair = 'BNBUSDT'
bar_size = 1000000

def create_bars(pair, size):
    price_list = []
    qty_list = []
    stored_files_path = Path(f'Data/trades/{pair}/')
    files_list = list(stored_files_path.glob(f'{pair}*.csv'))
    for i in range(len(files_list)):
        print(f'reading file {i}')
        df = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'),
                                 usecols=['price', 'quoteQty'])
        price_list.extend(list(df['price']))
        qty_list.extend(list(df['quoteQty']))
        del df

    groups = {}  # when trades are grouped together, the start and end indexes can be stored in this dictionary

    dollars = 0
    grp_start = 0
    grp_num = 0

    for i in range(len(qty_list)):
        if dollars < size:
            dollars += qty_list[i]
        else:
            grp_end = i - 1
            groups[grp_num] = (grp_start, grp_end,
                               # dollars # only needed for checking data
                               )
            grp_start = i
            dollars = qty_list[i]
            grp_num += 1

    ### count up volume in groups to check against original data
    # x = 0
    # for i in groups.values():
    #     x += i[2]
    #
    # last_group = grp_num - 1
    # last_group_end = groups[last_group][1]
    # count_back = 1 - (len(arr) - last_group_end)
    # qty_diff = sum(arr) - x  # difference between sum of dollar volume in groups and sum of dollar volume in original data
    # remaining = sum(arr[count_back:])  # print sum of dollar volumes for all data points after last group end to compare with discrepancy
    # print(f'volume discrepancy: {qty_diff - remaining}')
    # print(len(groups))
    #
    # return groups

    ohlc_dict = {}

    for i in range(len(groups)):
        start = groups.get(i)[0]
        end = groups.get(i)[1]
        o = price_list[start]
        h = max(price_list[start:end+1])
        l = min(price_list[start:end+1])
        c = price_list[end]
        ohlc_dict[i] = (o, h, l, c)

    return pd.DataFrame.from_dict(ohlc_dict, orient='index', columns=['o', 'h', 'l', 'c'])


ohlc_bars = create_bars(pair, bar_size)

print(ohlc_bars.head())


plt.plot(ohlc_bars.index, ohlc_bars['c'])
plt.show()

