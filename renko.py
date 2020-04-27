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

print(data.head())

# plt.plot(data.id,data.price)
# plt.show()