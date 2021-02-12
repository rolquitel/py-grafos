import math

import numpy
import pygame


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
        i = numpy.array([c[0] - r, c[1] - r])

        # pygame.draw.circle(surf, color, a, 5)
        # pygame.draw.circle(surf, color, b, 5)
        # pygame.draw.circle(surf, (200, 0, 0), c, 5, 1)
        # pygame.draw.circle(surf, (200, 0, 0), c, r, 1)
        pygame.draw.arc(surf, color, (i, (2 * r, 2 * r)), math.atan(-ma) + math.pi, math.atan(-mb) + math.pi)
    except ZeroDivisionError:
        pygame.draw.line(surf, color, a, b)


class Transformacion:
    def __init__(self, i, f, I, F, contenido=1):
        self.i = i = numpy.array(i)
        self.f = f = numpy.array(f)
        self.I = I = numpy.array(I)
        self.F = F = numpy.array(F)
        self.t = f - i
        self.T = F - I
        self.contenido = contenido

        marco = (1 - contenido) / 2

        Sx = (F[0] - I[0]) / (f[0] - i[0])
        Sy = (F[0] - I[0]) / (f[1] - i[1])

        if Sx > Sy:
            self.escala = Sy * contenido
            desp = (Sx - Sy) / (2 * Sx) + marco
            self.offset = numpy.array([self.T[0] * desp, self.T[1] * marco])
        else:
            self.escala = Sx * contenido
            desp = (Sy - Sx) / (2 * Sy) + marco
            self.offset = numpy.array([self.T[0] * marco, self.T[1] * desp])

    def transformar(self, punto):
        punto = numpy.array(punto)
        return self.escala * (punto - self.i) + self.offset
