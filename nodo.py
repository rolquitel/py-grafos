import random

import numpy
import pygame


ATTR_VECINOS = '__vecinos__'
ATTR_ARISTAS = '__aristas__'
ATTR_ESTILO = '__estilo__'
ATTR_POS = '__pos__'
ATTR_POS_VP = '__POS__'
ATTR_DESP = '__desp__'

FORMA_CIRCULAR = 'circulo'
FORMA_CUADRADA = 'cuadro'
FORMA_CRUZ = 'cruz'
FORMA_TACHE = 'tache'
FORMA_TRIANGULAR = 'triangulo'

ESTILO_FORMA = 'forma'
ESTILO_TAMANO = 'tamaño'
ESTILO_COL_BORDE = 'color_borde'
ESTILO_COL_RELLENO = 'color_relleno'
ESTILO_GROSOR = 'grosor'
ESTILO_RELLENO = 'relleno?'
ESTILO_BORDE = 'borde?'
ESTILO_ESCALAR = 'escalar?'
ESTILO_MOSTRAR_ID = 'mostrarId?'

class Nodo:
    """
    Clase nodo
    """
    

    def __init__(self, id):
        """
        Constructor
        :param id: identificador único del nodo
        """
        self.id = id
        self.atrib = {
            ATTR_ARISTAS: [],
            ATTR_VECINOS: [],
            ATTR_POS: numpy.array([random.random(), random.random()]),
            ATTR_ESTILO: {
                ESTILO_FORMA: FORMA_CIRCULAR,
                ESTILO_TAMANO: 10,
                ESTILO_COL_BORDE: (50, 50, 50),
                ESTILO_COL_RELLENO: (255, 255, 255),
                ESTILO_GROSOR: 1,
                ESTILO_RELLENO: True,
                ESTILO_BORDE: True,
                ESTILO_ESCALAR: False,
                ESTILO_MOSTRAR_ID: False,
            },
        }

    def __str__(self):
        """
        Convertir el nodo a str
        :return: representación textual del nodo
        """
        retVal = self.id + ': '
        for a in self.atrib.values():
            retVal += str(a) + ','
        return retVal

    def estilo(self, est, val):
        """
        Establece un valor de estilo en el nodo
        :param est: llave del estilo
        :param val: valor del estilo
        :return:
        """
        self.atrib[ATTR_ESTILO][est] = val

    def dibujar(self, viewport, transform=None):
        """
        Dibuja el nodo en el viewport de acuerdo a sus propios atrib
        :param viewport: descriptor de la zona de dibujo
        :return:
        """
        pos = self.atrib[ATTR_POS_VP]
        if self.atrib[ATTR_ESTILO][ESTILO_ESCALAR] and transform is not None:
            tam2 = self.atrib[ATTR_ESTILO][ESTILO_TAMANO] * transform.escala
        else:
            tam2 = self.atrib[ATTR_ESTILO][ESTILO_TAMANO]

        tam = tam2 / 2

        if self.atrib[ATTR_ESTILO][ESTILO_FORMA] == FORMA_CIRCULAR:
            if self.atrib[ATTR_ESTILO][ESTILO_RELLENO]:
                pygame.draw.ellipse(viewport.frame.surf,
                                    self.atrib[ATTR_ESTILO][ESTILO_COL_RELLENO],
                                    (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                    width=0)
            if self.atrib[ATTR_ESTILO][ESTILO_BORDE]:
                pygame.draw.ellipse(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                                    (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                    width=self.atrib[ATTR_ESTILO][ESTILO_GROSOR])

        elif self.atrib[ATTR_ESTILO][ESTILO_FORMA] == FORMA_CUADRADA:
            if self.atrib[ATTR_ESTILO][ESTILO_RELLENO]:
                pygame.draw.rect(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_RELLENO],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=0)
            if self.atrib[ATTR_ESTILO][ESTILO_BORDE]:
                pygame.draw.rect(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=self.atrib[ATTR_ESTILO][ESTILO_GROSOR])

        elif self.atrib[ATTR_ESTILO][ESTILO_FORMA] == FORMA_TRIANGULAR:
            if self.atrib[ATTR_ESTILO][ESTILO_RELLENO]:
                pygame.draw.polygon(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_RELLENO],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=0)
            if self.atrib[ATTR_ESTILO][ESTILO_BORDE]:
                pygame.draw.polygon(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=self.atrib[ATTR_ESTILO][ESTILO_GROSOR])

        elif self.atrib[ATTR_ESTILO][ESTILO_FORMA] == FORMA_TACHE:
            pygame.draw.line(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                             (pos[0] - tam, pos[1] - tam),
                             (pos[0] + tam, pos[1] + tam),
                             width=self.atrib[ATTR_ESTILO][ESTILO_GROSOR])
            pygame.draw.line(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                             (pos[0] - tam, pos[1] + tam),
                             (pos[0] + tam, pos[1] - tam),
                             width=self.atrib[ATTR_ESTILO][ESTILO_GROSOR])

        elif self.atrib[ATTR_ESTILO][ESTILO_FORMA] == FORMA_CRUZ:
            pygame.draw.line(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                             (pos[0], pos[1] - tam),
                             (pos[0], pos[1] + tam),
                             width=self.atrib[ATTR_ESTILO][ESTILO_GROSOR])
            pygame.draw.line(viewport.frame.surf, self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                             (pos[0] - tam, pos[1]),
                             (pos[0] + tam, pos[1]),
                             width=self.atrib[ATTR_ESTILO][ESTILO_GROSOR])

        if self.atrib[ATTR_ESTILO][ESTILO_MOSTRAR_ID]:
            lon = len(str(self.id)) * viewport.tam_fuente / 4
            try:
                viewport.text((pos[0] - lon, pos[1] - viewport.tam_fuente / 3),
                              self.atrib[ATTR_ESTILO][ESTILO_COL_BORDE],
                              str(self.id))
            except:
                print('Except: g.fuente.render_to()')
