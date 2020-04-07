from binance.client import Client
import keys

client = Client(api_key=keys.Pkey, api_secret=keys.Skey)

fees = client.get_trade_fee()
x = 1
for i in range(780):
    pair = fees.get('tradeFee')[i]
    symbol = pair.get('symbol')
    if symbol[-4:] == 'USDT':
        print(x, fees.get('tradeFee')[i])
        x += 1


# fees = client.get_trade_fee(symbol='BTCUSDT')
# fees = fees.get('tradeFee')[0]
# maker = fees.get('maker')
# taker = fees.get('taker')
# print(maker, taker)
