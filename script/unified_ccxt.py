import ccxt
from graphviz import Digraph
from collections import deque
from pprint import PrettyPrinter
from functools import reduce
import time
import math

class exchange(ccxt.Exchange):
    def __init__(self):
        exchange.__base__.__init__(self)
        # all the startup things here
        self.loaded_market = self.load_markets()

class binance(exchange, ccxt.binance):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return super(binance, self).fetch_tickers()

    def get_ticker(self, symbol, param={}):
        depth = binance.__base__.public_get_depth({'symbol':symbol, 'limit':5})
        return {
            'askPrice': float(depth['asks'][0][0]),
            'askQty':   float(depth['asks'][0][1]),
            'bidPrice': float(depth['bids'][0][0]),
            'bidQty':   float(depth['bids'][0][1])
        }


class bitfinex2(exchange, ccxt.bitfinex2):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        tickers = super(bitfinex2, self).fetch_tickers()
        return {i: {
                **tickers[i],
                **{
                    'info': {
                        'symbol': tickers[i]['info'][0][1:],
                        'bidPrice': tickers[i]['info'][1],
                        'bidQty': tickers[i]['info'][2],
                        'askPrice': tickers[i]['info'][3],
                        'askQty': tickers[i]['info'][4],
                        'dailyChange': tickers[i]['info'][5],
                        'dailyChangePerc': tickers[i]['info'][6],
                        'lastPrice': tickers[i]['info'][7],
                        'volume': tickers[i]['info'][8],
                        'highPrice': tickers[i]['info'][9],
                        'lowPrice': tickers[i]['info'][10],
                    }
                }
        } for i in tickers if tickers[i]['info'][0][0] == 't'}

    def get_ticker(self, symbol, param={}):
        ticker = super(bitfinex2, self).fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info'][2]),
            'askQty': float(ticker['info'][3]),
            'bidPrice': float(ticker['info'][0]),
            'bidQty': float(ticker['info'][1])
        }

class okcoinusd(exchange, ccxt.okcoinusd):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return super(okcoinusd, self).fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['ask']),
            'bidPrice': float(ticker['bid']),
        }

class bitstamp(exchange, ccxt.bitstamp1):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return self.fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info']['ask']),
            'bidPrice': float(ticker['info']['bid'])
        }

class gemini(exchange, ccxt.gemini):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return self.fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info']['ask']),
            'bidPrice': float(ticker['info']['bid'])
        }

class kraken(exchange, ccxt.kraken):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return self.fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info']['a'][0]),
            'bidPrice': float(ticker['info']['b'][0])
        }

class itbit(exchange, ccxt.itbit):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return self.fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info']['ask']),
            'bidPrice': float(ticker['info']['bid'])
        }

class gdax(exchange, ccxt.gdax):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return self.fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info']['ask']),
            'bidPrice': float(ticker['info']['bid'])
        }

class quadrigacx(exchange, ccxt.quadrigacx):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return self.fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info']['ask']),
            'bidPrice': float(ticker['info']['bid'])
        }

class exmo(exchange, ccxt.exmo):
    def __init__(self):
        exchange.__init__(self)

    def get_tickers(self):
        return self.fetch_tickers()

    def get_ticker(self, symbol, param={}):
        ticker = self.fetch_ticker(symbol, param)
        return {
            'askPrice': float(ticker['info']['sell_price']),
            'bidPrice': float(ticker['info']['buy_price'])
        }

if __name__ == "__main__":
    pp = PrettyPrinter()
    pprint = pp.pprint

    long_exchanges = [okcoinusd(), bitstamp(), gemini(), kraken(), itbit(), gdax(), quadrigacx(), exmo()]
    short_exchanges = [bitfinex2()]

    while True:
        for short_exchange in short_exchanges:
            short_ticker = short_exchange.get_ticker('BTC/USD')
            for long_exchange in long_exchanges:
                long_ticker = long_exchange.get_ticker('BTC/USD')

                profit_percent = (short_ticker['askPrice'] - long_ticker['bidPrice']) / long_ticker['bidPrice'] * 100
                print("%s/%s:\t %.2f" % (long_exchange.id, short_exchange.id, profit_percent))
        print("----------------------------------------")
        time.sleep(1)

    gem = exmo()
    pprint(gem.get_ticker('BTC/USD'))
    exit(0)

    all_exchanges = [
        ccxt.binance      ,ccxt.bithumb    ,ccxt.bittrex      ,ccxt.btctradeua  ,ccxt.chbtc          ,ccxt.coinsecure,
        ccxt.fybse     ,ccxt.hitbtc2             ,ccxt.itbit    ,ccxt.livecoin   ,ccxt.okex        ,ccxt.southxchange  ,ccxt.virwox,
        ccxt.bit2c        ,ccxt.bitlish    ,ccxt.bl3p         ,ccxt.btcturk     ,ccxt.chilebit       ,ccxt.coinspot,
        ccxt.fybsg     ,ccxt.hitbtc              ,ccxt.jubi     ,ccxt.luno       ,ccxt.paymium     ,ccxt.surbitcoin    ,ccxt.wex,
        ccxt.acx       ,ccxt.bitbay       ,ccxt.bitmarket  ,ccxt.bleutrade    ,ccxt.btcx        ,ccxt.coincheck      ,ccxt.cryptopia,
        ccxt.gatecoin  ,ccxt.huobicny            ,ccxt.kraken   ,ccxt.mercado    ,ccxt.poloniex    ,ccxt.therock       ,ccxt.xbtce,
        ccxt.allcoin   ,ccxt.bitcoincoid  ,ccxt.bitmex     ,ccxt.btcbox       ,ccxt.bter        ,ccxt.coinfloor      ,ccxt.dsx,
        ccxt.gateio    ,ccxt.huobipro            ,ccxt.kucoin   ,ccxt.mixcoins   ,ccxt.tidex         ,ccxt.yobit,
        ccxt.anxpro    ,ccxt.bitfinex2    ,ccxt.bitso      ,ccxt.btcchina     ,ccxt.bxinth      ,ccxt.coingi         ,ccxt.exmo,
        ccxt.gdax      ,ccxt.huobi               ,ccxt.kuna     ,ccxt.nova       ,ccxt.qryptos     ,ccxt.urdubit       ,ccxt.yunbi,
        ccxt.bitfinex     ,ccxt.bitstamp1  ,ccxt.btcexchange  ,ccxt.ccex        ,ccxt.coinmarketcap  ,ccxt.flowbtc,
        ccxt.gemini    ,ccxt.independentreserve  ,ccxt.lakebtc  ,ccxt.okcoincny  ,ccxt.quadrigacx  ,ccxt.vaultoro      ,ccxt.zaif,
        ccxt.bitflyer     ,ccxt.bitstamp   ,ccxt.btcmarkets   ,ccxt.cex
    ]

    for exchange in all_exchanges:
        obj = exchange()
        try:
            obj.fetch_tickers()
            print(obj)
        except BaseException:
            pass
    exit(0)
    pp = PrettyPrinter()
    pprint = pp.pprint

    bit2 = bitfinex2()
    bit2.load_markets()
    pprint(bit2.get_tickers()["ETH/BTC"]["info"])

    bin = binance()
    bin.load_markets()
    pprint(bin.get_tickers()["ETH/BTC"]["info"])


