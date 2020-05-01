import pandas as pd
from pathlib import Path

pair = 'BTCUSDT'

id_list = []
stored_files_path = Path(f'Data/trades/{pair}/')
files_list = list(stored_files_path.glob(f'{pair}*.csv'))
for i in range(len(files_list)):
    print(f'reading file {i}')
    df = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_{i}.csv'),
                             usecols=['id'])
    id_list.extend(list(df['id']))
    del df

print('Verifying IDs')
last_perc = -1
for i in range(len(id_list)):
    percent = round(i / len(id_list) * 100)
    if percent - last_perc:
        print(f'{percent}% complete')
    if i != id_list[i]:
        print(f'mis-match: id {id_list[i]} at index {i}')
        break
    last_perc = percent