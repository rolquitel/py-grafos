import math
import random
import numpy
import threading

from edge import Edge
from node import Node
from util import draw_dashed_rect, Transform
from names import *

WRITING_LOCK = threading.Lock()


class Graph:
    """
    Clase grafo
    """

    def __init__(self):
        """
        Constructor
        """
        self.id = 'grafo'
        self.nodes = {}
        self.edges = {}
        self.attr = {
            ATTR_STYLE: {
                STYLE_BACKGROUND: (20, 20, 20),
                STYLE_LINECOLOR: (224, 244, 244),
                STYLE_SHOW_EXT: False,
                STYLE_SHOW_VP: False,
                STYLE_APPLIED: None,
            },
            ATTR_LAYERED: False,
        }
        self.threading = False

    def clone(self):
        ret = Graph()

        ret.id = self.id + "_clon"
        for n in self.nodes.values():
            nn = ret.addNode(n.id)
            nn.attr = n.attr.copy()
            nn.attr[ATTR_NEIGHBORS] = []
            nn.attr[ATTR_EDGES] = []

        for m in self.edges.values():
            e = ret.addEdge(m.id, m.n0.id, m.n1.id)
            # e.atrib = m.atrib.copy()

        ret.attr.clear()
        ret.attr = self.attr.copy()

        return ret

    def addNode(self, name):
        """
        Agregar nodo al grafo, primero verifica si el nodo ya existe, de lo contrario lo crea y lo agrega al diccionario
        :param name: nombre del nodo
        :return: el nodo que we encontró o se creó
        """
        node = self.nodes.get(name)

        if node is None:
            node = Node(name)

            with WRITING_LOCK:
                self.nodes[name] = node

        return node

    def addEdge(self, name, node0, node1):
        """
        Agregar una arista al grafo
        :param name: nombre de la arista
        :param node0: nodo origen
        :param node1: nodo destino
        :return: la arista creada
        """
        e = self.edges.get(name)

        if e is None:
            n0 = self.addNode(node0)
            n1 = self.addNode(node1)
            e = Edge(n0, n1, name)

            with WRITING_LOCK:
                self.edges[name] = e

            n0.attr.get(ATTR_NEIGHBORS).append(n1)
            n1.attr.get(ATTR_NEIGHBORS).append(n0)

            n0.attr.get(ATTR_EDGES).append(e)
            n1.attr.get(ATTR_EDGES).append(e)

        return e

    def getNode(self, name):
        """
        Busca un nodo en el grafo
        :param name: nombre del nodo a buscar
        :return: el nodo que se encontró o None si no está
        """
        return self.nodes.get(name)

    def getDegree(self, nodeName):
        """
        Obtiene el grado de un nodo
        :param nodeName: nombre del nodo
        :return: grado del nodo
        """
        n = self.getNode(nodeName)
        if n is None:
            return 0

        return len(n.attr[ATTR_NEIGHBORS])

    def __str__(self):
        """
        Convierte el grafo en texto
        :return: representación textual del grafo
        """
        retVal = 'Nodos: '
        for n in self.nodes:
            retVal += n + ', '

        retVal += '\nAristas: '
        for e in self.edges:
            retVal += str(e) + ', '

        return retVal

    def toGraphviz(self):
        """
        Genera una representación GV del grafo
        :return: representación en GV del grafo
        """
        retVal = 'digraph X {\n'
        for e in self.edges.values():
            n0 = e.n0.id
            n1 = e.n1.id
            retVal += n0 + ' -> ' + n1 + ';\n'
        retVal += '}\n'

        return retVal

    def compute_ext(self):
        """
        Calcula el rectangulo que delimita la zona del grafo
        :return:
        """
        # if len(self.nodos) < 2:
        #     self.extent = numpy.array([numpy.array([-1.0, -1.0]), numpy.array([1.0, 1.0])])
        #     return self.extent

        I = numpy.array([math.inf, math.inf])
        F = numpy.array([-math.inf, -math.inf])
        for v in self.nodes.values():
            I[0] = min(I[0], v.attr[ATTR_POS][0])
            I[1] = min(I[1], v.attr[ATTR_POS][1])
            F[0] = max(F[0], v.attr[ATTR_POS][0])
            F[1] = max(F[1], v.attr[ATTR_POS][1])

        if F[0] <= I[0] or F[1] <= I[0]:
            self.extent = numpy.array(
                [numpy.array([-1.0, -1.0]), numpy.array([1.0, 1.0])])
        else:
            self.extent = numpy.array([I, F])

        return self.extent

    def save(self, archivo):
        """
        Guarda el grafo en un archivo
        :param archivo: nombre del archivo
        :return:
        """
        print('Guardando', archivo, ' ...', end='')
        gv = self.toGraphviz()
        f = open(archivo, 'w+')
        f.write(gv)
        print('Ok.', len(self.nodes), 'nodos,', len(self.edges), 'aristas')

    @staticmethod
    def load(archivo):
        """
        Lee el grafo de un archivo
        :param archivo: nombre del archivo
        :return:
        """
        print('Leyendo', archivo, ' ...', end='')
        g = Graph()
        f = open(archivo, 'r')
        lines = f.readlines()
        for i in range(1, len(lines)):
            tokens = lines[i].split(' ')
            if len(tokens) < 3:
                continue
            tokens[2] = tokens[2].rstrip(';\n')
            g.addEdge(tokens[0] + tokens[1] + tokens[2], tokens[0], tokens[2])

        print('Ok.', len(g.nodes), 'nodos,', len(g.edges), 'aristas')
        return g

    def getRandomEdge(self):
        return random.choice(list(self.edges.values()))

    def style(self, est, val):
        """
        Establece un valor de estilo en el grafo
        :param est: llave del estilo
        :param val: valor del estilo
        :return:
        """
        self.attr[Graph.ATTR_ESTILO][est] = val

    def draw(self, viewport):
        """
        Dibuja el grafo en el viewport
        :param viewport:
        :return:
        """
        # if not self.atrib[Grafo.ATTR_ACOMODADO]:
        #     layout.Random(self).ejecutar()
        #     self.atrib[Grafo.ATTR_ACOMODADO] = True

        self.compute_ext()
        self.transformacion = Transform(self.extent, viewport.rect)

        # viewport.frame.surf(self.atrib[Grafo.ATTR_ESTILO][Grafo.ESTILO_FONDO])

        if self.attr[ATTR_STYLE][STYLE_SHOW_EXT]:
            I = self.transformacion.transform(self.extent[0])
            F = self.transformacion.transform(self.extent[1])
            draw_dashed_rect(viewport.surf, (128, 128, 128), I, F)

        if self.attr[ATTR_STYLE][STYLE_SHOW_VP]:
            draw_dashed_rect(viewport.surf, (255, 128, 128),
                             viewport.rect[0], viewport.rect[1])

        for v in self.nodes.values():
            v.attr[ATTR_POS_VP] = self.transformacion.transform(
                v.attr[ATTR_POS])

        for a in self.edges.values():
            a.draw(viewport)

        for v in self.nodes.values():
            v.draw(viewport, self.transformacion)
