import numpy
import pygame
import pygame.freetype


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


class Extent:
    def __init__(self, rect):
        self.rect = rect

    def tam(self):
        return self.rect[1] - self.rect[0]
