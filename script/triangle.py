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
        tree_markets[base_market].append({
            'market': quote_market,
            'price': float(ticker["bidPrice"]),
            'qty': float(ticker["bidQty"])
        })

        tree_markets[quote_market].append({
            'market': base_market,
            'price': 1.0 / float(ticker["askPrice"]),
            'qty': float(ticker["askQty"])
        })

    # build tree
    # item in frontier are dictionary of path, price of transition and quantity
    frontier = deque([{
        'path': [base_currency],
        'price': [],
        'qty': []
    }])
    max_depth = 5
    valid_path = []

    while len(frontier):
        current_node = frontier.popleft()
        path = current_node['path']
        transition_price = current_node['price']
        transition_quantity = current_node['qty']

        if len(path) > 2 and path[-1] == base_currency:
            valid_path.append(current_node)
        if len(path) >= max_depth:
            continue
        node = path[-1]
        for child_market in tree_markets[node]:
            children = child_market['market']
            price = child_market['price']
            quantity = child_market['qty']

            frontier.append({
                'path': path + [children],
                'price': transition_price + [price],
                'qty': transition_quantity + [quantity]
            })

    tree = Digraph()
    node_count = 0

    # TODO: deal with the BNB discount
    find_path_cost = lambda path_obj: reduce(lambda cost, x: cost * x * 0.9995, path_obj['price'], 1.0)
    valid_path = list(filter(lambda path_obj: find_path_cost(path_obj) > 1.0, valid_path))
    valid_path = sorted(valid_path, key=lambda path_obj: find_path_cost(path_obj), reverse=True)

    for path_obj in valid_path:
        path = path_obj['path']
        transition_price = path_obj['price']
        transition_quantity = path_obj['qty']

        path_cost = find_path_cost(path_obj)

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
        find_arbitrage_binance('ETH')
        time.sleep(1)

if __name__ == "__main__":
    main()