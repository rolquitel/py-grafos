import pygame


class Nodo:
    """
    Clase nodo
    """
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

    def __init__(self, id):
        """
        Constructor
        :param id: identificador único del nodo
        """
        self.id = id
        self.atrib = {
            Nodo.ATTR_ARISTAS: [],
            Nodo.ATTR_VECINOS: [],
            Nodo.ATTR_ESTILO: {
                Nodo.ESTILO_FORMA: Nodo.FORMA_CIRCULAR,
                Nodo.ESTILO_TAMANO: 10,
                Nodo.ESTILO_COL_BORDE: (50, 50, 50),
                Nodo.ESTILO_COL_RELLENO: (255, 255, 255),
                Nodo.ESTILO_GROSOR: 1,
                Nodo.ESTILO_RELLENO: True,
                Nodo.ESTILO_BORDE: True,
                Nodo.ESTILO_ESCALAR: False,
                Nodo.ESTILO_MOSTRAR_ID: False,
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
        self.atrib[Nodo.ATTR_ESTILO][est] = val

    def dibujar(self, g):
        """
        Dibuja el nodo en la pantalla de acuerdo a los parámetros y a sus propios atrib
        :param g:
        :return:
        """
        # pos = g.transformacion.transformar(self.atrib[Nodo.ATTR_POS])
        pos = self.atrib[Nodo.ATTR_POS_VP]
        if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_ESCALAR]:
            tam2 = self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_TAMANO] * g.escala
        else:
            tam2 = self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_TAMANO]

        tam = tam2 / 2

        if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_FORMA] == Nodo.FORMA_CIRCULAR:
            if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_RELLENO]:
                pygame.draw.ellipse(g.viewport.surf,
                                    self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_RELLENO],
                                    (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                    width=0)
            if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_BORDE]:
                pygame.draw.ellipse(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE],
                                    (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                    width=self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_GROSOR])

        elif self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_FORMA] == Nodo.FORMA_CUADRADA:
            if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_RELLENO]:
                pygame.draw.rect(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_RELLENO],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=0)
            if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_BORDE]:
                pygame.draw.rect(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_GROSOR])

        elif self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_FORMA] == Nodo.FORMA_TRIANGULAR:
            if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_RELLENO]:
                pygame.draw.polygon(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_RELLENO],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=0)
            if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_BORDE]:
                pygame.draw.polygon(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_GROSOR])

        elif self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_FORMA] == Nodo.FORMA_TACHE:
            pygame.draw.line(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE],
                             (pos[0] - tam, pos[1] - tam),
                             (pos[0] + tam, pos[1] + tam),
                             width=self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_GROSOR])
            pygame.draw.line(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE],
                             (pos[0] - tam, pos[1] + tam),
                             (pos[0] + tam, pos[1] - tam),
                             width=self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_GROSOR])

        elif self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_FORMA] == Nodo.FORMA_CRUZ:
            pygame.draw.line(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE],
                             (pos[0], pos[1] - tam),
                             (pos[0], pos[1] + tam),
                             width=self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_GROSOR])
            pygame.draw.line(g.viewport.surf, self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE],
                             (pos[0] - tam, pos[1]),
                             (pos[0] + tam, pos[1]),
                             width=self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_GROSOR])

        if self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_MOSTRAR_ID]:
            lon = len(str(self.id)) * g.tam_fuente / 4
            try:
                g.fuente.render_to(g.viewport.surf, (pos[0] - lon, pos[1] - g.tam_fuente / 3), str(self.id),
                                   self.atrib[Nodo.ATTR_ESTILO][Nodo.ESTILO_COL_BORDE])
            except:
                print('Except: g.fuente.render_to()')
