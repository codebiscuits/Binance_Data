import pandas as pd
from binance.client import Client
import time
import keys
from pathlib import Path
import math
import matplotlib as plt

data = pd.read_csv(Path('Data/trades/BTCUSDT_9.csv'), usecols=['id', 'price', 'quoteQty', 'time'])
# print(data.iloc[0, :])
# print(data.iloc[-1, :])
print(data.head())

