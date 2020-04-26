import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

data = pd.read_csv(Path('Data/trades/ETHUSDT_0.csv'), usecols=['id', 'price', 'quoteQty', 'time'])

id_arr = list(data['id'])
price_arr = list(data['price'])
qty_arr = list(data['quoteQty'])
time_arr = list(data['time'])

groups = {} # when trades are grouped together, the start and end indexes can be stored in this dictionary

dollars = 0
grp_start = 0
grp_end = 0
grp_num = 0

for i in range(len(qty_arr)):
    if dollars <= 100000:
        dollars += qty_arr[i]
    else:
        grp_end = i-1
        groups[grp_num] = (grp_start, grp_end, dollars)
        grp_start = i
        dollars = qty_arr[i]
        grp_num += 1

x = 0
for i in groups.values():
    x += i[2]

last_group = grp_num - 1
last_group_end = groups[last_group][1]
count_back = 1 - (len(qty_arr) - last_group_end)
qty_diff = sum(qty_arr) - x # difference between sum of dollar volume in groups and sum of dollar volume in original data
remaining = sum(qty_arr[count_back:]) # print sum of dollar volumes for all data points after last group end to compare with discrepancy
print(f'volume discrepancy: {qty_diff - remaining}')


# print(data.head())

# plt.plot(data.id,data.price)
# plt.show()

