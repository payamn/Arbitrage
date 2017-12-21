import ccxt
from graphviz import Digraph
from collections import deque
bin = ccxt.binance()
bin.load_markets()
all_markets = bin.markets

tree_markets = {}
for markets in all_markets:
    market1, market2 = tuple(markets.split("/"))
    if market1 not in tree_markets:
        tree_markets[market1] = []
    if market2 not in tree_markets:
        tree_markets[market2] = []

    tree_markets[market1].append(market2)
    tree_markets[market2].append(market1)

# build tree
frontier = deque(['USDT'])
depth_idx = 1
explored_nodes = {}
max_depth = 3

tree = Digraph()
tree.node('USDT', 'USDT')

while depth_idx < max_depth:
    new_frontier = deque()
    depth_idx += 1
    while len(frontier):
        node = frontier.popleft()
        explored_nodes[node] = True
        children = tree_markets[node]

        for child in children:
            if child not in explored_nodes:
                new_frontier.append(child)
                tree.node(child, child)
            tree.edge(node, child)
            if len(new_frontier) > 5:
                break
    frontier = new_frontier

tree.render('tmp', '/tmp', view=True)
