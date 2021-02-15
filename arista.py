import math
import pygame
import numpy

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
        self.atrib[Arista.ATTR_ESTILO][est] = val

    def dibujar(self, g):
        """
        Dibuja la arista en la pantalla de acuerdo a los parámetros y a sus propios atrib
        :param scr: handle de la pantalla
        :param scale: escala actual
        :param origin: valor del origen
        :return:
        """
        n0 = g.transformacion.transformar(self.n0.atrib['pos'])
        n1 = g.transformacion.transformar(self.n1.atrib['pos'])
        if self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_DISCONTINUO]:
            dibujar_linea_punteada(g.screen, self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR],
                                   n0,
                                   n1,
                                   self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_GROSOR],
                                   self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_TAMANO])
        elif self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_ANTIALIAS]:
            pygame.draw.aaline(g.viewport.surf, self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR],
                               n0,
                               n1,
                               self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_GROSOR])
        else:
            pygame.draw.line(g.viewport.surf, self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR],
                             n0,
                             n1,
                             self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_GROSOR])

        try:
            if self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_MOSTRAR_ID]:
                pos = (g.escala * ((self.n0.atrib['pos'] + self.n1.atrib['pos']) / 2) + g.origen)
                lon = len(str(self.id)) * g.tam_fuente / 4
                g.fuente.render_to(g.screen,
                                   (pos[0] - lon, pos[1] - g.tam_fuente / 3), str(self.id),
                                   self.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR])
        except:
            print('Except: g.fuente.render_to()')
