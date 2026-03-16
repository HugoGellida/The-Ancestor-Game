from collections import defaultdict, deque

undefined = None

n = 0
nodes = []
ancestor = {}
weight = {}
count = {}
high = {}
D_father = {}
A_children = defaultdict(list)
T_children = defaultdict(list)
V_father = {}
V_children = defaultdict(list)
OBJ = defaultdict(list)
REM = defaultdict(list)
LCA = {}
number_of = {}
node_of = {}


def L(X):
    return X[0]


def R(X):
    return X[1]


def flog(x):
    if x <= 0:
        return 0
    return x.bit_length() - 1


def front(Q):
    return Q[0]


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


def build_forest_from_links(G):
    global T_children
    T_children = defaultdict(list)
    parent = {}
    all_nodes = set()
    for sigma_i in G:
        if sigma_i[0] == "link":
            _, u, v = sigma_i
            parent[u] = v
            T_children[v].append(u)
            all_nodes.add(u)
            all_nodes.add(v)
        elif sigma_i[0] == "lca":
            _, u, v = sigma_i
            all_nodes.add(u)
            all_nodes.add(v)
    roots = [u for u in all_nodes if u not in parent]
    if len(roots) == 1:
        return roots[0], all_nodes, parent
    root = "unrelated"
    while root in all_nodes:
        root = (root, len(all_nodes))
    for u in roots:
        T_children[root].append(u)
        parent[u] = root
    all_nodes.add(root)
    return root, all_nodes, parent


def preorder_tree(root, children):
    global number_of, node_of, count, high
    order = []

    def dfs(u):
        order.append(u)
        for v in children.get(u, []):
            dfs(v)

    dfs(root)
    number_of = {u: i + 1 for i, u in enumerate(order)}
    node_of = {i + 1: u for i, u in enumerate(order)}
    numbered_children = defaultdict(list)
    for u in order:
        numbered_children[number_of[u]] = [number_of[v] for v in children.get(u, [])]
    count = {}
    high = {}

    def dfs2(i):
        c = 1
        h = i
        for j in numbered_children.get(i, []):
            c_j, h_j = dfs2(j)
            c += c_j
            if h_j > h:
                h = h_j
        count[i] = c
        high[i] = h
        return c, h

    dfs2(number_of[root])
    return number_of[root], numbered_children


def postorder_nodes(root, children):
    out = []

    def dfs(u):
        for v in children.get(u, []):
            dfs(v)
        out.append(u)

    dfs(root)
    return out


def Algorithm_2(root, children, objects):
    by_R = defaultdict(list)
    for X in objects:
        by_R[R(X)].append(X)
    B = []
    for i in postorder_nodes(root, children):
        for X in by_R[i]:
            B.append(("enter", X))
        B.append(("remove", i))
    return B


def Algorithm_3(B, k, objects):
    global OBJ, REM
    OBJ = defaultdict(list)
    REM = defaultdict(list)
    for X in objects:
        OBJ[L(X)].append(X)
    remove_order = [i for op, i in B if op == "remove"]
    next_remove = {}
    for t in range(len(remove_order) - 1):
        next_remove[remove_order[t]] = remove_order[t + 1]
    S = {i: set() for i in remove_order}
    owner = {}
    for X in objects:
        e_X = ("e", X)
        j = R(X)
        S[j].add(e_X)
        owner[e_X] = j
    for i, j in next_remove.items():
        r_i = ("r", i)
        S[j].add(r_i)
        owner[r_i] = j

    def merge_sets(j, h):
        if j == h:
            return h
        for atom in list(S[j]):
            S[h].add(atom)
            owner[atom] = h
        del S[j]
        return h

    for i in range(k, 0, -1):
        for X in OBJ.get(i, []):
            j = owner[("e", X)]
            while True:
                if i >= j:
                    REM[j].append(X)
                    break
                h = owner[("r", j)]
                merge_sets(j, h)
                j = h
    output = []
    for op, i in B:
        if op == "remove":
            for X in REM.get(i, []):
                output.append((X, i))
    return output


def remove_unrelated_offline(G):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        x = find(x)
        y = find(y)
        if x != y:
            parent[x] = y

    output = {}
    for sigma_i in G:
        if sigma_i[0] == "link":
            _, u, v = sigma_i
            union(u, v)
        elif sigma_i[0] == "lca":
            _, u, v = sigma_i
            find(u)
            find(v)
    G2 = []
    for t, sigma_i in enumerate(G):
        if sigma_i[0] == "lca":
            _, u, v = sigma_i
            if find(u) != find(v):
                output[t] = "unrelated"
            else:
                G2.append((t, sigma_i))
        else:
            G2.append((t, sigma_i))
    return G2, output


def Algorithm_4(G):
    global LCA
    G2, output = remove_unrelated_offline(G)
    root, _, _ = build_forest_from_links([sigma_i for _, sigma_i in G2])
    root, numbered_children = preorder_tree(root, T_children)
    objects = []
    instruction_to_object = {}
    for t, sigma_i in G2:
        if sigma_i[0] == "lca":
            _, u, v = sigma_i
            i = number_of[u]
            j = number_of[v]
            if i > j:
                i, j = j, i
            X = (i, j, t)
            objects.append(X)
            instruction_to_object[t] = X
    B = Algorithm_2(root, numbered_children, objects)
    output_3 = Algorithm_3(B, len(number_of), objects)
    LCA = {}
    for X, i in output_3:
        LCA[X] = node_of[i]
    answers = {}
    for t, sigma_i in enumerate(G):
        if sigma_i[0] == "lca":
            if t in output:
                answers[t] = output[t]
            else:
                answers[t] = LCA[instruction_to_object[t]]
    return answers


def build(u):
    global V_father
    path = [u]
    while T_children.get(path[-1], []):
        u_i = path[-1]
        u_i_1 = max(T_children[u_i], key=lambda v: count[v])
        path.append(u_i_1)
    Q = deque([path[-1]])
    for p in range(len(path) - 2, -1, -1):
        u_i = path[p]
        while Q and count[u_i] >= 2 * count[front(Q)]:
            V_father[front(Q)] = u_i
            Q.popleft()
        Q.append(u_i)
    for p in range(len(path) - 1):
        u_i = path[p]
        u_i_1 = path[p + 1]
        for v in T_children.get(u_i, []):
            if v != u_i_1:
                R_ = build(v)
                for w in R_:
                    V_father[w] = u_i
    return Q


def Algorithm_5(u_0):
    global V_father
    V_father = {u_0: undefined}
    Q = build(u_0)
    for v in list(Q):
        if v != u_0:
            V_father[v] = u_0
    return V_father


def is_descendant(i, j):
    return j <= i and high[j] >= high[i]


def locate(u, v, i, j):
    if count[u] > count[v]:
        u, v, i, j = v, u, j, i
    if i == 0:
        return getancestor(u, 0)
    a = getancestor(u, i - 1)
    if v == a:
        return a
    if (a is undefined) or (v < a or high[v] > high[a]):
        return locate(u, v, i - 1, j)
    return locate(a, v, i - 1, j)


def Algorithm_6(G):
    parent = {}
    children = defaultdict(list)
    all_nodes = set()
    prepared = False
    answers = []
    k = None
    for sigma_i in G:
        if sigma_i[0] == "link":
            _, u, v = sigma_i
            parent[u] = v
            children[v].append(u)
            all_nodes.add(u)
            all_nodes.add(v)
        elif sigma_i[0] == "lca":
            if not prepared:
                roots = [u for u in all_nodes if u not in parent]
                root = "unrelated"
                while root in all_nodes:
                    root = (root, len(all_nodes))
                for u in roots:
                    children[root].append(u)
                all_nodes.add(root)
                numbered_root, numbered_children = preorder_tree(root, children)
                global T_children, ancestor
                T_children = numbered_children
                Algorithm_5(numbered_root)
                ancestor = {u: {0: V_father.get(u, undefined)} for u in numbered_children}
                k = flog(1 + flog(len(numbered_children)))
                for u in numbered_children:
                    for i in range(0, k + 1):
                        getancestor(u, i)
                prepared = True
            _, u, v = sigma_i
            u = number_of[u]
            v = number_of[v]
            if is_descendant(u, v):
                answers.append(node_of[v])
            elif is_descendant(v, u):
                answers.append(node_of[u])
            else:
                answers.append(node_of[locate(u, v, k, k)])
    return answers


def reduce_graph_13(N, E, u_0):
    raise NotImplementedError


def Algorithm_7(N, E, u_0, consumptions=None):
    if consumptions is None:
        consumptions = reduce_graph_13(N, E, u_0)
    initialize_online(N)
    predecessors = defaultdict(list)
    for x, y in E:
        predecessors[y].append(x)
    for u_0, U in consumptions:
        k = len(U)
        if k == 1:
            ancestor[u_0][0] = U[0]
            A_children[U[0]].append(u_0)
            merge(u_0, U[0])
        else:
            v_1 = lowest(U[0], U[1])
            v_i_1 = v_1
            for i in range(2, k):
                v_i = lowest(v_i_1, U[i])
                v_i_1 = v_i
            ancestor[u_0][0] = v_i_1
            A_children[v_i_1].append(u_0)
            merge(u_0, v_i_1)
    return {u: ancestor[u][0] for u in ancestor if ancestor[u][0] is not undefined}