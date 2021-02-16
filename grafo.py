import math
import random
import threading
import numpy
import pygame
import pygame.freetype

import layout
from arista import Arista
from nodo import Nodo
from util import dibujar_rect_punteado, Transformacion, Viewport

NODE_NAME_PREFIX = 'nodo_'
X_ATTR = '__x__'
Y_ATTR = '__y__'


class Grafo:
    """
    Clase grafo
    """
    ATTR_ESTILO = '_estilo'

    ESTILO_FONDO = '_fondo'
    ESTILO_MOSTRAR_EXTENSION = '_mostrarExt'
    ESTILO_MOSTRAR_VIEWPORT = '_mostrarVP'

    def __init__(self):
        """
        Constructor
        """
        self.id = 'grafo'
        self.nodos = {}
        self.aristas = {}
        self.atrib = {
            Grafo.ATTR_ESTILO: {
                Grafo.ESTILO_FONDO: (20, 20, 20),
                Grafo.ESTILO_MOSTRAR_EXTENSION: False,
                Grafo.ESTILO_MOSTRAR_VIEWPORT: False,
            },
        }
        self.threading = False

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

            n0.atrib.get(Nodo.ATTR_VECINOS).append(n1)
            n1.atrib.get(Nodo.ATTR_VECINOS).append(n0)

            n0.atrib.get(Nodo.ATTR_ARISTAS).append(e)
            n1.atrib.get(Nodo.ATTR_ARISTAS).append(e)

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
        for e in self.aristas.values():
            n0 = e.n0.id
            n1 = e.n1.id
            retVal += n0 + ' -> ' + n1 + ';\n'
        retVal += '}\n'

        return retVal

    def calcular_extension(self):
        I = numpy.array([math.inf, math.inf])
        F = numpy.array([-math.inf, -math.inf])
        for v in self.nodos.values():
            I[0] = min(I[0], v.atrib[Nodo.ATTR_POS][0])
            I[1] = min(I[1], v.atrib[Nodo.ATTR_POS][1])
            F[0] = max(F[0], v.atrib[Nodo.ATTR_POS][0])
            F[1] = max(F[1], v.atrib[Nodo.ATTR_POS][1])

        self.extent = numpy.array([I, F])
        return self.extent

    def estilo(self, est, val):
        self.atrib[Grafo.ATTR_ESTILO][est] = val

    def dibujar(self):
        """
        Dibujar el grafo, si se llama continuamente va calculando el layout del mismo
        :param screen: handle del área de dibujo
        :return:
        """
        self.calcular_extension()
        self.transformacion = Transformacion(self.extent, self.viewport.rect)

        self.viewport.surf.fill(self.atrib[Grafo.ATTR_ESTILO][Grafo.ESTILO_FONDO])

        if self.atrib[Grafo.ATTR_ESTILO][Grafo.ESTILO_MOSTRAR_EXTENSION]:
            I = self.transformacion.transformar(self.extent[0])
            F = self.transformacion.transformar(self.extent[1])
            dibujar_rect_punteado(self.viewport.surf, (128, 128, 128), I, F)

        if self.atrib[Grafo.ATTR_ESTILO][Grafo.ESTILO_MOSTRAR_VIEWPORT]:
            dibujar_rect_punteado(self.viewport.surf, (255, 128, 128), self.viewport.rect[0], self.viewport.rect[1])

        for v in self.nodos.values():
            v.atrib[Nodo.ATTR_POS_VP] = self.transformacion.transformar(v.atrib[Nodo.ATTR_POS])

        for a in self.aristas.values():
            a.dibujar(self)

        for v in self.nodos.values():
            v.dibujar(self)

    def posicionar_nodos_malla(self):
        lado = int(math.ceil(math.sqrt(len(self.nodos))))
        tam = self.viewport.res / (lado + 2)
        origen = self.viewport.res / 2

        n = 0
        for v in self.nodos.values():
            x = tam[0] * int((n % lado) + 1) - origen[0]
            y = tam[1] * int((n / lado) + 1) - origen[1]
            v.atrib[Nodo.ATTR_POS] = numpy.array([x, y])
            n = n + 1

    def mostrar(self, res, lyout=None):
        pause = False
        running = True
        CPS = 60
        marco = 0.05

        pygame.init()
        surf = pygame.display.set_mode(res)
        res = numpy.array(res)
        self.viewport = Viewport([marco * res, (1 - marco) * res], surf, res)
        self.tam_fuente = 10
        self.fuente = pygame.freetype.Font('fonts/courier_b.ttf', self.tam_fuente)
        self.layout = lyout
        self.antialias = False

        layinout = False

        self.layout = layout.Random(self)
        self.layout.ejecutar()

        fpsClock = pygame.time.Clock()

        while running:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.KEYDOWN:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_SPACE]:
                        pause = not pause
                    elif pressed[pygame.K_b]:
                        if not layinout:
                            layinout = True
                            self.layout = layout.BarnesHut(self)
                            # self.layout.avance = 50
                            # self.layout.repeticiones_para_bajar = 20
                            self.layout.umbral_convergencia = 1.0
                    elif pressed[pygame.K_s]:
                        if not layinout:
                            layinout = True
                            self.layout = layout.Spring(self)
                    elif pressed[pygame.K_f]:
                        if not layinout:
                            layinout = True
                            self.layout = layout.FruchtermanReingold(self)
                    elif pressed[pygame.K_ESCAPE]:
                        layinout = False
                    elif pressed[pygame.K_a]:
                        for a in self.aristas.values():
                            a.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_ANTIALIAS] = not a.atrib[Arista.ATTR_ESTILO][
                                Arista.ESTILO_ANTIALIAS]
                    elif pressed[pygame.K_r]:
                        if not layinout:
                            layout.Random(self).ejecutar()
                    elif pressed[pygame.K_g]:
                        if not layinout:
                            layout.Grid(self).ejecutar()
                    elif pressed[pygame.K_PLUS]:
                        self.viewport.zoom(1.5)
                    elif pressed[pygame.K_MINUS]:
                        self.viewport.zoom(1 / 1.5)

                if event.type == pygame.QUIT:
                    layout.parar_layout = True
                    running = False

                # mouseClick = pygame.mouse.get_pressed()
                # if sum(mouseClick) > 0:
                #     posX, posY = pygame.mouse.get_pos()
                #     celX, celY = int(np.floor(posX / dim)), int(np.floor(posY / dim) )
                #     newGameState[celX, celY] = 1

            if pause:
                continue

            if layinout:
                layinout = not self.layout.paso()

            self.dibujar()

            cad = str(len(self.nodos.values())) + ' nodos y ' + str(len(self.aristas.values())) + ' aristas'
            self.fuente.render_to(self.viewport.surf, (10, 10), cad, (128, 128, 128))
            cad = str(math.ceil(1000 / fpsClock.tick(CPS))) + ' cps'
            self.fuente.render_to(self.viewport.surf, (res[0] - 50, res[1] - 15), cad, (128, 128, 128))

            pygame.display.flip()

    def display_thread(self, res):
        t = threading.Thread(target=self.mostrar, args=(res,))
        t.start()

    def guardar(self, archivo):
        print('Guardando', archivo, ' ...', end='')
        gv = self.aGraphviz()
        f = open(archivo, 'w+')
        f.write(gv)
        print('Ok.', len(self.nodos), 'nodos,', len(self.aristas), 'aristas')

    def abrir(self, archivo):
        print('Leyendo', archivo, ' ...', end='')
        f = open(archivo, 'r')
        lines = f.readlines()
        for i in range(1, len(lines)):
            tokens = lines[i].split(' ')
            if len(tokens) < 3:
                continue
            tokens[2] = tokens[2].rstrip(';\n')
            self.agregarArista(tokens[0] + tokens[1] + tokens[2], tokens[0], tokens[2])

        print('Ok.', len(self.nodos), 'nodos,', len(self.aristas), 'aristas')
