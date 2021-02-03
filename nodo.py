import pygame

class Nodo:
    """
    Clase nodo
    """
    ATTR_VECINOS = '__vecinos__'
    ATTR_ARISTAS = '__aristas__'

    def __init__(self, id):
        """
        Constructor
        :param id: identificador único del nodo
        """
        self.id = id
        self.atributos = {
            Nodo.ATTR_ARISTAS: [],
            Nodo.ATTR_VECINOS: [],
            'estilo.forma' : 'estilo.redondo',
            'estilo.tamaño' : 10,
            'estilo.color_borde': (50, 50, 50),
            'estilo.color_relleno': (255, 255, 255),
            'estilo.grosor' : 1,
            'estilo.relleno?': True,
            'estilo.borde?': True,
            'estilo.escalar?': False,
            'estilo.mostrarId?': False,
        }

    def __str__(self):
        """
        Convertir el nodo a str
        :return: representación textual del nodo
        """
        retVal = self.id + ': '
        for a in self.atributos.values():
            retVal += str(a) + ','
        return retVal

    def draw(self, g):
        """
        Dibuja el nodo en la pantalla de acuerdo a los parámetros y a sus propios atributos
        :param g:
        :return:
        """
        pos = g.escala * self.atributos['pos'] + g.origen
        if self.atributos['estilo.escalar?']:
            tam2 = self.atributos['estilo.tamaño'] * g.escala
        else:
            tam2 = self.atributos['estilo.tamaño']

        tam = tam2 / 2

        if self.atributos['estilo.forma'] == 'estilo.redondo':
            if self.atributos['estilo.relleno?']:
                pygame.draw.ellipse(g.screen, self.atributos['estilo.color_relleno'],
                                    (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                    width=0)
            if self.atributos['estilo.borde?']:
                pygame.draw.ellipse(g.screen, self.atributos['estilo.color_borde'],
                                    (pos[0] - tam, pos[1] - tam , tam2, tam2),
                                    width=self.atributos['estilo.grosor'])

        elif self.atributos['estilo.forma'] == 'estilo.cuadrado':
            if self.atributos['estilo.relleno?']:
                pygame.draw.rect(g.screen, self.atributos['estilo.color_relleno'],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=0)
            if self.atributos['estilo.borde?']:
                pygame.draw.rect(g.screen, self.atributos['estilo.color_borde'],
                                 (pos[0] - tam, pos[1] - tam, tam2, tam2),
                                 width=self.atributos['estilo.grosor'])

        elif self.atributos['estilo.forma'] == 'estilo.triangular':
            if self.atributos['estilo.relleno?']:
                pygame.draw.polygon(g.screen, self.atributos['estilo.color_relleno'],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=0)
            if self.atributos['estilo.borde?']:
                pygame.draw.polygon(g.screen, self.atributos['estilo.color_borde'],
                                    ((pos[0] - tam, pos[1] + tam),
                                     (pos[0], pos[1] - tam),
                                     (pos[0] + tam, pos[1] + tam)),
                                    width=self.atributos['estilo.grosor'])

        elif self.atributos['estilo.forma'] == 'estilo.tache':
            pygame.draw.line(g.screen, self.atributos['estilo.color_borde'],
                             (pos[0] - tam, pos[1] - tam),
                             (pos[0] + tam, pos[1] + tam),
                             width=self.atributos['estilo.grosor'])
            pygame.draw.line(g.screen, self.atributos['estilo.color_borde'],
                             (pos[0] - tam, pos[1] + tam),
                             (pos[0] + tam, pos[1] - tam),
                             width=self.atributos['estilo.grosor'])

        elif self.atributos['estilo.forma'] == 'estilo.mas':
            pygame.draw.line(g.screen, self.atributos['estilo.color_borde'],
                             (pos[0], pos[1] - tam),
                             (pos[0], pos[1] + tam),
                             width=self.atributos['estilo.grosor'])
            pygame.draw.line(g.screen, self.atributos['estilo.color_borde'],
                             (pos[0] - tam, pos[1]),
                             (pos[0] + tam, pos[1]),
                             width=self.atributos['estilo.grosor'])

        if self.atributos['estilo.mostrarId?']:
            lon = len(str(self.id)) * g.tam_fuente / 4
            try:
                g.fuente.render_to(g.screen, (pos[0] - lon, pos[1] - g.tam_fuente / 3), str(self.id), self.atributos['estilo.color_borde'])
            except:
                print('Except: g.fuente.render_to()')