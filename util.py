import math
import numpy
import pygame
import pygame.freetype
import layout
import arista


def dibujar_linea_punteada(surf, color, start_pos, end_pos, width=1, dash_length=10):
    origin = numpy.array(start_pos)
    target = numpy.array(end_pos)
    displacement = target - origin
    length = numpy.linalg.norm(displacement)
    slope = displacement / length

    for index in range(0, int(length / dash_length), 2):
        start = origin + (slope * index * dash_length)
        end = origin + (slope * (index + 1) * dash_length)
        pygame.draw.aaline(surf, color, start, end, width)


def dibujar_rect_punteado(surf, color, start_pos, end_pos, width=1, dash_length=10):
    dibujar_linea_punteada(surf, color, start_pos, [start_pos[0], end_pos[1]], width, dash_length)
    dibujar_linea_punteada(surf, color, start_pos, [end_pos[0], start_pos[1]], width, dash_length)
    dibujar_linea_punteada(surf, color, end_pos, [start_pos[0], end_pos[1]], width, dash_length)
    dibujar_linea_punteada(surf, color, end_pos, [end_pos[0], start_pos[1]], width, dash_length)


class Transformacion:
    """
    Clase para transformar dado un espacio real, denotado por una extensión, y un viewport
    """

    def __init__(self, ext, vp):
        """
        Constructor de la clase
        :param ext: extensión del espacio real
        :param vp: viewport
        """
        self.viewport = vp
        self.extent = ext
        self.T = vp[1] - vp[0]  # tamaño del viewport
        self.t = ext[1] - ext[0]  # tamaño del espacio

        Sx = self.T[0] / self.t[0]  # escala en x
        Sy = self.T[1] / self.t[1]  # escala en y

        """
        Lo siguiente se hace para que se mantenga la relación de aspecto de forma tal que pueda hacer un desplazamiento
        de tal forma que el espacio quede centrado en el eje más pequeño
        """
        if Sx > Sy:
            self.escala = Sy
            desp = (Sx - Sy) / (2 * Sx)
            self.offset = numpy.array([self.T[0] * desp, 0])
        else:
            self.escala = Sx
            desp = (Sy - Sx) / (2 * Sy)
            self.offset = numpy.array([0, self.T[1] * desp])

    def transformar(self, punto):
        # punto = numpy.array(punto)
        return self.escala * (punto - self.extent[0]) + self.viewport[0] + self.offset


class Viewport:
    def __init__(self):
        self.rect = numpy.array([numpy.array([0, 0]), numpy.array([100, 100])])
        self.tam_fuente = 10
        # self.set_font()

    def set_font(self, ttf='fonts/courier_b.ttf', tam=10):
        self.tam_fuente = tam
        self.fuente = pygame.freetype.Font(ttf, tam)

    def tam(self):
        return self.rect[1] - self.rect[0]

    def zoom(self, z):
        center = (self.rect[1] + self.rect[0]) / 2
        self.rect[0] = (self.rect[0] - center) * z + center
        self.rect[1] = (self.rect[1] - center) * z + center

    def pan(self, eje, desp):
        self.rect[0][eje] = self.rect[0][eje] + desp
        self.rect[1][eje] = self.rect[1][eje] + desp

    def text(self, pos, col, cad):
        self.fuente.render_to(self.surf, pos, cad, col)

    def manage_input(self):
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_SPACE]:
                    self.pause = not self.pause
                elif pressed[pygame.K_b]:
                    if not self.layinout:
                        self.layinout = True
                        self.layout = layout.BarnesHut(self.grafo)
                        self.layout.umbral_convergencia = 1.0
                elif pressed[pygame.K_s]:
                    if not self.layinout:
                        self.layinout = True
                        self.layout = layout.Spring(self.grafo)
                elif pressed[pygame.K_f]:
                    if not self.layinout:
                        self.layinout = True
                        self.layout = layout.FruchtermanReingold(self.grafo)
                elif pressed[pygame.K_ESCAPE]:
                    self.layinout = False
                elif pressed[pygame.K_a]:
                    for a in self.grafo.aristas.values():
                        a.atrib[arista.Arista.ATTR_ESTILO][arista.Arista.ESTILO_ANTIALIAS] = \
                            not a.atrib[arista.Arista.ATTR_ESTILO][arista.Arista.ESTILO_ANTIALIAS]
                elif pressed[pygame.K_r]:
                    if not self.layinout:
                        layout.Random(self.grafo).ejecutar()
                elif pressed[pygame.K_g]:
                    if not self.layinout:
                        layout.Grid(self.grafo).ejecutar()
                elif pressed[pygame.K_PLUS]:
                    self.zoom(1.5)
                elif pressed[pygame.K_MINUS]:
                    self.zoom(1 / 1.5)
                elif pressed[pygame.K_LEFT]:
                    self.pan(0, -10)
                elif pressed[pygame.K_RIGHT]:
                    self.pan(0, 10)
                elif pressed[pygame.K_UP]:
                    self.pan(1, -10)
                elif pressed[pygame.K_DOWN]:
                    self.pan(1, 10)

            if event.type == pygame.QUIT:
                layout.parar_layout = True
                self.running = False

            # mouseClick = pygame.mouse.get_pressed()
            # if sum(mouseClick) > 0:
            #     posX, posY = pygame.mouse.get_pos()
            #     celX, celY = int(np.floor(posX / dim)), int(np.floor(posY / dim) )
            #     newGameState[celX, celY] = 1

    def show(self, g, res):
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
        res = numpy.array(res)
        self.rect = [marco * res, (1 - marco) * res]
        self.layinout = False
        self.grafo = g

        self.layout = layout.Random(g)
        self.layout.ejecutar()

        fpsClock = pygame.time.Clock()

        while self.running:
            self.manage_input()

            if self.pause:
                continue

            if self.layinout:
                self.layinout = not self.layout.paso()

            self.grafo.dibujar(self)

            cad = str(len(g.nodos.values())) + ' nodos y ' + str(len(g.aristas.values())) + ' aristas'
            self.text((10, 10), (128, 128, 128), cad)
            cad = str(math.ceil(1000 / fpsClock.tick(CPS))) + ' cps'
            self.text((res[0] - 50, res[1] - 15), (128, 128, 128), cad)

            pygame.display.flip()


class Extent:
    def __init__(self, rect):
        self.rect = rect

    def tam(self):
        return self.rect[1] - self.rect[0]
