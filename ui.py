import math
import numpy
import pygame

import layout
import grafo


class Frame:
    def __init__(self):
        self.views = []
        self.surf = None
        self.key_listeners = []
        self.tam_fuente = 10
        self.fuente = None

    def set_font(self, ttf='fonts/courier_b.ttf', tam=10):
        self.tam_fuente = tam
        self.fuente = pygame.freetype.Font(ttf, tam)

    def text(self, pos, col, cad):
        self.fuente.render_to(self.surf, pos, cad, col)

    def add_viewport(self, vp):
        self.views.append(vp)
        vp.frame = self

    def add_key_listerer(self, listener):
        self.key_listeners.append(listener)

    def manage_input(self):
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
        :param g: grafo a dibujar
        :param res: resolución
        :return:
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


class Viewport:
    out_rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
    mid_rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
    rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
    grafo = None
    layinout = False
    frame = None
    layout = None
    margen = 0

    def __init__(self, g):
        # self.rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
        self.grafo = g
        # self.layinout = False
        # self.frame = frame
        # self.layout = layout.BarnesHut(g)

        # self.frame.add_viewport(self)

    def set_rect(self, pos, tam, margen=0.05):
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
        return self.rect[1] - self.rect[0]

    def zoom(self, z):
        center = (self.rect[1] + self.rect[0]) / 2
        self.rect[0] = (self.rect[0] - center) * z + center
        self.rect[1] = (self.rect[1] - center) * z + center

    def pan(self, eje, desp):
        self.rect[0][eje] = self.rect[0][eje] + desp
        self.rect[1][eje] = self.rect[1][eje] + desp

    def draw(self):
        if self.layinout:
            self.layinout = not self.layout.paso()

        tam_out_rect = self.out_rect[1] - self.out_rect[0]
        tam_mid_rect = self.mid_rect[1] - self.mid_rect[0]

        pygame.draw.rect(self.frame.surf,
                         self.grafo.atrib[grafo.Grafo.ATTR_ESTILO][grafo.Grafo.ESTILO_FONDO],
                         (self.out_rect[0], tam_out_rect),
                         width=0)
        pygame.draw.rect(self.frame.surf,
                         (128, 128, 128),
                         (self.mid_rect[0], tam_mid_rect),
                         width=1)

        if self.grafo is not None:
            self.grafo.dibujar(self)

            cad = str(len(self.grafo.nodos.values())) + ' nodos y ' + str(len(self.grafo.aristas.values())) + ' aristas'
            self.frame.text(self.mid_rect[0] + 10, (128, 128, 128), cad)

    def key_manage(self, pressed):
        print(self.__class__)
