from binance.client import Client
import keys
from get_all_pairs import get_pairs

client = Client(api_key=keys.Pkey, api_secret=keys.Skey)

pairs_list = get_pairs('USDT')

### Print out the current number of pairs being actively traded and the current number that are on the pairs list but not actively traded
x, y = 0, 0
for pair in pairs_list:
    info = client.get_symbol_info(pair)
    if info.get('status') == 'TRADING':
        x += 1
    elif info.get('status') == 'BREAK':
        print(info.get('symbol'))
        y += 1
print(f'Trading: {x} Break: {y}')
