import ccxt
from graphviz import Digraph
from collections import deque
from pprint import PrettyPrinter
from functools import reduce
import time


def find_arbitrage_binance():
    pp = PrettyPrinter()
    pprint = pp.pprint

    bin = ccxt.binance()
    bin.load_markets()
    all_markets = bin.markets

    tree_markets = {}
    all_tickers = bin.public_get_ticker_allbooktickers()
    all_tickers = {i['symbol']: i for i in all_tickers}

    for markets in all_markets:
        market1, market2 = tuple(markets.split("/"))
        market1 = market1 if market1 != "BCH" else "BCC"
        market2 = market2 if market2 != "BCH" else "BCC"
        if market1 not in tree_markets:
            tree_markets[market1] = []
        if market2 not in tree_markets:
            tree_markets[market2] = []

        symbol1 = market1 + market2
        symbol2 = market2 + market1
        ticker = all_tickers[symbol1] if symbol1 in all_tickers else all_tickers[symbol2]
        if float(ticker["askPrice"]) == 0 or float(ticker["bidPrice"]) == 0:
            continue
        pprint(ticker)
        tree_markets[market1].append((market2, float(ticker["bidPrice"])))
        tree_markets[market2].append((market1, 1.0 / float(ticker["askPrice"])))

    # build tree
    # item in frontier are tuple of path and price of transition
    frontier = deque([(['USDT'],[])])
    depth_idx = 1
    explored_nodes = {}
    max_depth = 5


    valid_path = []

    while len(frontier):
        path, transition_price = frontier.popleft()
        if len(path) > 2 and path[-1] == "USDT":
            valid_path.append((path, transition_price))
        if len(path) >= max_depth:
            continue
        node = path[-1]
        for children, price in tree_markets[node]:
            frontier.append((path + [children], transition_price + [price]))

    tree = Digraph()
    node_count = 0
    for path, transition_price in valid_path:
        path_cost = reduce(lambda cost, x: cost * x * 0.999, transition_price, 1.0)
        if path_cost < 1.0:
            continue

        tree.node(str(node_count), path[0])
        node_count += 1
        for i in range(1, len(path)):
            tree.node(str(node_count), path[i])
            tree.edge(str(node_count - 1), str(node_count), str(transition_price[i - 1]))
            node_count += 1
            # TODO: deduce transaction fee and consider minimum quantity

        tree.node(str(node_count), str(path_cost))
        tree.edge(str(node_count-1), str(node_count))
        node_count += 1
    tree.render('tmp', '/tmp', view=True)

def find_arbitrage_bitfinex():
    pp = PrettyPrinter()
    pprint = pp.pprint

    bin = ccxt.bitfinex()
    bin.load_markets()
    all_markets = bin.markets

    tree_markets = {}
    all_tickers = bin.public_get_ticker_allbooktickers()
    all_tickers = {i['symbol']: i for i in all_tickers}

    for markets in all_markets:
        market1, market2 = tuple(markets.split("/"))
        market1 = market1 if market1 != "BCH" else "BCC"
        market2 = market2 if market2 != "BCH" else "BCC"
        if market1 not in tree_markets:
            tree_markets[market1] = []
        if market2 not in tree_markets:
            tree_markets[market2] = []

        symbol1 = market1 + market2
        symbol2 = market2 + market1
        ticker = all_tickers[symbol1] if symbol1 in all_tickers else all_tickers[symbol2]
        if float(ticker["askPrice"]) == 0 or float(ticker["bidPrice"]) == 0:
            continue
        pprint(ticker)
        tree_markets[market1].append((market2, float(ticker["bidPrice"])))
        tree_markets[market2].append((market1, 1.0 / float(ticker["askPrice"])))

    # build tree
    # item in frontier are tuple of path and price of transition
    frontier = deque([(['USDT'],[])])
    depth_idx = 1
    explored_nodes = {}
    max_depth = 5


    valid_path = []

    while len(frontier):
        path, transition_price = frontier.popleft()
        if len(path) > 2 and path[-1] == "USDT":
            valid_path.append((path, transition_price))
        if len(path) >= max_depth:
            continue
        node = path[-1]
        for children, price in tree_markets[node]:
            frontier.append((path + [children], transition_price + [price]))

    tree = Digraph()
    node_count = 0
    for path, transition_price in valid_path:
        path_cost = reduce(lambda cost, x: cost * x * 0.999, transition_price, 1.0)
        if path_cost < 1.0:
            continue

        tree.node(str(node_count), path[0])
        node_count += 1
        for i in range(1, len(path)):
            tree.node(str(node_count), path[i])
            tree.edge(str(node_count - 1), str(node_count), str(transition_price[i - 1]))
            node_count += 1
            # TODO: deduce transaction fee and consider minimum quantity

        tree.node(str(node_count), str(path_cost))
        tree.edge(str(node_count-1), str(node_count))
        node_count += 1
    tree.render('tmp', '/tmp', view=True)


def main():
    while True:
        find_arbitrage_binance()
        time.sleep(1)

if __name__ == "__main__":
    main()