import math
import random
import threading
import time
import numpy
import pygame
import pygame.freetype

import layout
from arista import Arista
from nodo import Nodo
from quadtree import QuadTree, Rectangulo, Punto, Circulo
from util import dibujar_rect_punteado, Transformacion

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
            'estilo.mostrarExtension?': False,
        }
        self.threading = False

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
        for e in self.aristas.values():
            n0 = e.n0.id
            n1 = e.n1.id
            retVal += n0 + ' -> ' + n1 + ';\n'
        retVal += '}\n'

        return retVal

    def calcular_limites(self):
        I = numpy.array([math.inf, math.inf])
        F = numpy.array([-math.inf, -math.inf])
        for v in self.nodos.values():
            I[0] = min(I[0], v.atributos['pos'][0])
            I[1] = min(I[1], v.atributos['pos'][1])
            F[0] = max(F[0], v.atributos['pos'][0])
            F[1] = max(F[1], v.atributos['pos'][1])

        self.I = I
        self.F = F

        self.transformacion = Transformacion(self.I, self.F, [0, 0], self.res, 0.9)

    def dibujar(self):
        """
        Dibujar el grafo, si se llama continuamente va calculando el layout del mismo
        :param screen: handle del área de dibujo
        :return:
        """

        if self.atributos['estilo.mostrarExtension?']:
            I = self.transformacion.transformar(self.I)
            F = self.transformacion.transformar(self.F)
            dibujar_rect_punteado(self.screen, (128, 128, 128), I, F)

        for a in self.aristas.values():
            a.dibujar(self)

        for v in self.nodos.values():
            v.dibujar(self)

    def posicionar_nodos_al_azar(self):
        origen = self.res / 2
        for v in self.nodos.values():
            v.atributos['pos'] = numpy.array(
                [random.randint(-origen[0], origen[0]), random.randint(-origen[1], origen[1])])

    def posicionar_nodos_malla(self):
        lado = int(math.ceil(math.sqrt(len(self.nodos))))
        tam = self.res / (lado + 2)
        origen = self.res / 2

        n = 0
        for v in self.nodos.values():
            x = tam[0] * ((n % lado) + 1) - origen[0]
            y = tam[1] * ((n / lado) + 1) - origen[1]
            v.atributos['pos'] = numpy.array([x, y])
            n = n + 1

    def posicionar_nodos(self):
        # self.posicionar_nodos_al_azar()
        self.posicionar_nodos_malla()

        self.calcular_limites()

    def mostrar(self, res, lyout=None):
        pause = False
        running = True
        acomodando = True
        CPS = 30

        pygame.init()
        self.screen = pygame.display.set_mode(res)
        self.res = numpy.array(res)
        self.origen = self.res / 2
        self.escala = 1
        self.tam_fuente = 10
        self.fuente = pygame.freetype.Font('fonts/courier_b.ttf', self.tam_fuente)
        self.layout = lyout
        self.antialias = False

        self.posicionar_nodos()

        if lyout == None:
            self.layout = layout.BarnesHut(self, res)

        if self.threading:
            t = threading.Thread(target=lyout.ejecutar)
            t.start()

        fpsClock = pygame.time.Clock()

        while running:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.KEYDOWN:
                    pressed = pygame.key.get_pressed()
                    if pressed[pygame.K_SPACE]:
                        pause = not pause

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

            self.screen.fill(self.atributos['estilo.fondo'])

            if not self.threading:
                self.layout.paso()

            if self.layout.convergio and not self.antialias:
                self.antialias = True
                for a in self.aristas.values():
                    a.atributos['estilo.antialias?'] = True

            self.dibujar()

            cad = str(len(self.nodos.values())) + ' nodos y ' + str(len(self.aristas.values())) + ' aristas'
            self.fuente.render_to(self.screen, (10, 10), cad, (128, 128, 128))
            cad = str(math.ceil(1000 / fpsClock.tick(CPS))) + ' cps'
            self.fuente.render_to(self.screen, (res[0] - 50, res[1] - 15), cad, (128, 128, 128))

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
            self.agregarArista(tokens[0]+tokens[1]+tokens[2], tokens[0], tokens[2])

        print('Ok.', len(self.nodos), 'nodos,', len(self.aristas), 'aristas')
