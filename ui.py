import math
import random

import numpy
import pygame

import layout
import grafo
from arista import Arista
from nodo import Nodo


class Frame:
    """
    Clase para controlar la ventana de pygame
    """
    def __init__(self):
        self.views = []             # lista de viewports a mostrar
        self.surf = None            # surface de dibujo de pygame
        self.key_listeners = []     # lista de controladores de teclas
        self.tam_fuente = 10        # tamaño de la fuente
        self.fuente = None          # fuente para mostrar texto

    def set_font(self, ttf='fonts/courier_b.ttf', tam=10):
        """
        Carga una fuente desde ur archivo TTF al tamaño especificado
        :param ttf: nombre de la fuente
        :param tam: tamaño de la fuente
        :return: None
        """
        self.tam_fuente = tam
        self.fuente = pygame.freetype.Font(ttf, tam)

    def text(self, pos, col, cad):
        """
        Muestra un texto en la pantalla
        :param pos: posición del texto
        :param col: color del texto
        :param cad: texto a mostrar
        :return: None
        """
        self.fuente.render_to(self.surf, pos, cad, col)

    def add_viewport(self, vp):
        """
        Agrega un viewport a la lista para dibujar
        :param vp: viewport a agregar
        :return: None
        """
        self.views.append(vp)
        vp.frame = self

    def add_key_listerer(self, listener):
        """
        Agrega un controlador de teclas
        :param listener: controlador de teclas presionadas
        :return: None
        """
        self.key_listeners.append(listener)

    def manage_input(self):
        """
        Captura y canaliza los eventos de entrada
        :return: None
        """
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                layout.parar_layout = True
                self.running = False

            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_SPACE]:
                    self.pause = not self.pause

                for l in self.key_listeners:
                    l.key_manage(pressed)

    def show(self, res):
        """
        Mostrar grafo en el viewport
        :param res: resolución
        :return: None
        """
        self.pause = False
        self.running = True
        CPS = 60
        marco = 0.05

        pygame.init()
        self.surf = pygame.display.set_mode(res)
        self.set_font()

        fpsClock = pygame.time.Clock()

        while self.running:
            self.manage_input()

            if self.pause:
                continue

            for v in self.views:
                v.draw()

            cad = str(math.ceil(1000 / fpsClock.tick(CPS))) + ' cps'
            self.text((res[0] - 50, res[1] - 15), (128, 128, 128), cad)

            pygame.display.flip()

        pygame.quit()


class Viewport:
    """
    Clase para definir la zona de dibujo
    """
    out_rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
    mid_rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
    rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
    grafo = None
    layinout = False
    frame = None
    layout = None
    margen = 0

    def __init__(self, g):
        """
        Constructor
        :param g: grafo relacionado con el viewport
        """
        self.grafo = g

    def set_rect(self, pos, tam, margen=0.05):
        """
        Establecer dimensiones del viewport
        :param pos: posición del viewpport
        :param tam: tamaño del viewport
        :param margen: porcentaje del area que se toma como margen
        :return: None
        """
        pos = numpy.array(pos)
        tam = numpy.array(tam)
        margen = max(0, margen)
        margen = min(0.4, margen)

        self.margen = margen

        marco_int = tam * margen
        marco_med = tam * (margen / 2)
        self.out_rect = numpy.array([pos, pos + tam])
        self.mid_rect = numpy.array([pos + marco_med, pos + tam - marco_med])
        self.rect = numpy.array([pos + marco_int, pos + tam - marco_int])

    def size(self):
        """
        Calcula el tamaño del viewport
        :return: tamaño del viewport
        """
        return self.rect[1] - self.rect[0]

    def zoom(self, z):
        """
        Escalamiento del viewport
        :param z: valor de la escala, si es menor que 1 -> zoom out, mayor que 1 -> zoom in
        :return: None
        """
        center = (self.rect[1] + self.rect[0]) / 2
        self.rect[0] = (self.rect[0] - center) * z + center
        self.rect[1] = (self.rect[1] - center) * z + center

    def pan(self, eje, desp):
        """
        Desplazamiento del viewport
        :param eje: eje del desplazamiento
        :param desp: valor del desplazamiento
        :return: None
        """
        self.rect[0][eje] = self.rect[0][eje] + desp
        self.rect[1][eje] = self.rect[1][eje] + desp

    def draw(self):
        """
        Dibujar el viewport
        :return: None
        """
        if self.layinout:
        #     self.layinout = not self.layout.paso()
            self.layout.paso()

        tam_out_rect = self.out_rect[1] - self.out_rect[0]
        tam_mid_rect = self.mid_rect[1] - self.mid_rect[0]

        pygame.draw.rect(self.frame.surf,
                         self.grafo.atrib[grafo.ATTR_ESTILO][grafo.ESTILO_FONDO],
                         (self.out_rect[0], tam_out_rect),
                         width=0)
        pygame.draw.rect(self.frame.surf,
                         self.grafo.atrib[grafo.ATTR_ESTILO][grafo.ESTILO_COL_LINEA],
                         (self.mid_rect[0], tam_mid_rect),
                         width=1)

        if self.grafo is not None:
            self.grafo.dibujar(self)

            cad = str(len(self.grafo.nodos.values())) + ' nodos y ' + str(len(self.grafo.aristas.values())) + ' aristas'
            self.frame.text(self.mid_rect[0] + 10,
                            self.grafo.atrib[grafo.ATTR_ESTILO][grafo.ESTILO_COL_LINEA],
                            cad)

    def key_manage(self, pressed):
        """
        Manejo predeterminado de eventos del teclado
        :param pressed: vector de teclas presionadas
        :return: None
        """
        print(self.__class__)


class ColorScheme:
    """
    Clase para describir un esquema de color
    """
    bg_color = (224, 224, 224)
    edge_color = (128, 128, 128)
    fg_color = edge_color
    node_border_color = edge_color
    node_fill_colors = []

    def __init__(self):
        for i in range(256):
            self.node_fill_colors.append((random.randint(32, 224), random.randint(32, 224), random.randint(32, 224)))

    def apply_to_graph(self, graph):
        """
        Aplica el esquema de color al grafo dado
        :param graph: el grafo al que se le aplicará el esquema de color
        :return: None
        """
        for n in graph.nodos.values():
            n.estilo(Nodo.ESTILO_COL_RELLENO, self.node_fill_colors[random.randint(0, len(self.node_fill_colors) - 1)])

        for a in graph.aristas.values():
            a.estilo(Arista.ESTILO_COLOR, self.edge_color)

        graph.estilo(grafo.ESTILO_FONDO, self.bg_color)
        graph.estilo(grafo.ESTILO_APLICADO, self)
        graph.estilo(grafo.ESTILO_COL_LINEA, self.fg_color)


class DarkGrayColorScheme(ColorScheme):
    """
    Clase de esquema de color gris con fondo obscuro
    """
    def __init__(self):
        self.bg_color = (16, 16, 16)
        self.fg_color = (64, 64, 64)
        self.edge_color = self.fg_color
        self.node_border_color = self.fg_color

        self.node_fill_colors = []
        for i in range(32, 224):
            self.node_fill_colors.append((i, i, i))


class LightGrayColorScheme(ColorScheme):
    """
    Clase de esquema de color gris con fondo claro
    """
    def __init__(self):
        self.bg_color = (224, 224, 224)
        self.fg_color = (64, 64, 64)
        self.edge_color = self.fg_color
        self.node_border_color = self.fg_color

        self.node_fill_colors = []
        for i in range(32, 224):
            self.node_fill_colors.append((i, i, i))


class BlueRedColorScheme(ColorScheme):
    """
    Clase con esquema de color de fondo azul obscuro y nodos en tonos de rosa
    """
    def __init__(self):
        self.bg_color = (16, 16, 64)
        self.fg_color = (64, 32, 32)
        self.edge_color = self.fg_color
        self.node_border_color = self.fg_color

        self.node_fill_colors = []
        for i in range(32, 248):
            self.node_fill_colors.append((248, i, i))
