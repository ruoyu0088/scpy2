# -*- coding: utf-8 -*-
from os import path
from collections import defaultdict
from itertools import product
import cPickle
import time

FOLDER = path.dirname(__file__)

W, H = 4, 5

Positions = list(product(range(H), range(W)))

Blocks = {
    "A": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "B": [(0, 0), (1, 0)],
    "C": [(0, 0), (0, 1)],
    "D": [(0, 0)],
}

BlockSizes = {key: (blocks[-1][0] + 1, blocks[-1][1] + 1) for key, blocks in Blocks.items()}

D = 1, 0
U = -1, 0
R = 0, 1
L = 0, -1

Direct = {
    "D": D,
    "U": U,
    "R": R,
    "L": L,
}

Moves = {
    "A": {"D": [(2, 0), (2, 1)],
          "U": [(-1, 0), (-1, 1)],
          "R": [(0, 2), (1, 2)],
          "L": [(0, -1), (1, -1)]},

    "B": {"D": [(2, 0)],
          "U": [(-1, 0)],
          "DD": [(2, 0), (3, 0)],
          "UU": [(-1, 0), (-2, 0)],
          "R": [(0, 1), (1, 1)],
          "L": [(0, -1), (1, -1)]},

    "C": {"D": [(1, 0), (1, 1)],
          "U": [(-1, 0), (-1, 1)],
          "R": [(0, 2)],
          "L": [(0, -1)],
          "RR": [(0, 2), (0, 3)],
          "LL": [(0, -1), (0, -2)]},

    "D": {"D": [(1, 0)],
          "DD": [(1, 0), (2, 0)],
          "U": [(-1, 0)],
          "UU": [(-1, 0), (-2, 0)],
          "R": [(0, 1)],
          "RR": [(0, 1), (0, 2)],
          "L": [(0, -1)],
          "LL": [(0, -1), (0, -2)],
          "DL": [(1, 0), (1, -1)],
          "DR": [(1, 0), (1, 1)],
          "UL": [(-1, 0), (-1, -1)],
          "UR": [(-1, 0), (-1, 1)],
          "LD": [(0, -1), (1, -1)],
          "LU": [(0, -1), (-1, -1)],
          "RD": [(0, 1), (1, 1)],
          "RU": [(0, 1), (-1, 1)]}
}


def compress_node(node):
    cells = node[0]
    return "".join([cells[pos] if cells[pos] is not None else " " for pos in Positions])


def find_all_nodes(blocks):
    nodes = []
    positions = []
    cells = {pos: None for pos in Positions}
    last_positions = defaultdict(list)

    for block in Blocks:
        last_positions[block].append((-1, -1))

    def is_empty(name, r, c):
        return all(cells[r + r2, c + c2] is None for r2, c2 in Blocks[name])

    def set_cells(name, r, c, value):
        for r2, c2 in Blocks[name]:
            cells[r + r2, c + c2] = value

    def solve(blocks):
        if not blocks:
            nodes.append((cells.copy(), positions[:]))
            return

        block = blocks[0]
        h, w = BlockSizes[block]
        empty_positions = []
        last_pos = last_positions[block][-1]

        for pos in Positions:
            r, c = pos
            if cells[pos] is None and r <= H - h and c <= W - w and pos > last_pos:
                empty_positions.append(pos)

        for pos in empty_positions:
            r, c = pos
            if is_empty(block, r, c):
                set_cells(block, r, c, block)
                positions.append(pos)
                last_positions[block].append(pos)

                solve(blocks[1:])

                set_cells(block, r, c, None)
                last_positions[block].pop()
                positions.pop()

    solve(blocks)
    return nodes


def get_moves(node, blocks):
    _Moves = Moves
    block_moves = [_Moves[c] for c in blocks]
    cells, positions = node
    empty = {key for key, value in cells.iteritems() if value is None}
    possible_pos = set()
    for r, c in empty:
        for dr, dc in Direct.itervalues():
            possible_pos.add((r + dr, c + dc))
            possible_pos.add((r + dr * 2, c + dc * 2))

    for i in xrange(len(positions)):
        pos = positions[i]
        if pos not in possible_pos:
            continue
        r, c = pos
        moves = block_moves[i]
        for move, offsets in moves.iteritems():
            if empty.issuperset([(r + r2, c + c2) for (r2, c2) in offsets]):
                yield pos, move


def get_neighbour(node, move):
    cells, positions = node
    cells = cells.copy()
    pos, direct = move
    name = cells[pos]
    r, c = pos
    from_pos = [(r + r2, c + c2) for r2, c2 in Blocks[name]]

    dr = dc = 0
    for cmd in direct:
        dr2, dc2 = Direct[cmd]
        dr += dr2
        dc += dc2

    to_pos = [(r + dr, c + dc) for r, c in from_pos]
    for key in from_pos:
        cells[key] = None
    for key in to_pos:
        cells[key] = name
    return compress_node((cells, None))


def is_solved_node(cnode):
    return cnode[13:15] == "AA" and cnode[17:19] == "AA"


def cnode_str(cnode):
    return "\n".join(cnode[i * W:i * W + W] for i in range(H))


def dump_graph(blocks):
    nodes = find_all_nodes(blocks)
    compressed_nodes = [compress_node(node) for node in nodes]
    node_ids = {node: i for i, node in enumerate(compressed_nodes)}

    edges = []
    moves = []
    for i, node in enumerate(nodes):
        for move in get_moves(node, blocks):
            edge = i, node_ids[get_neighbour(node, move)]
            edges.append(edge)
            moves.append(move)

    fn = path.join(FOLDER, "%s.pickle" % blocks)
    with file(fn, "wb") as f:
        cPickle.dump({"nodes": compressed_nodes, "edges": edges}, f)

    print fn, "saved"


def load_graph(blocks):
    full_path = path.join(FOLDER, "%s.pickle" % blocks)
    if path.exists(full_path):
        with file(full_path, "rb") as f:
            return cPickle.load(f)
    else:
        raise IOError("graph %s not found" % blocks)


def create_graphs():
    for i in range(1, 5):
        blocks = "A" + "B" * i + "C" * (5 - i) + "D"*4
        dump_graph(blocks)

graph_cache = {}

def find_path(start_node):
    import numpy as np
    from scipy import sparse
    from scipy.sparse import csgraph
    from collections import Counter

    counts = Counter(start_node)
    blocks = ("A" * (counts["A"] // 4) + "B" * (counts["B"] // 2) +
              "C" * (counts["C"] // 2) + "D" * counts["D"])

    if blocks not in graph_cache:
        graph = load_graph(blocks)
        graph_cache[blocks] = graph
    else:
        graph = graph_cache[blocks]

    cnodes = graph["nodes"]

    mask = np.array([is_solved_node(cnode) for cnode in cnodes], bool)
    edges = np.array(graph["edges"])
    data = np.ones(len(edges))
    m = sparse.coo_matrix((data, (edges[:, 0], edges[:, 1])))
    start_idx = cnodes.index(start_node)
    dist, predecessors = csgraph.dijkstra(m, True, indices=[start_idx], return_predecessors=True)
    dist = dist[0]
    predecessors = predecessors[0]
    dist[~mask] = np.inf
    end_idx = np.argmin(dist)

    path = []
    p = end_idx
    while p != start_idx:
        path.append(p)
        p = predecessors[p]
    path.append(start_idx)

    path = path[::-1]

    for n1, n2 in zip(path[:-1], path[1:]):
        yield cnodes[n2]


if __name__ == '__main__':
    import sys
    dump_graph(sys.argv[1])
