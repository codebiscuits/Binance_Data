import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

pair = 'BNBUSDT'

data = pd.read_csv(Path(f'Data/trades/{pair}/{pair}_0.csv'), usecols=[
    # 'id',
    'price',
    # 'quoteQty',
    # 'time'
    ])

data['delta'] = data['price'] - data['price'].shift(1)
data['delta'][0] = 0

bricks = []

print(data.head())

# plt.plot(data.id,data.price)
# plt.show()