import math
import random
import time
import numpy

from graph import Graph
from names import *


def dist(a, b):
    """
    Calcula la distancia entre los puntos a y b
    :param a:
    :param b:
    :return:
    """
    return math.sqrt(
        (a.attr[X_ATTR] - b.attr[X_ATTR]) ** 2 + (a.attr[Y_ATTR] - b.attr[Y_ATTR]) ** 2)


def randomArray(size):
    """
    Genera un arreglo que contiene los números del 0 a size-1 pero en órden aleatorio
    :param size: tamaño de la lista
    :return: lista con los números aleatorios
    """
    k = size
    numeros = []
    resultado = []

    for i in range(size):
        numeros.append(i)
        resultado.append(i)

    for i in range(size):
        res = random.randint(0, k - 1)
        resultado[i] = numeros[res]
        numeros[res] = numeros[k - 1]
        k -= 1

    return resultado


def randomErdos(n, m):
    """
    Genera grafo aleatorio con el método de Erdos
    :param n: número de nodos
    :param m: número de aristas
    :return: grafo generado
    """
    g = Graph()

    for i in range(n):
        g.addNode(NNAME_PREFIX + str(i))

    for i in range(m):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            g.addEdge(NNAME_PREFIX + str(u) + '->' + NNAME_PREFIX + str(v), NNAME_PREFIX + str(u),
                      NNAME_PREFIX + str(v))

    return g


def randomGilbert(n, p):
    """
    Genera grafo aleatorio con el método de Gilbert
    :param n: número de nodos
    :param p: probabilidad de generar una arista entre un par de nodos
    :return: grafo generado
    """
    g = Graph()

    for i in range(n):
        g.addNode(NNAME_PREFIX + str(i))

    for i in range(n):
        for j in range(n):
            if random.random() < p:
                if (j != i):
                    g.addEdge(NNAME_PREFIX + str(i) + '->' + NNAME_PREFIX + str(j),
                              NNAME_PREFIX + str(i),
                              NNAME_PREFIX + str(j))
    return g


def randomGeo(n, r):
    """
    Genera grafo aleatorio con el método geográfico simple
    :param n: número de nodos
    :param r: distancia máxima para generar la arista entre un par de nodos
    :return: grafo generado
    """
    g = Graph()

    # Generar n nodos con coordenadas en el espacio ((0,0),(1,1))
    for i in range(n):
        node = g.addNode(NNAME_PREFIX + str(i))
        node.attr[X_ATTR] = random.random()
        node.attr[Y_ATTR] = random.random()

    # Crear una arista entre cada par de nodos que están a distancia <= r
    for i in range(n):
        for j in range(n):
            if i != j:
                d = dist(g.getNode(NNAME_PREFIX + str(i)),
                         g.getNode(NNAME_PREFIX + str(j)))
                if d <= r:
                    g.addEdge(NNAME_PREFIX + str(i) + '->' + NNAME_PREFIX + str(j),
                              NNAME_PREFIX + str(i),
                              NNAME_PREFIX + str(j))

    return g


def randomBarabasi(n, d):
    """
    Genera grafo aleatorio con el método de Barabasi
    :param n: número de nodos
    :param d: número máximo de aristas por nodo
    :return: grafo generado
    """
    g = Graph()
    g.addNode(NNAME_PREFIX + str(0))

    for u in range(1, n):
        randomNodes = randomArray(u)
        for v in range(u):
            deg = g.getDegree(NNAME_PREFIX + str(randomNodes[v]))
            p = 1 - deg / d
            if random.random() < p:
                if randomNodes[v] != u:
                    g.addEdge(NNAME_PREFIX + str(u) + '->' + NNAME_PREFIX + str(randomNodes[v]),
                              NNAME_PREFIX + str(u), NNAME_PREFIX + str(randomNodes[v]))

    return g


def nodeName(i):
    return NNAME_PREFIX + str(i)


def edgeName(i, j):
    return nodeName(i) + '->' + nodeName(j)


def gridGraph(m, n=0, diagonals=False):
    """
    Genera un grafo de malla
    :param m: número de filas
    :param n: número de columnas
    :param diagonales: generar aristas diagonales?
    :return: None
    """
    # si no se pasa n, la malla es cuadrada de m*m
    if n == 0:
        n = m

    # por lo menos debe de ser un cuadro
    m = max(2, m)
    n = max(2, n)

    g = Graph()

    for i in range(m):
        for j in range(n):
            g.addNode(nodeName(i * n + j)
                      ).attr[ATTR_POS] = numpy.array([float(i), float(j)])
            if j < n - 1:
                g.addEdge(edgeName(i * n + j, i * n + j + 1),
                          nodeName(i * n + j),
                          nodeName(i * n + j + 1))
            if i < m - 1:
                g.addEdge(edgeName(i * n + j, (i + 1) * n + j),
                          nodeName(i * n + j),
                          nodeName((i + 1) * n + j))
            if i < m - 1 and j < n - 1 and diagonals:
                g.addEdge(edgeName(i * n + j, (i + 1) * n + j + 1),
                          nodeName(i * n + j),
                          nodeName((i + 1) * n + j + 1))
            if i > 0 and j < n - 1 and diagonals:
                g.addEdge(edgeName(i * n + j, (i - 1) * n + j + 1),
                          nodeName(i * n + j),
                          nodeName((i - 1) * n + j + 1))

    g.attr[ATTR_LAYERED] = True
    return g


def event_DorogovtsevMendes(g):
    i = len(g.nodes)
    a = g.getRandomEdge()
    g.addEdge(edgeName(i, a.n0.id), i, a.n0.id)
    g.addEdge(edgeName(i, a.n1.id), i, a.n1.id)


def DorogovtsevMendesGraph(n):
    g = Graph()

    g.addEdge(edgeName(0, 1), 0, 1)
    g.addEdge(edgeName(1, 2), 1, 2)
    g.addEdge(edgeName(2, 0), 2, 0)

    if n < 3:
        n = 3

    for i in range(3, n):
        # a = g.getRandomEdge()
        # g.addEdge(nombreArista(i, a.n0.id), i, a.n0.id)
        # g.addEdge(nombreArista(i, a.n1.id), i, a.n1.id)
        event_DorogovtsevMendes(g)

    return g


def DorogovtsevMendesGraphV2(n, divisor=10, p_inicial=1.0):
    g = Graph()

    divisor = max(1.0, divisor)

    g.addEdge(edgeName(0, 1), 0, 1).atrib['__DM'] = p_inicial
    g.addEdge(edgeName(1, 2), 1, 2).atrib['__DM'] = p_inicial
    g.addEdge(edgeName(2, 0), 2, 0).atrib['__DM'] = p_inicial

    if n < 3:
        n = 3

    for i in range(3, n):
        a = g.getRandomEdge()
        while not random.random() <= a.atrib['__DM']:
            a = g.getRandomEdge()

        g.addEdge(edgeName(i, a.n0.id), i, a.n0.id).atrib['__DM'] = p_inicial
        g.addEdge(edgeName(i, a.n1.id), i, a.n1.id).atrib['__DM'] = p_inicial
        a.atrib['__DM'] = a.atrib['__DM'] / divisor

    return g


def colorRamp(layer):
    ramp = [
        (0xFA, 0, 0),
        (0xFA, 0x2A, 0),
        (0xFB, 0x55, 0),
        (0xFC, 0x7F, 0),
        (0xFD, 0xAA, 0),
        (0xFE, 0xD4, 0),
        (0xFF, 0xFF, 0),
        (0xD4, 0xFF, 0),
        (0xAA, 0xFF, 0),
        (0x7F, 0xFF, 0),
        (0x55, 0xFF, 0),
        (0x2A, 0xFF, 0),
        (0x00, 0xFF, 0)
    ]
    return ramp[layer % len(ramp)]


def BFS(bfs, g, sleep=0, s=None):
    layers = []
    added = {}

    print('BFS started ...')
    if s is None:
        seed = random.choice(list(g.nodes.values()))
    else:
        seed = g.getNode(s)
    seed.style(STYLE_FILLCOLOR, (250, 0, 0))

    n = bfs.addNode(seed.id)
    n.style(STYLE_FILLCOLOR, colorRamp(0))
    n.style(STYLE_SIZE, 20)

    layers.append({seed.id: seed})
    added[seed.id] = seed
    for e in g.edges.values():
        e.atrib['bfs'] = False

    i = 0
    while i < len(layers):
        nextLayer = {}
        curLayer = layers[i]

        for n in curLayer.values():
            # fillColor = rampColor(i + 1)
            edges = n.attr[ATTR_EDGES]
            for e in edges:
                if e.n0.id == n.id:
                    m = e.n1
                else:
                    m = e.n0

                if m.id not in nextLayer and m.id not in added:
                    nn = bfs.addNode(n.id)
                    mm = bfs.addNode(m.id)

                    if i == 0:
                        nn.style(STYLE_SIZE, 20)
                        nn.style(STYLE_FILLCOLOR, colorRamp(0))

                    bfs.addEdge(str(n.id) + '->' + str(m.id), nn.id, mm.id)
                    mm.style(STYLE_FILLCOLOR, colorRamp(i))
                    m.style(STYLE_FILLCOLOR, colorRamp(i))

                    e.style(STYLE_THICKNESS, 2)
                    e.style(STYLE_COLOR, COLOR_DARK_GREEN)

                    e.atrib['bfs'] = True
                    nextLayer[m.id] = m
                    added[m.id] = m
                    time.sleep(sleep / 1000.0)

        i += 1
        if len(nextLayer) != 0:
            layers.append(nextLayer)

    print('BFS finished.')


def DFS(dfs, g, sleep=0, s=None):
    added = {}

    print('DFS started ...')
    if s is None:
        seed = random.choice(list(g.nodes.values()))
    else:
        seed = g.obtNodo(s)

    DFS_R(seed, dfs, added, sleep, 0)
    print('DFS finished.')


def DFS_R(seed, dfs, added, sleep, layer):
    added[seed.id] = seed

    edges = seed.attr[ATTR_EDGES]
    for e in edges:
        if e.n0.id == seed.id:
            m = e.n1
        else:
            m = e.n0

        if not m.id in added:
            nn = dfs.addNode(seed.id)
            mm = dfs.addNode(m.id)

            if layer == 0:
                nn.style(STYLE_SIZE, 20)
                nn.style(STYLE_FILLCOLOR, colorRamp(layer))
                nn.style(STYLE_BORDERCOLOR, colorRamp(layer))

            mm.style(STYLE_FILLCOLOR, colorRamp(layer + 1))
            m.style(STYLE_FILLCOLOR, colorRamp(layer + 1))

            dfs.addEdge(str(nn.id) + '->' + str(mm.id), nn.id, mm.id)

            e.style(STYLE_THICKNESS, 3)
            e.style(STYLE_COLOR, COLOR_DARK_YELLOW)

            time.sleep(sleep / 2000.0)

            DFS_R(m, dfs, added, sleep, layer + 1)

            e.style(STYLE_THICKNESS, 2)
            e.style(STYLE_COLOR, COLOR_DARK_GREEN)
            time.sleep(sleep / 2000.0)
