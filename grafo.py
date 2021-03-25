import math
import random
import numpy
import threading

import nodo
from arista import Arista
from nodo import Nodo
from util import dibujar_rect_punteado, Transformacion

NNAME_PREFIX = 'nodo_'
X_ATTR = '__x__'
Y_ATTR = '__y__'

ATTR_ESTILO = '_estilo'
ATTR_ACOMODADO = '__acomodado__'

ESTILO_FONDO = '_fondo'
ESTILO_MOSTRAR_EXTENSION = '_mostrarExt'
ESTILO_MOSTRAR_VIEWPORT = '_mostrarVP'
ESTILO_APLICADO = '_estiloAplicado?'
ESTILO_COL_LINEA = '_estiloColorLinea'

WRITING_LOCK = threading.Lock()

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
        self.atrib = {
            ATTR_ESTILO: {
                ESTILO_FONDO: (20, 20, 20),
                ESTILO_COL_LINEA: (224, 244, 244),
                ESTILO_MOSTRAR_EXTENSION: False,
                ESTILO_MOSTRAR_VIEWPORT: False,
                ESTILO_APLICADO: None,
            },
            ATTR_ACOMODADO: False,
        }
        self.threading = False

    def clonar(self):
        ret = Grafo()

        ret.id = self.id + "_clon"
        for n in self.nodos.values():
            nn = ret.agregarNodo(n.id)
            nn.atrib = n.atrib.copy()
            nn.atrib[nodo.ATTR_VECINOS] = []
            nn.atrib[nodo.ATTR_ARISTAS] = []

        for m in self.aristas.values():
            e = ret.agregarArista(m.id, m.n0.id, m.n1.id)
            # e.atrib = m.atrib.copy()

        ret.atrib.clear()
        ret.atrib = self.atrib.copy()

        return ret

    def agregarNodo(self, name):
        """
        Agregar nodo al grafo, primero verifica si el nodo ya existe, de lo contrario lo crea y lo agrega al diccionario
        :param name: nombre del nodo
        :return: el nodo que we encontró o se creó
        """
        node = self.nodos.get(name)

        if node is None:
            node = Nodo(name)

            with WRITING_LOCK:
                self.nodos[name] = node

        return node

    def agregarArista(self, name, node0, node1):
        """
        Agregar una arista al grafo
        :param name: nombre de la arista
        :param node0: nodo origen
        :param node1: nodo destino
        :return: la arista creada
        """
        e = self.aristas.get(name)

        if e is None:
            n0 = self.agregarNodo(node0)
            n1 = self.agregarNodo(node1)
            e = Arista(n0, n1, name)

            with WRITING_LOCK:
                self.aristas[name] = e

            n0.atrib.get(nodo.ATTR_VECINOS).append(n1)
            n1.atrib.get(nodo.ATTR_VECINOS).append(n0)

            n0.atrib.get(nodo.ATTR_ARISTAS).append(e)
            n1.atrib.get(nodo.ATTR_ARISTAS).append(e)

        return e

    def obtNodo(self, name):
        """
        Busca un nodo en el grafo
        :param name: nombre del nodo a buscar
        :return: el nodo que se encontró o None si no está
        """
        return self.nodos.get(name)

    def obtGrado(self, nodeName):
        """
        Obtiene el grado de un nodo
        :param nodeName: nombre del nodo
        :return: grado del nodo
        """
        n = self.obtNodo(nodeName)
        if n is None:
            return 0

        return len(n.atrib[nodo.ATTR_VECINOS])

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

    def aGraphviz(self):
        """
        Genera una representación GV del grafo
        :return: representación en GV del grafo
        """
        retVal = 'digraph X {\n'
        for e in self.aristas.values():
            n0 = e.n0.id
            n1 = e.n1.id
            retVal += n0 + ' -> ' + n1 + ';\n'
        retVal += '}\n'

        return retVal

    def calcular_extension(self):
        """
        Calcula el rectangulo que delimita la zona del grafo
        :return:
        """
        # if len(self.nodos) < 2:
        #     self.extent = numpy.array([numpy.array([-1.0, -1.0]), numpy.array([1.0, 1.0])])
        #     return self.extent

        I = numpy.array([math.inf, math.inf])
        F = numpy.array([-math.inf, -math.inf])
        for v in self.nodos.values():
            I[0] = min(I[0], v.atrib[nodo.ATTR_POS][0])
            I[1] = min(I[1], v.atrib[nodo.ATTR_POS][1])
            F[0] = max(F[0], v.atrib[nodo.ATTR_POS][0])
            F[1] = max(F[1], v.atrib[nodo.ATTR_POS][1])

        if F[0] <= I[0] or F[1] <= I[0]:
            self.extent = numpy.array([numpy.array([-1.0, -1.0]), numpy.array([1.0, 1.0])])
        else:
            self.extent = numpy.array([I, F])

        return self.extent

    def guardar(self, archivo):
        """
        Guarda el grafo en un archivo
        :param archivo: nombre del archivo
        :return:
        """
        print('Guardando', archivo, ' ...', end='')
        gv = self.aGraphviz()
        f = open(archivo, 'w+')
        f.write(gv)
        print('Ok.', len(self.nodos), 'nodos,', len(self.aristas), 'aristas')

    @staticmethod
    def abrir(archivo):
        """
        Lee el grafo de un archivo
        :param archivo: nombre del archivo
        :return:
        """
        print('Leyendo', archivo, ' ...', end='')
        g = Grafo()
        f = open(archivo, 'r')
        lines = f.readlines()
        for i in range(1, len(lines)):
            tokens = lines[i].split(' ')
            if len(tokens) < 3:
                continue
            tokens[2] = tokens[2].rstrip(';\n')
            g.agregarArista(tokens[0] + tokens[1] + tokens[2], tokens[0], tokens[2])

        print('Ok.', len(g.nodos), 'nodos,', len(g.aristas), 'aristas')
        return g

    def getRandomEdge(self):
        return random.choice(list(self.aristas.values()))

    def estilo(self, est, val):
        """
        Establece un valor de estilo en el grafo
        :param est: llave del estilo
        :param val: valor del estilo
        :return:
        """
        self.atrib[Grafo.ATTR_ESTILO][est] = val

    def dibujar(self, viewport):
        """
        Dibuja el grafo en el viewport
        :param viewport:
        :return:
        """
        # if not self.atrib[Grafo.ATTR_ACOMODADO]:
        #     layout.Random(self).ejecutar()
        #     self.atrib[Grafo.ATTR_ACOMODADO] = True

        self.calcular_extension()
        self.transformacion = Transformacion(self.extent, viewport.rect)

        # viewport.frame.surf(self.atrib[Grafo.ATTR_ESTILO][Grafo.ESTILO_FONDO])

        if self.atrib[ATTR_ESTILO][ESTILO_MOSTRAR_EXTENSION]:
            I = self.transformacion.transformar(self.extent[0])
            F = self.transformacion.transformar(self.extent[1])
            dibujar_rect_punteado(viewport.surf, (128, 128, 128), I, F)

        if self.atrib[ATTR_ESTILO][ESTILO_MOSTRAR_VIEWPORT]:
            dibujar_rect_punteado(viewport.surf, (255, 128, 128), viewport.rect[0], viewport.rect[1])

        for v in self.nodos.values():
            v.atrib[nodo.ATTR_POS_VP] = self.transformacion.transformar(v.atrib[nodo.ATTR_POS])

        for a in self.aristas.values():
            a.dibujar(viewport)

        for v in self.nodos.values():
            v.dibujar(viewport, self.transformacion)
