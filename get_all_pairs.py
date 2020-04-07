from binance.client import Client
import keys

client = Client(api_key=keys.Pkey, api_secret=keys.Skey)

def get_pairs(quote):

    info = client.get_exchange_info()
    symbols = info['symbols']
    length = len(quote)
    pairs_list = []

    for item in symbols:
        if item['symbol'][-length:] == quote:
            if not (item['symbol'] in ['PAXUSDT', 'USDSBUSDT', 'BCHSVUSDT', 'BCHABCUSDT', 'VENUSDT', 'TUSDUSDT', 'USDCUSDT', 'USDSUSDT', 'BUSDUSDT', 'EURUSDT', 'BCCUSDT', 'IOTAUSDT']):
                pairs_list.append(item['symbol'])

    return pairs_list
