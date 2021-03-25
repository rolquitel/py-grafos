import pygame

from util import draw_dashed_line
from names import *


class Edge:
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
        self.atrib = {
            ATTR_STYLE: {
                STYLE_COLOR: (200, 200, 200),
                STYLE_THICKNESS: 1,
                STYLE_DOTTED: False,
                STYLE_SIZE: 10,
                STYLE_SHOW_ID: False,
                STYLE_ANTIALIAS: False,
            },
        }

    def __str__(self):
        """
        Convertir arista en str
        :return: representación textual de la arista
        """
        return self.id

    def style(self, est, val):
        """
        Establece un valor de estilo en la arista
        :param est: llave del estilo
        :param val: valor del estilo
        :return:
        """
        self.atrib[ATTR_STYLE][est] = val

    def draw(self, viewport, transform=None):
        """
        Dibuja la arista en la pantalla de acuerdo a los parámetros y a sus propios atrib
        :param viewport:
        :return:
        """
        surf = viewport.frame.surf
        # n0 = g.transform.transformar(self.n0.atrib[nodo.ATTR_POS])
        # n1 = g.transform.transformar(self.n1.atrib[nodo.ATTR_POS])
        n0 = self.n0.attr[ATTR_POS_VP]
        n1 = self.n1.attr[ATTR_POS_VP]
        if self.atrib[ATTR_STYLE][STYLE_DOTTED]:
            draw_dashed_line(surf, self.atrib[ATTR_STYLE][STYLE_COLOR],
                             n0,
                             n1,
                             self.atrib[ATTR_STYLE][STYLE_THICKNESS],
                             self.atrib[ATTR_STYLE][STYLE_SIZE])
        elif self.atrib[ATTR_STYLE][STYLE_ANTIALIAS]:
            pygame.draw.aaline(surf, self.atrib[ATTR_STYLE][STYLE_COLOR],
                               n0,
                               n1,
                               self.atrib[ATTR_STYLE][STYLE_THICKNESS])
        else:
            pygame.draw.line(surf, self.atrib[ATTR_STYLE][STYLE_COLOR],
                             n0,
                             n1,
                             self.atrib[ATTR_STYLE][STYLE_THICKNESS])

        try:
            if self.atrib[ATTR_STYLE][STYLE_SHOW_ID]:
                pos = (n0 + n1) / 2
                lon = len(str(self.id)) * viewport.tam_fuente / 4
                viewport.frame.text((pos[0] - lon, pos[1] - viewport.tam_fuente / 3),
                                    self.atrib[ATTR_STYLE][STYLE_COLOR],
                                    str(self.id))
        except:
            print('Except: g.fuente.render_to()')
