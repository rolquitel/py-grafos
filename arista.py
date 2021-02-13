import math
import pygame
import numpy

from util import dibujar_linea_punteada


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
            'estilo.mostrarId?' : False,
            'estilo.antialias?': False,
        }

    def __str__(self):
        """
        Convertir arista en str
        :return: representación textual de la arista
        """
        return self.id

    def obtID(self):
        return self.id

    def dibujar(self, g):
        """
        Dibuja la arista en la pantalla de acuerdo a los parámetros y a sus propios atributos
        :param scr: handle de la pantalla
        :param scale: escala actual
        :param origin: valor del origen
        :return:
        """
        n0 = g.transformacion.transformar(self.n0.atributos['pos'])
        n1 = g.transformacion.transformar(self.n1.atributos['pos'])
        if self.atributos['estilo.discontinuo?']:
            dibujar_linea_punteada(g.screen, self.atributos['estilo.color'],
                                   n0,
                                   n1,
                                   self.atributos['estilo.grosor'],
                                   self.atributos['estilo.tamaño'])
        elif self.atributos['estilo.antialias?']:
            pygame.draw.aaline(g.screen, self.atributos['estilo.color'],
                               n0,
                               n1,
                               self.atributos['estilo.grosor'])
        else:
            pygame.draw.line(g.screen, self.atributos['estilo.color'],
                               n0,
                               n1,
                               self.atributos['estilo.grosor'])
            # arco(g.screen, self.atributos['estilo.color'],
            #      g.escala * (self.n0.atributos['pos']) + g.origen,
            #      g.escala * (self.n1.atributos['pos']) + g.origen
            #      )


        try:
            if self.atributos['estilo.mostrarId?']:
                pos = (g.escala * ((self.n0.atributos['pos'] + self.n1.atributos['pos']) / 2) + g.origen)
                lon = len(str(self.id)) * g.tam_fuente / 4
                g.fuente.render_to(g.screen, (pos[0] - lon, pos[1] - g.tam_fuente / 3), str(self.id), self.atributos['estilo.color'])
        except:
            print('Except: g.fuente.render_to()')
