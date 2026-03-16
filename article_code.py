from collections import defaultdict

undefined = None

n = 0
nodes = []
ancestor = {}
weight = {}
count = {}
D_father = {}
A_children = defaultdict(list)

def flog(x):
    if x <= 0:
        return 0
    return x.bit_length() - 1


def root_D(u):
    while D_father[u] != u:
        u = D_father[u]
    return u

def initialize_online(nodes_):
    global n, nodes, ancestor, weight, count, high, D_father, A_children, T_children, V_father, V_children, OBJ, REM, LCA, number_of, node_of
    nodes = list(nodes_)
    n = len(nodes)
    ancestor = {u: {0: undefined} for u in nodes}
    weight = {u: 0 for u in nodes}
    count = {u: 1 for u in nodes}
    high = {}
    D_father = {u: u for u in nodes}
    A_children = defaultdict(list)
    T_children = defaultdict(list)
    V_father = {}
    V_children = defaultdict(list)
    OBJ = defaultdict(list)
    REM = defaultdict(list)
    LCA = {}
    number_of = {}
    node_of = {}


def depth(u):
    path = []
    x = u
    while True:
        path.append(x)
        if D_father[x] == x:
            break
        x = D_father[x]
    path.reverse()
    d = sum(weight[u_i] for u_i in path)
    u_0 = path[0]
    for i in range(2, len(path)):
        u_i = path[i]
        u_i_1 = path[i - 1]
        D_father[u_i] = u_0
        weight[u_i] = weight[u_i] + weight[u_i_1]
    return d


def merge(u, v):
    depth_u = depth(u)
    depth_v = depth(v)
    x = root_D(u)
    y = root_D(v)
    if count[x] <= count[y]:
        D_father[x] = y
        count[y] = count[y] + count[x]
        weight[x] = weight[x] + depth_v + 1 - weight[y]
    else:
        D_father[y] = x
        count[x] = count[y] + count[x]
        weight[x] = weight[x] + depth_v + 1
        weight[y] = weight[y] - weight[x]
    return depth_u, depth_v


def getancestor(u, i):
    if u is undefined:
        return undefined
    ancestor.setdefault(u, {})
    if i in ancestor[u]:
        return ancestor[u][i]
    if i == 0:
        ancestor[u][0] = ancestor[u].get(0, undefined)
        return ancestor[u][0]
    if i - 1 not in ancestor[u]:
        ancestor[u][i - 1] = getancestor(u, i - 1)
    if ancestor[u][i - 1] is undefined:
        ancestor[u][i] = undefined
    else:
        ancestor[u][i] = getancestor(getancestor(u, i - 1), i - 1)
    return ancestor[u][i]


def find(u, v, i, d):
    if i == 0:
        return getancestor(u, 0)
    if getancestor(u, i - 1) == getancestor(v, i - 1):
        return find(u, v, i - 1, d)
    d = d - (1 << (i - 1))
    j = min(i - 1, flog(d)) if d > 0 else 0
    return find(getancestor(u, i - 1), getancestor(v, i - 1), j, d)


def lowest(u, v):
    depth_u = depth(u)
    depth_v = depth(v)
    if root_D(u) != root_D(v):
        return "unrelated"
    if depth_u < depth_v:
        u, v = v, u
        depth_u, depth_v = depth_v, depth_u
    a = u
    d = depth_u - depth_v
    while d > 0:
        j = flog(d)
        a = getancestor(a, j)
        d = d - (1 << j)
    if a == v:
        return a
    return find(a, v, flog(depth_v), depth_v)


def Algorithm_1(G, nodes_):
    initialize_online(nodes_)
    output = []
    for sigma_i in G:
        if sigma_i[0] == "lca":
            _, u, v = sigma_i
            output.append(lowest(u, v))
        elif sigma_i[0] == "link":
            _, u, v = sigma_i
            ancestor[u][0] = v
            A_children[v].append(u)
            merge(u, v)
    return output

G = [("link", 2, 1), ("lca", 3, 4), ("link", 3, 2), ("link", 4, 1), ("lca", 3, 4)]
print(Algorithm_1(G, [1, 2, 3, 4]))