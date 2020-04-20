import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

data = pd.read_csv(Path('Data/trades/BTCUSDT_9.csv'), usecols=['id', 'price', 'quoteQty', 'time'])
data = data.iloc[:100000, 0:2]



plt.plot(data.id,data.price)
plt.show()