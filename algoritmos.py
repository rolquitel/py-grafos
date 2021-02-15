import math
import random

from grafo import Grafo, NODE_NAME_PREFIX, X_ATTR, Y_ATTR


def dist(a, b):
    """
    Calcula la distancia entre los puntos a y b
    :param a:
    :param b:
    :return:
    """
    return math.sqrt(
        (a.atrib[X_ATTR] - b.atrib[X_ATTR]) ** 2 + (a.atrib[Y_ATTR] - b.atrib[Y_ATTR]) ** 2)


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
    g = Grafo()

    for i in range(n):
        g.agregarNodo(NODE_NAME_PREFIX + str(i))

    for i in range(m):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            g.agregarArista(NODE_NAME_PREFIX + str(u) + '->' + NODE_NAME_PREFIX + str(v), NODE_NAME_PREFIX + str(u),
                            NODE_NAME_PREFIX + str(v))

    return g


def randomGilbert(n, p):
    """
    Genera grafo aleatorio con el método de Gilbert
    :param n: número de nodos
    :param p: probabilidad de generar una arista entre un par de nodos
    :return: grafo generado
    """
    g = Grafo()

    for i in range(n):
        g.agregarNodo(NODE_NAME_PREFIX + str(i))

    for i in range(n):
        for j in range(n):
            if random.random() < p:
                if (j != i):
                    g.agregarArista(NODE_NAME_PREFIX + str(i) + '->' + NODE_NAME_PREFIX + str(j),
                                    NODE_NAME_PREFIX + str(i),
                                    NODE_NAME_PREFIX + str(j))
    return g


def randomGeo(n, r):
    """
    Genera grafo aleatorio con el método geográfico simple
    :param n: número de nodos
    :param r: distancia máxima para generar la arista entre un par de nodos
    :return: grafo generado
    """
    g = Grafo()

    # Generar n nodos con coordenadas en el espacio ((0,0),(1,1))
    for i in range(n):
        node = g.agregarNodo(NODE_NAME_PREFIX + str(i))
        node.atrib[X_ATTR] = random.random()
        node.atrib[Y_ATTR] = random.random()

    # Crear una arista entre cada par de nodos que están a distancia <= r
    for i in range(n):
        for j in range(n):
            if i != j:
                d = dist(g.obtNodo(NODE_NAME_PREFIX + str(i)), g.obtNodo(NODE_NAME_PREFIX + str(j)))
                if d <= r:
                    g.agregarArista(NODE_NAME_PREFIX + str(i) + '->' + NODE_NAME_PREFIX + str(j),
                                    NODE_NAME_PREFIX + str(i),
                                    NODE_NAME_PREFIX + str(j))

    return g


def randomBarabasi(n, d):
    """
    Genera grafo aleatorio con el método de Barabasi
    :param n: número de nodos
    :param d: número máximo de aristas por nodo
    :return: grafo generado
    """
    g = Grafo()
    g.agregarNodo(NODE_NAME_PREFIX + str(0))

    for u in range(1, n):
        randomNodes = randomArray(u)
        for v in range(u):
            deg = g.obtGrado(NODE_NAME_PREFIX + str(randomNodes[v]))
            p = 1 - deg / d
            if random.random() < p:
                if randomNodes[v] != u:
                    g.agregarArista(NODE_NAME_PREFIX + str(u) + '->' + NODE_NAME_PREFIX + str(randomNodes[v]),
                                    NODE_NAME_PREFIX + str(u), NODE_NAME_PREFIX + str(randomNodes[v]))

    return g


def nombreNodo(i):
    return NODE_NAME_PREFIX + str(i)


def nombreArista(i, j):
    return nombreNodo(i) + '->' + nombreNodo(j)


def grafoMalla(m, n=0, diagonales=False):
    if n == 0:
        n = m

    m = max(2, m)
    n = max(2, n)

    g = Grafo()

    for i in range(m):
        for j in range(n):
            if j < n - 1:
                g.agregarArista(nombreArista(i * n + j, i * n + j + 1),
                                nombreNodo(i * n + j),
                                nombreNodo(i * n + j + 1))
            if i < m - 1:
                g.agregarArista(nombreArista(i * n + j, (i + 1) * n + j),
                                nombreNodo(i * n + j),
                                nombreNodo((i + 1) * n + j))
            if i < m - 1 and j < n - 1 and diagonales:
                g.agregarArista(nombreArista(i * n + j, (i + 1) * n + j + 1),
                                nombreNodo(i * n + j),
                                nombreNodo((i + 1) * n + j + 1))
            if i > 0 and j < n - 1 and diagonales:
                g.agregarArista(nombreArista(i * n + j, (i - 1) * n + j + 1),
                                nombreNodo(i * n + j),
                                nombreNodo((i - 1) * n + j + 1))

    return g
