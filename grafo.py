
import math
import random
import threading
import time
import numpy
import pygame
import pygame.freetype

from arista import Arista
from nodo import Nodo

NODE_NAME_PREFIX = 'nodo_'
X_ATTR = '__x__'
Y_ATTR = '__y__'


def dist(a, b):
    """
    Calcula la distancia entre los puntos a y b
    :param a:
    :param b:
    :return:
    """
    return math.sqrt(
        (a.atributos[X_ATTR] - b.atributos[X_ATTR])**2 + (a.atributos[Y_ATTR] - b.atributos[Y_ATTR])**2)


def fr(k, x):
    """
    Fuerza de repulsion
    :param k:
    :param x:
    :return:
    """
    return (k**2) / x


def fa(k, x):
    """
    Fuerza de atracción
    :param k:
    :param x:
    :return:
    """
    return (x**2) / k


def mag(v2d):
    """
    Magnitud de un vector 2d
    :param v2d:
    :return:
    """
    return math.sqrt((v2d[0] ** 2) + (v2d[1] ** 2))

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


class Grafo:
    """
    Clase grafo
    """

    def __init__(self):
        """
        Constructor
        """
        self.id = 'grafo'
        self.nodos = {}
        self.aristas = {}
        self.atributos = {
            'estilo.fondo': (20, 20, 20),
        }

    def getNodes(self):
        return self.nodos

    def getEdges(self):
        return self.aristas

    def addNode(self, name):
        """
        Agregar nodo al grafo, primero verifica si el nodo ya existe, de lo contrario lo crea y lo agrega al diccionario
        :param name: nombre del nodo
        :return: el nodo que we encontró o se creó
        """
        node = self.nodos.get(name)

        if node is None:
            node = Nodo(name)
            self.nodos[name] = node

        return node

    def addEdge(self, name, node0, node1):
        """
        Agregar una arista al grafo
        :param name: nombre de la arista
        :param node0: nodo origen
        :param node1: nodo destino
        :return: la arista creada
        """
        e = self.aristas.get(name)

        if e is None:
            n0 = self.addNode(node0)
            n1 = self.addNode(node1)
            e = Arista(n0, n1, name)
            self.aristas[name] = e

            n0.atributos.get(Nodo.ATTR_VECINOS).append(n1)
            n1.atributos.get(Nodo.ATTR_VECINOS).append(n0)

            n0.atributos.get(Nodo.ATTR_ARISTAS).append(e)
            n1.atributos.get(Nodo.ATTR_ARISTAS).append(e)

        return e

    def getNode(self, name):
        """
        Busca un nodo en el grafo
        :param name: nombre del nodo a buscar
        :return: el nodo que se encontró o None si no está
        """
        return self.nodos.get(name)

    def getDegree(self, nodeName):
        """
        Obtiene el grado de un nodo
        :param nodeName: nombre del nodo
        :return: grado del nodo
        """
        n = self.getNode(nodeName)
        if n is None:
            return 0

        return len(n.atributos[Nodo.ATTR_VECINOS])

    def __str__(self):
        """
        Convierte el grafo en texto
        :return: representación textual del grafo
        """
        retVal = 'Nodos: '
        for n in self.nodos:
            retVal += n + ', '

        retVal += '\nAristas: '
        for e in self.aristas:
            retVal += str(e) + ', '

        return retVal

    def toGraphviz(self):
        """
        Genera una representación GV del grafo
        :return: representación en GV del grafo
        """
        retVal = 'digraph X {\n'
        for e in self.aristas:
            retVal += str(e) + ';\n'
        retVal += '}\n'

        return retVal

    def draw(self):
        """
        Dibujar el grafo, si se llama continuamente va calculando el layout del mismo
        :param screen: handle del área de dibujo
        :return:
        """
        for v in self.nodos.values():
            v.atributos['disp'] = numpy.array([0, 0])
            for u in self.nodos.values():
                if v != u:
                    delta = v.atributos['pos'] - u.atributos['pos']
                    v.atributos['disp'] = v.atributos['disp'] + (delta / mag(delta)) * fr(self.k, mag(delta))

        for e in self.aristas.values():
            delta = e.n0.atributos['pos'] - e.n1.atributos['pos']
            e.n0.atributos['disp'] = e.n0.atributos['disp'] - (delta / mag(delta)) * fa(self.k, mag(delta))
            e.n1.atributos['disp'] = e.n1.atributos['disp'] + (delta / mag(delta)) * fa(self.k, mag(delta))

        diff = 0
        I = numpy.array([100000, 10000])
        F = numpy.array([-100000, -10000])
        for v in self.nodos.values():
            diff += mag(v.atributos['disp'])
            v.atributos['pos'] = v.atributos['pos'] + (v.atributos['disp'] / mag(v.atributos['disp'])) * min(mag(v.atributos['disp']), self.t)
            I[0] = min(I[0], v.atributos['pos'][0])
            I[1] = min(I[1], v.atributos['pos'][1])
            F[0] = max(F[0], v.atributos['pos'][0])
            F[1] = max(F[1], v.atributos['pos'][1])
        diff /= len(self.nodos)**2

        self.t -= 1 / (10 * math.log2(diff))
        if self.t < 0:
            self.t = 0

        #print(self.t, math.log2(diff))
        Sx = self.res[0] / (F[0] - I[0])
        Sy = self.res[1] / (F[1] - I[0])
        self.escala = min(Sx, Sy) * 0.8

        for a in self.aristas.values():
            a.draw(self)

        for v in self.nodos.values():
            v.draw(self)

    def display(self, res):
        pause = False
        running = True
        timeout = 0.1

        pygame.init()
        self.screen = pygame.display.set_mode(res)
        self.res = numpy.array(res)
        self.t = 10
        self.k = math.sqrt((self.res[0] * self.res[1]) / len(self.nodos))
        self.origen = self.res / 2
        self.escala = 1
        self.tam_fuente = 10
        self.fuente = pygame.freetype.Font('fonts/courier_b.ttf', self.tam_fuente)

        for v in self.nodos.values():
            v.atributos['pos'] = numpy.array(
                [random.randint(-self.origen[0], self.origen[0]), random.randint(-self.origen[1], self.origen[1])])

        while running:
            self.screen.fill(self.atributos['estilo.fondo'])

            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.KEYDOWN:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_SPACE]:
                        pause = not pause

                if event.type == pygame.QUIT:
                    running = False

                # mouseClick = pygame.mouse.get_pressed()
                # if sum(mouseClick) > 0:
                #     posX, posY = pygame.mouse.get_pos()
                #     celX, celY = int(np.floor(posX / dim)), int(np.floor(posY / dim) )
                #     newGameState[celX, celY] = 1

            self.draw()

            cad = str(len(self.nodos.values())) + ' nodos y ' + str(len(self.aristas.values())) + ' aristas'
            self.fuente.render_to(self.screen, (10, 10), cad, (128, 128, 128))

            time.sleep(timeout / len(self.nodos))
            pygame.display.flip()

    def display_thread(self, res):
        t = threading.Thread(target=self.display, args=(res,))
        t.start()

    @staticmethod
    def randomErdos(n, m):
        """
        Genera grafo aleatorio con el método de Erdos
        :param n: número de nodos
        :param m: número de aristas
        :return: grafo generado
        """
        g = Grafo()

        for i in range(n):
            g.addNode(NODE_NAME_PREFIX + str(i))

        for i in range(m):
            u = random.randint(0, n - 1)
            v = random.randint(0, n - 1)
            if u != v:
                g.addEdge(NODE_NAME_PREFIX + str(u) + '->' + NODE_NAME_PREFIX + str(v), NODE_NAME_PREFIX + str(u),
                          NODE_NAME_PREFIX + str(v))

        return g

    @staticmethod
    def randomGilbert(n, p):
        """
        Genera grafo aleatorio con el método de Gilbert
        :param n: número de nodos
        :param p: probabilidad de generar una arista entre un par de nodos
        :return: grafo generado
        """
        g = Grafo()

        for i in range(n):
            g.addNode(NODE_NAME_PREFIX + str(i))

        for i in range(n):
            for j in range(n):
                if random.random() < p:
                    if (j != i):
                        g.addEdge(NODE_NAME_PREFIX + str(i) + '->' + NODE_NAME_PREFIX + str(j), NODE_NAME_PREFIX + str(i),
                                  NODE_NAME_PREFIX + str(j))
        return g

    @staticmethod
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
            node = g.addNode(NODE_NAME_PREFIX + str(i))
            node.atributos[X_ATTR] = random.random()
            node.atributos[Y_ATTR] = random.random()

        # Crear una arista entre cada par de nodos que están a distancia <= r
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = dist(g.getNode(NODE_NAME_PREFIX + str(i)), g.getNode(NODE_NAME_PREFIX + str(j)))
                    if d <= r:
                        g.addEdge(NODE_NAME_PREFIX + str(i) + '->' + NODE_NAME_PREFIX + str(j), NODE_NAME_PREFIX + str(i),
                                  NODE_NAME_PREFIX + str(j))

        return g

    @staticmethod
    def randomBarabasi(n, d):
        """
        Genera grafo aleatorio con el método de Barabasi
        :param n: número de nodos
        :param d: número máximo de aristas por nodo
        :return: grafo generado
        """
        g = Grafo()
        g.addNode(NODE_NAME_PREFIX + str(0))

        for u in range(1, n):
            randomNodes = randomArray(u)
            for v in range(u):
                deg = g.getDegree(NODE_NAME_PREFIX + str(randomNodes[v]))
                p = 1 - deg / d
                if random.random() < p:
                    if randomNodes[v] != u:
                        g.addEdge(NODE_NAME_PREFIX + str(u) + '->' + NODE_NAME_PREFIX + str(randomNodes[v]),
                                  NODE_NAME_PREFIX + str(u), NODE_NAME_PREFIX + str(randomNodes[v]))

        return g

# def run(g):
#     pause = False
#     running = True
#     timeout = 0.5
#
#     w = 800
#     h = 800
#     area = w * h
#
#     I = numpy.array([-w / 2, -h / 2])
#     F = numpy.array([w / 2, h / 2])
#
#     origen = numpy.array([w / 2, h / 2])
#
#     long = 250
#
#     t = 10
#
#     k = math.sqrt(area / len(g.nodos))
#
#     # place vertices at random
#     for v in g.nodos.values():
#         v.attributes['pos'] = numpy.array([random.randint(-w / 2, w / 2), random.randint(-h / 2, h / 2)])
#
#     while running:
#         screen.fill((25, 25, 25))
#
#         ev = pygame.event.get()
#         for event in ev:
#             if event.type == pygame.KEYDOWN:
#                 pressed = pygame.key.get_pressed()
#                 if pressed[pygame.K_SPACE]:
#                     pause = not pause
#
#             if event.type == pygame.QUIT:
#                 running = False
#
#             # mouseClick = pygame.mouse.get_pressed()
#             # if sum(mouseClick) > 0:
#             #     posX, posY = pygame.mouse.get_pos()
#             #     celX, celY = int(np.floor(posX / dim)), int(np.floor(posY / dim) )
#             #     newGameState[celX, celY] = 1
#
#         for v in g.nodos.values():
#             v.attributes['force'] = numpy.array([0, 0])
#
#         for v in g.nodos.values():
#             for n in v.attributes[Nodo.ATTR_VECINOS]:
#                 delta = n.attributes['pos'] - v.attributes['pos']
#                 f_mag = mag(delta)
#                 delta_uni = delta / f_mag
#                 force = delta_uni * (f_mag - long)
#                 v.attributes['force'] = v.attributes['force'] + force
#
#         for v in g.nodos.values():
#             for u in g.nodos.values():
#                 delta = u.attributes['pos'] - v.attributes['pos']
#                 f_mag = mag(delta)
#                 if f_mag > 0:
#                     delta_uni = delta / f_mag
#                     force = delta_uni * (long / f_mag)
#                     v.attributes['force'] = v.attributes['force'] - force
#
#         diff = 0
#         I = numpy.array([100000, 10000])
#         F = numpy.array([-100000, -10000])
#         for v in g.nodos.values():
#             diff += mag(v.attributes['force'])
#             v.attributes['pos'] = v.attributes['pos'] + v.attributes['force'] * 0.1
#             I[0] = min(I[0], v.attributes['pos'][0])
#             I[1] = min(I[1], v.attributes['pos'][1])
#             F[0] = max(F[0], v.attributes['pos'][0])
#             F[1] = max(F[1], v.attributes['pos'][1])
#         diff /= sqr(len(g.nodos))
#
#         t -= 1 / (10 * math.log2(diff))
#         if t < 0:
#             t = 0
#
#         #print(t, math.log2(diff))
#         Sx = w / (F[0] - I[0])
#         Sy = h / (F[1] - I[0])
#         S = min(Sx, Sy) * 0.8
#
#         for a in g.aristas.values():
#             #pygame.draw.line(screen, (200, 200, 200), S * (a.n0.attributes['pos']) + origen, S * (a.n1.attributes['pos']) + origen)
#             a.draw(screen, S, origen)
#
#         for v in g.nodos.values():
#             pygame.draw.circle(screen, (200, 200, 0), S * v.attributes['pos'] + origen, 10 * S)
#
#         time.sleep(timeout / len(g.nodos))
#         pygame.display.flip()