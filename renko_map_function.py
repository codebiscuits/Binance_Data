import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import time

pair = 'BNBUSDT'

### load one file
global data = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_8.csv'), usecols=['price'])

### load all files
# price_list = []
# stored_files_path = Path(f'Data/trades/{pair}/')
# files_list = list(stored_files_path.glob(f'{pair}*.csv'))
# for i in range(len(files_list)):
#     print(f'reading file {i}')
#     df = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'),
#                              usecols=['price'])
#     price_list.extend(list(df['price']))
#     del df
#
# global data = pd.DataFrame(price_list, columns=['price'])

period = range(10)

def renko_bars(period):
    tr_period =