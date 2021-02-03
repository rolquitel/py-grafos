import math
import pygame
import numpy

def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
    origin = numpy.array(start_pos)
    target = numpy.array(end_pos)
    displacement = target - origin
    length = numpy.linalg.norm(displacement)
    slope = displacement / length

    for index in range(0, int(length/dash_length), 2):
        start = origin + (slope *    index    * dash_length)
        end   = origin + (slope * (index + 1) * dash_length)
        pygame.draw.aaline(surf, color, start, end, width)


def arco(surf, color, a, b):
    try:
        alpha = math.pi / 3
        a = numpy.array(a)
        b = numpy.array(b)
        r = numpy.linalg.norm(a - b)
        p = (a + b) / 2
        m = -(a[0] - b[0]) / (a[1] - b[1])
        theta = math.atan(m)
        rho = r * math.sin((math.pi - alpha) / 2)
        c = numpy.array([p[0] + rho * math.cos(theta), p[1] + rho * math.sin(theta)])
        ma = (c[1] - a[1]) / (c[0] - a[0])
        mb = (c[1] - b[1]) / (c[0] - b[0])
        i = numpy.array([ c[0] - r, c[1] - r])

        # pygame.draw.circle(surf, color, a, 5)
        # pygame.draw.circle(surf, color, b, 5)
        # pygame.draw.circle(surf, (200, 0, 0), c, 5, 1)
        # pygame.draw.circle(surf, (200, 0, 0), c, r, 1)
        pygame.draw.arc(surf, color, (i, (2*r, 2*r)), math.atan(-ma) + math.pi, math.atan(-mb) + math.pi)
    except ZeroDivisionError:
        pygame.draw.line(surf, color, a, b)


#################################################
class Arista:
    """
    Clase arista
    """

    def __init__(self, source, target, id):
        """
        Constructor
        :param source: nodo fuente
        :param target: nodo destino
        :param id: identificador de la arista
        """
        self.n0 = source
        self.n1 = target
        self.id = id
        self.atributos = {
            'estilo.color' : (200, 200, 200),
            'estilo.grosor' : 1,
            'estilo.discontinuo?': False,
            'estilo.tamaño': 10,
            'estilo.mostrarId?' : True,
        }

    def __str__(self):
        """
        Convertir arista en str
        :return: representación textual de la arista
        """
        return self.id

    def getID(self):
        return self.id

    def draw(self, g):
        """
        Dibuja la arista en la pantalla de acuerdo a los parámetros y a sus propios atributos
        :param scr: handle de la pantalla
        :param scale: escala actual
        :param origin: valor del origen
        :return:
        """
        if self.atributos['estilo.discontinuo?']:
            draw_dashed_line(g.screen, self.atributos['estilo.color'],
                             g.escala * (self.n0.atributos['pos']) + g.origen,
                             g.escala * (self.n1.atributos['pos']) + g.origen,
                             self.atributos['estilo.grosor'],
                             self.atributos['estilo.tamaño'])
        else:
            pygame.draw.aaline(g.screen, self.atributos['estilo.color'],
                               g.escala * (self.n0.atributos['pos']) + g.origen,
                               g.escala * (self.n1.atributos['pos']) + g.origen,
                               self.atributos['estilo.grosor'])
            # arco(g.screen, self.atributos['estilo.color'],
            #      g.escala * (self.n0.atributos['pos']) + g.origen,
            #      g.escala * (self.n1.atributos['pos']) + g.origen
            #      )

        pos = (g.escala * ((self.n0.atributos['pos'] + self.n1.atributos['pos']) / 2) + g.origen)
        lon = len(str(self.id)) * g.tam_fuente / 4
        try:
            g.fuente.render_to(g.screen, (pos[0] - lon, pos[1] - g.tam_fuente / 3), str(self.id),
                               self.atributos['estilo.color'])
        except:
            print('Except: g.fuente.render_to()')
