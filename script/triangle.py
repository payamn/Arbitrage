import ccxt
from graphviz import Digraph
from collections import deque
from pprint import PrettyPrinter
from functools import reduce
import time


def find_arbitrage_binance(base_currency="USDT"):
    pp = PrettyPrinter()
    pprint = pp.pprint

    bin = ccxt.binance()
    all_markets = bin.load_markets()
    # all_markets = bin.markets

    tree_markets = {}
    all_tickers = bin.public_get_ticker_allbooktickers()
    all_tickers = {i['symbol']: i for i in all_tickers}

    for markets in all_markets:
        base_market = all_markets[markets]['base']
        quote_market = all_markets[markets]['quote']

        if base_market not in tree_markets:
            tree_markets[base_market] = []
        if quote_market not in tree_markets:
            tree_markets[quote_market] = []

        ticker = all_tickers[all_markets[markets]['id']]
        if float(ticker["askPrice"]) == 0 or float(ticker["bidPrice"]) == 0:
            continue
        pprint(ticker)
        tree_markets[base_market].append((
            quote_market, float(ticker["bidPrice"]), float(ticker["bidQty"])
        ))
        tree_markets[quote_market].append((
            base_market, 1.0 / float(ticker["askPrice"]), float(ticker["askQty"])
        ))

    # build tree
    # item in frontier are tuple of path, price of transition and quantity
    frontier = deque([([base_currency],[], [])])
    max_depth = 5
    valid_path = []

    while len(frontier):
        path, transition_price, transition_quantity = frontier.popleft()
        if len(path) > 2 and path[-1] == base_currency:
            valid_path.append((path, transition_price, transition_quantity))
        if len(path) >= max_depth:
            continue
        node = path[-1]
        for children, price, quantity in tree_markets[node]:
            frontier.append((path + [children], transition_price + [price], transition_quantity + [quantity]))

    tree = Digraph()
    node_count = 0

    for path, transition_price, transition_quantity in valid_path:
        path_cost = reduce(lambda cost, x: cost * x * 0.999, transition_price, 1.0)
        if path_cost < 1.0:
            continue
        tree.node(str(node_count), path[0])
        node_count += 1
        for i in range(1, len(path)):
            tree.node(str(node_count), path[i])
            tree.edge(
                str(node_count - 1),
                str(node_count),
                "%.3g"%(transition_price[i - 1])
                +","
                +"%.3g"%(transition_quantity[i - 1])
            )
            node_count += 1

        tree.node(str(node_count), str(path_cost))
        tree.edge(str(node_count-1), str(node_count))
        node_count += 1
    tree.render('tmp', '/tmp', view=True)

def main():
    while True:
        find_arbitrage_binance('USDT')
        time.sleep(1)

if __name__ == "__main__":
    main()