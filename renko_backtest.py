import pandas as pd
from pathlib import Path
from binance.client import Client
import keys
import matplotlib.pyplot as plt

pair = 'BNBUSDT'
client = Client(api_key=keys.Pkey, api_secret=keys.Skey)

columns = pd.read_csv(Path(f'Data/renko_idea_1_results/{pair}.csv'), index_col=0).columns

def get_backtest(pair, column):
    data = pd.read_csv(Path(f'Data/renko_idea_1_results/{pair}.csv'), index_col=0)
    # print(data.iloc[:, 1])
    trade_series = list(data.iloc[:, column])
    trade_series = [x for x in trade_series if str(x) != 'nan']
    # print(trade_series[-1])
    trade_list = [trade[1:-2].split(', ') for trade in trade_series]

    new_trade_list = []
    for t in trade_list:
        i = [0, 0, 0]
        i[0] = int(t[0])
        i[1] = float(t[1])
        i[2] = t[2][-1]
        new_trade_list.append(i)

    return data.columns[column], new_trade_list

# results = {}
name_list = []
prof_list = []
for x in range(len(columns)):
    name, bt = get_backtest(pair, x)
    name_list.append(name)

    startcash = 1000
    cash = startcash
    asset = 0
    fees = 0.00075
    # fees = client.get_trade_fee(symbol=pair)
    # fees = fees.get('tradeFee')[0]
    # fees = fees.get('taker')
    # print(f'fees: {fees}')
    comm = 1 - fees
    if bt[0][2] == 's':
        bt = bt[1:]
    equity_curve = []
    for i in bt:
        if i[2] == 'b':
            asset = comm * cash / i[1]
            # print(f'bought {asset:.2f} units at {i[1]}, commision: {(fees * cash):.3f}')
        else:
            cash = comm * asset * i[1]
            equity_curve.append(cash)
            # print(f'sold {asset:.2f} units at {i[1]}, commision: {(fees * cash):.3f}')

    profit = (100 * (cash - startcash) / startcash)
    print(f'Settings: {name}, {len(equity_curve)} trades, Profit: {profit:.6}%')
    # results[name] = [cash, len(equity_curve)]
    prof_list.append(profit)
    # print(name)
    # print(equity_curve)

print(len(name_list))
a = (name_list[:17], prof_list[:17])
b = (name_list[17:34], prof_list[17:34])
c = (name_list[34:51], prof_list[34:51])
d = (name_list[51:68], prof_list[51:68])
e = (name_list[68:85], prof_list[68:85])
f = (name_list[85:102], prof_list[85:102])
g = (name_list[102:119], prof_list[102:119])
h = (name_list[119:136], prof_list[119:136])
i = (name_list[136:], prof_list[136:])

def shorten(letter):
    for name in letter[0]:
        name = name.split('-')[0]

shorten(a)
shorten(b)
shorten(c)
shorten(d)
shorten(e)
shorten(f)
shorten(g)
shorten(h)
shorten(i)


# results_df = pd.DataFrame(results)

# print(results_df.head(3))

# TODO write calculations for sqn and other metrics
# TODO turn it all into a for-loop going through each backtest, then only print balance and plot for the best one

# print(f'Final balance: {cash:.3}$\nProfit: {(100 * (cash - startcash) / startcash):.3}%')
#
plt.plot(a[0], a[1])
plt.plot(b[0], b[1])
plt.plot(c[0], c[1])
plt.plot(d[0], d[1])
plt.plot(e[0], e[1])
plt.plot(f[0], f[1])
plt.plot(g[0], g[1])
plt.plot(h[0], h[1])
plt.plot(i[0], i[1])

plt.show()