import ccxt
from graphviz import Digraph
from collections import deque
from pprint import PrettyPrinter
from functools import reduce
import time
import math

def calculate_final_value(path_obj, bottleneck):
    value = math.floor(bottleneck / path_obj['step_size'][0]) * path_obj['step_size'][0]
    path_obj['raw_values'] = [bottleneck]
    path_obj['rounded_values'] = [value]

    for i in range(len(path_obj['price'])):
        value = path_obj['price'][i] * value * 0.9995
        path_obj['raw_values'].append(value)
        if (i < len(path_obj['price'])-1):
            value = math.floor(value / path_obj['step_size'][i+1]) * path_obj['step_size'][i+1]
        path_obj['rounded_values'].append(value)
    return value

def check_limits(path_obj, bottleneck):
    value = bottleneck
    for i in range(0, len(path_obj['price'])-1):
        if (value < path_obj['step_size'][i]):
            return False
        value = path_obj['price'][i] * value
    return True

def find_bottleneck(path_obj, max_investment):
    din = 1.
    bottleneck = float('inf')
    for i in range(0, len(path_obj['qty'])):
        bottleneck = min(bottleneck, path_obj['qty'][i] / din)
        din *= path_obj['price'][i]

    bottleneck = min(bottleneck, max_investment)

    return bottleneck

def find_arbitrage_binance(base_currency="USDT", max_investment=0.00):
    pp = PrettyPrinter()
    pprint = pp.pprint

    bin = ccxt.binance()
    all_markets = bin.load_markets()
    bit = ccxt.bitfinex2()
    bit.load_markets()
    bit.fetch_tickers()
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
            'qty': float(ticker["bidQty"]),
            'step_size': float(all_markets[markets]["limits"]["amount"]["min"])
        })

        tree_markets[quote_market].append({
            'market': base_market,
            'price': 1.0 / float(ticker["askPrice"]),
            'qty': float(ticker["askQty"]) * float(ticker["askPrice"]),
            'step_size': float(all_markets[markets]["limits"]["amount"]["min"]) * float(ticker["askPrice"])
        })

    # build tree
    # item in frontier are dictionary of path, price of transition and quantity
    frontier = deque([{
        'path': [base_currency],
        'price': [],
        'qty': [],
        'step_size': []
    }])
    max_depth = 5
    valid_path = []

    find_path_cost = lambda path_obj: reduce(lambda cost, x: cost * x * 0.9995, path_obj['price'], 1.0)

    while len(frontier):
        current_node = frontier.popleft()
        path = current_node['path']
        step_sizes = current_node['step_size']
        transition_price = current_node['price']
        transition_quantity = current_node['qty']

        if len(path) > 2 and path[-1] == base_currency:
            path_cost = find_path_cost(current_node)
            if (path_cost < 1.000):
                continue

            investment = find_bottleneck(current_node, max_investment)
            if (check_limits(current_node, investment) == False):
                # print("less than bottleneck %f" % investment)
                continue

            final_value = calculate_final_value(current_node, investment)
            profit = (final_value - investment)
            current_node['path_cost'] = path_cost
            current_node['investment'] = investment
            current_node['final_value'] = final_value
            current_node['profit'] = profit
            current_node['profit_percent'] = profit / investment
            valid_path.append(current_node)
        if len(path) >= max_depth:
            continue
        node = path[-1]
        for child_market in tree_markets[node]:
            children = child_market['market']
            price = child_market['price']
            quantity = child_market['qty']
            step_size = child_market['step_size']

            frontier.append({
                'path': path + [children],
                'price': transition_price + [price],
                'qty': transition_quantity + [quantity],
                'step_size': step_sizes + [step_size]
            })

    tree = Digraph()
    node_count = 0

    # TODO: deal with the BNB discount
    # valid_path = list(filter(lambda path_obj: find_path_cost(path_obj) > 1.000, valid_path))
    valid_path = sorted(valid_path, key=lambda path_obj: (path_obj['profit']), reverse=True)
    if (len(valid_path) == 0):
        return

    for path_obj in valid_path:
        path = path_obj['path']
        transition_price = path_obj['price']
        transition_quantity = path_obj['qty']
        transition_step_size = path_obj['step_size']

        tree.node(str(node_count), str(path_obj['investment']))

        node_count += 1

        tree.node(str(node_count), path[0]+" %.5g"%(path_obj['raw_values'][0])+" %.5g"%(path_obj['rounded_values'][0]))
        tree.edge(str(node_count - 1), str(node_count))
        node_count += 1
        for i in range(1, len(path)):
            tree.node(str(node_count), path[i]+" %.5g"%(path_obj['raw_values'][i])+" %.5g"%(path_obj['rounded_values'][i]))
            tree.edge(
                str(node_count - 1),
                str(node_count),
                "%.3g"%(transition_price[i - 1])
                +", lim: "
                +"%.3g"%(transition_quantity[i - 1])
                +", step:"
                +"%.5g"%(transition_step_size[i-1])
            )
            node_count += 1

        tree.node(str(node_count), "%.6g"%(path_obj['path_cost']))
        tree.edge(str(node_count-1), str(node_count), "proportion")

        node_count += 1

        tree.node(str(node_count), "%.6g"%(path_obj['final_value']))
        tree.edge(str(node_count - 2), str(node_count), "final")

        node_count += 1

        tree.node(str(node_count), "%.6g"%(path_obj['profit']))
        tree.edge(str(node_count - 3), str(node_count), "profit")

        node_count += 1
        break # Get the best option

    tree.render('tmp', '/tmp', view=True)
    pprint(valid_path)

def main():
    while True:
        find_arbitrage_binance('USDT', 50.)
        time.sleep(1)

if __name__ == "__main__":
    main()