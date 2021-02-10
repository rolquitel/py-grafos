
import math
import random
import threading
import time
import numpy
import pygame
import pygame.freetype

import disposicion
from arista import Arista
from nodo import Nodo
from util import dibujar_rect_punteado

NODE_NAME_PREFIX = 'nodo_'
X_ATTR = '__x__'
Y_ATTR = '__y__'


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
            'estilo.mostrarExtension?': True,
        }

    def obtNodos(self):
        return self.nodos

    def obtAristas(self):
        return self.aristas

    def agregarNodo(self, name):
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
            self.aristas[name] = e

            n0.atributos.get(Nodo.ATTR_VECINOS).append(n1)
            n1.atributos.get(Nodo.ATTR_VECINOS).append(n0)

            n0.atributos.get(Nodo.ATTR_ARISTAS).append(e)
            n1.atributos.get(Nodo.ATTR_ARISTAS).append(e)

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

    def aGraphviz(self):
        """
        Genera una representación GV del grafo
        :return: representación en GV del grafo
        """
        retVal = 'digraph X {\n'
        for e in self.aristas:
            retVal += str(e) + ';\n'
        retVal += '}\n'

        return retVal

    def transformar(self, punto):
        return self.escala * (punto - self.I) + self.offset

    def dibujar(self):
        """
        Dibujar el grafo, si se llama continuamente va calculando el layout del mismo
        :param screen: handle del área de dibujo
        :return:
        """
        contenido = 0.9
        marco = (1 - contenido) / 2
        I = numpy.array([100000, 10000])
        F = numpy.array([-100000, -10000])
        for v in self.nodos.values():
            I[0] = min(I[0], v.atributos['pos'][0])
            I[1] = min(I[1], v.atributos['pos'][1])
            F[0] = max(F[0], v.atributos['pos'][0])
            F[1] = max(F[1], v.atributos['pos'][1])

        Sx = self.res[0] / (F[0] - I[0])
        Sy = self.res[1] / (F[1] - I[1])

        self.I = I

        if Sx > Sy:
            self.escala = Sy * contenido
            desp = (Sx - Sy) / (2 * Sx) + marco
            self.offset = numpy.array([self.res[0] * desp, self.res[1] * marco])
        else:
            self.escala = Sx * contenido
            desp = (Sy - Sx) / (2 * Sy) + marco
            self.offset = numpy.array([self.res[0] * marco, self.res[1] * desp])

        if self.atributos['estilo.mostrarExtension?']:
            I = self.transformar(I)
            F = self.transformar(F)
            dibujar_rect_punteado(self.screen, (128, 128, 128), I, F)

        for a in self.aristas.values():
            a.dibujar(self)

        for v in self.nodos.values():
            v.dibujar(self)

    def mostrar(self, res, disp = None):
        pause = False
        running = True
        timeout = 0.1
        acomodando = True

        pygame.init()
        self.screen = pygame.display.set_mode(res)
        self.res = numpy.array(res)
        self.origen = self.res / 2
        self.escala = 1
        self.tam_fuente = 10
        self.fuente = pygame.freetype.Font('fonts/courier_b.ttf', self.tam_fuente)

        if disp == None:
            disp = disposicion.FruchtermanReingold(self, res)

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

            if acomodando:
                acomodando = not disp.paso()

            self.dibujar()

            cad = str(len(self.nodos.values())) + ' nodos y ' + str(len(self.aristas.values())) + ' aristas'
            self.fuente.render_to(self.screen, (10, 10), cad, (128, 128, 128))

            time.sleep(timeout / len(self.nodos))
            pygame.display.flip()

    def display_thread(self, res):
        t = threading.Thread(target=self.mostrar, args=(res,))
        t.start()
