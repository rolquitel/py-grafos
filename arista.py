import math
import pygame
import numpy

import util
from nodo import Nodo
from util import dibujar_linea_punteada


class Arista:
    """
    Clase arista
    """
    ATTR_ESTILO = '__estilo__'

    FORMA_CIRCULAR = 'circulo'
    FORMA_CUADRADA = 'cuadro'
    FORMA_CRUZ = 'cruz'
    FORMA_TACHE = 'tache'
    FORMA_TRIANGULAR = 'triangulo'

    ESTILO_COLOR = '_color'
    ESTILO_GROSOR = '_grosor'
    ESTILO_DISCONTINUO = '_discontinuo?'
    ESTILO_TAMANO = '_tamaño'
    ESTILO_MOSTRAR_ID = '_mostrarId?'
    ESTILO_ANTIALIAS = '_antialias'

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
            Arista.ATTR_ESTILO: {
                Arista.ESTILO_COLOR: (200, 200, 200),
                Arista.ESTILO_GROSOR: 1,
                Arista.ESTILO_DISCONTINUO: False,
                Arista.ESTILO_TAMANO: 10,
                Arista.ESTILO_MOSTRAR_ID: False,
                Arista.ESTILO_ANTIALIAS: False,
            },
        }

    def __str__(self):
        """
        Convertir arista en str
        :return: representación textual de la arista
        """
        return self.id

    def estilo(self, est, val):
        """
        Establece un valor de estilo en la arista
        :param est: llave del estilo
        :param val: valor del estilo
        :return:
        """
        self.atrib[Arista.ATTR_ESTILO][est] = val

    def dibujar(self, viewport, transform=None):
        """
        Dibuja la arista en la pantalla de acuerdo a los parámetros y a sus propios atrib
        :param viewport:
        :return:
        """
        # n0 = g.transform.transformar(self.n0.atrib[Nodo.ATTR_POS])
        # n1 = g.transform.transformar(self.n1.atrib[Nodo.ATTR_POS])
        n0 = self.n0.atrib[Nodo.ATTR_POS_VP]
        n1 = self.n1.atrib[Nodo.ATTR_POS_VP]
        if self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_DISCONTINUO]:
            dibujar_linea_punteada(viewport.surf, self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR],
                                   n0,
                                   n1,
                                   self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_GROSOR],
                                   self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_TAMANO])
        elif self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_ANTIALIAS]:
            pygame.draw.aaline(viewport.surf, self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR],
                               n0,
                               n1,
                               self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_GROSOR])
        else:
            pygame.draw.line(viewport.surf, self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR],
                             n0,
                             n1,
                             self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_GROSOR])

        try:
            if self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_MOSTRAR_ID]:
                pos = (n0 + n1) / 2
                lon = len(str(self.id)) * viewport.tam_fuente / 4
                viewport.text((pos[0] - lon, pos[1] - viewport.tam_fuente / 3),
                              self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR],
                              str(self.id))
        except:
            print('Except: g.fuente.render_to()')
