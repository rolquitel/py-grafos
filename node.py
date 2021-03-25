import random

import numpy
import pygame

from names import *


class Node:
    """
    Clase nodo
    """

    def __init__(self, id):
        """
        Constructor
        :param id: identificador único del nodo
        """
        self.id = id
        self.attr = {
            ATTR_EDGES: [],
            ATTR_NEIGHBORS: [],
            ATTR_POS: numpy.array([random.random(), random.random()]),
            ATTR_STYLE: {
                STYLE_FORM: FORM_CIRCLE,
                STYLE_SIZE: 10,
                STYLE_BORDERCOLOR: (50, 50, 50),
                STYLE_FILLCOLOR: (255, 255, 255),
                STYLE_THICKNESS: 1,
                STYLE_FILLED: True,
                STYLE_BORDERED: True,
                STYLE_SCALED: False,
                STYLE_SHOW_ID: False,
            },
        }

    def __str__(self):
        """
        Convertir el nodo a str
        :return: representación textual del nodo
        """
        retVal = self.id + ': '
        for a in self.attr.values():
            retVal += str(a) + ','
        return retVal

    def style(self, est, val):
        """
        Establece un valor de estilo en el nodo
        :param est: llave del estilo
        :param val: valor del estilo
        :return:
        """
        self.attr[ATTR_STYLE][est] = val

    def draw(self, viewport, transform=None):
        """
        Dibuja el nodo en el viewport de acuerdo a sus propios atrib
        :param viewport: descriptor de la zona de dibujo
        :return:
        """
        pos = self.attr[ATTR_POS_VP]
        if self.attr[ATTR_STYLE][STYLE_SCALED] and transform is not None:
            tam2 = self.attr[ATTR_STYLE][STYLE_SIZE] * transform.escala
        else:
            tam2 = self.attr[ATTR_STYLE][STYLE_SIZE]

        tam = tam2 / 2

        if self.attr[ATTR_STYLE][STYLE_FORM] == FORM_CIRCLE:
            if self.attr[ATTR_STYLE][STYLE_FILLED]:
                pygame.draw.ellipse(viewport.frame.surf,
                                    self.attr[ATTR_STYLE][STYLE_FILLCOLOR],
                                    (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                    width=0)
            if self.attr[ATTR_STYLE][STYLE_BORDERED]:
                pygame.draw.ellipse(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                                    (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                    width=self.attr[ATTR_STYLE][STYLE_THICKNESS])

        elif self.attr[ATTR_STYLE][STYLE_FORM] == FORM_SQUARE:
            if self.attr[ATTR_STYLE][STYLE_FILLED]:
                pygame.draw.rect(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_FILLCOLOR],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=0)
            if self.attr[ATTR_STYLE][STYLE_BORDERED]:
                pygame.draw.rect(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=self.attr[ATTR_STYLE][STYLE_THICKNESS])

        elif self.attr[ATTR_STYLE][STYLE_FORM] == FORM_TRIANGLE:
            if self.attr[ATTR_STYLE][STYLE_FILLED]:
                pygame.draw.polygon(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_FILLCOLOR],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=0)
            if self.attr[ATTR_STYLE][STYLE_BORDERED]:
                pygame.draw.polygon(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=self.attr[ATTR_STYLE][STYLE_THICKNESS])

        elif self.attr[ATTR_STYLE][STYLE_FORM] == FORM_CROSSOUT:
            pygame.draw.line(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                             (pos[0] - tam, pos[1] - tam),
                             (pos[0] + tam, pos[1] + tam),
                             width=self.attr[ATTR_STYLE][STYLE_THICKNESS])
            pygame.draw.line(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                             (pos[0] - tam, pos[1] + tam),
                             (pos[0] + tam, pos[1] - tam),
                             width=self.attr[ATTR_STYLE][STYLE_THICKNESS])

        elif self.attr[ATTR_STYLE][STYLE_FORM] == FORM_CROSS:
            pygame.draw.line(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                             (pos[0], pos[1] - tam),
                             (pos[0], pos[1] + tam),
                             width=self.attr[ATTR_STYLE][STYLE_THICKNESS])
            pygame.draw.line(viewport.frame.surf, self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                             (pos[0] - tam, pos[1]),
                             (pos[0] + tam, pos[1]),
                             width=self.attr[ATTR_STYLE][STYLE_THICKNESS])

        if self.attr[ATTR_STYLE][STYLE_SHOW_ID]:
            lon = len(str(self.id)) * viewport.tam_fuente / 4
            try:
                viewport.text((pos[0] - lon, pos[1] - viewport.tam_fuente / 3),
                              self.attr[ATTR_STYLE][STYLE_BORDERCOLOR],
                              str(self.id))
            except:
                print('Except: g.fuente.render_to()')
