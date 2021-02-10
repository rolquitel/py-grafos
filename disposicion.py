import abc
import math
import random
import numpy

from abc import ABC


class Disposicion(ABC):
    """
    Clase abstracta para el cálculo de la disposición (layout) de un grafo
    """
    def __init__(self, g, res):
        __metaclass__ = abc.ABCMeta
        self.grafo = g
        self.res = res
        self.atributos = {}

    @abc.abstractmethod
    def paso(self):
        return False


#####################################################################################################################
def fr(k, x):
    """
    Fuerza de repulsion
    :param k:
    :param x:
    :return:
    """
    return (k**2) / x


def fa(k, x):
    """
    Fuerza de atracción
    :param k:
    :param x:
    :return:
    """
    return (x**2) / k


def mag(v2d):
    """
    Magnitud de un vector 2d
    :param v2d:
    :return:
    """
    return math.sqrt((v2d[0] ** 2) + (v2d[1] ** 2))


class FruchtermanReingold(Disposicion):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de equilibrio de fuerza de Fruchterman y Reigold (1991)
    con la mejora introducida por R. Fletcher (2000) para el enfriamiento del procesamiento
    """
    def __init__(self, g, res):
        self.grafo = g
        self.res = numpy.array(res)
        self.atributos = {
            'k'         : math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos)),
            't'         : 0.9,
            'paso'      : 0,
            'convergio?': False,
            'energia'   : math.inf,
            'progreso'  : 0
        }

        self.atributos['paso'] = self.atributos['k']

        # Posicionar los nodos al azar
        origen = self.res / 2
        for v in g.nodos.values():
            v.atributos['pos'] = numpy.array(
                [random.randint(-origen[0], origen[0]), random.randint(-origen[1], origen[1])])

    def paso(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        if self.atributos['convergio?']:
            print('Convergió.')
            return

        # para el enfriamiento
        energia_anterior = self.atributos['energia']
        self.atributos['energia'] = 0

        # fuerza de repulsion
        for v in self.grafo.nodos.values():
            v.atributos['disp'] = numpy.array([0, 0])
            for u in self.grafo.nodos.values():
                if v != u:
                    delta = v.atributos['pos'] - u.atributos['pos']
                    v.atributos['disp'] = v.atributos['disp'] + (delta / mag(delta)) * fr(self.atributos['k'], mag(delta))

        # fuerza de atracción
        for e in self.grafo.aristas.values():
            delta = e.n0.atributos['pos'] - e.n1.atributos['pos']
            e.n0.atributos['disp'] = e.n0.atributos['disp'] - (delta / mag(delta)) * fa(self.atributos['k'], mag(delta))
            e.n1.atributos['disp'] = e.n1.atributos['disp'] + (delta / mag(delta)) * fa(self.atributos['k'], mag(delta))

        # mover los nodos de acuerdo a la fuerza resultante
        dif = numpy.array([0, 0])
        for v in self.grafo.nodos.values():
            dif = dif + (v.atributos['disp'] / mag(v.atributos['disp'])) * self.atributos['paso']
            v.atributos['pos'] = v.atributos['pos'] + (v.atributos['disp'] / mag(v.atributos['disp'])) * self.atributos['paso']
            self.atributos['energia'] = self.atributos['energia'] + mag(v.atributos['disp']) ** 2

        self.actualizar_paso(energia_anterior)

        if mag(dif) < self.atributos['k'] / 10:
            self.atributos['convergio?'] = True

        return self.atributos['convergio?']

    def actualizar_paso(self, energia_anteior):
        """
        Actualizar la magnitud del cambio de posición de los nodos, de acuerdo a como lo menciona R. Fletcher (2000)
        :param energia_anteior: valor de energía anterior
        :return: None
        """
        if self.atributos['energia'] < energia_anteior:
            self.atributos['progreso'] = self.atributos['progreso'] + 1

            if self.atributos['progreso'] >= 5:
                self.atributos['progreso'] = 0
                self.atributos['paso'] = self.atributos['t'] * self.atributos['paso']

        else:
            self.atributos['progreso'] = 0
            self.atributos['paso'] = self.atributos['t'] * self.atributos['paso']


#####################################################################################################################
class Resorte(Disposicion):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de resortes presentado por P. Eades (1984)
    """
    def __init__(self, g, res):
        self.grafo = g
        self.res = numpy.array(res)
        self.atributos = {}

        self.atributos['c1'] = 1
        self.atributos['c2'] = 25
        self.atributos['c3'] = 1
        self.atributos['c4'] = 10
        self.atributos['expandir'] = True

        self.atributos['k'] = math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos))

        origen = self.res / 2

        # Posicionar los nodos al azar
        for v in g.nodos.values():
            v.atributos['pos'] = numpy.array(
                [random.randint(-origen[0], origen[0]), random.randint(-origen[1], origen[1])])

    def paso(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        for n in self.grafo.nodos.values():
            n.atributos['disp'] = numpy.array([0, 0])

        for e in self.grafo.aristas.values():
            f = e.n0.atributos['pos'] - e.n1.atributos['pos']
            d = numpy.linalg.norm(f)
            f = (f / d) * math.log10( d / self.atributos['c2']) * self.atributos['c4']
            # f = (f / d) * (d - self.atributos['c2']) * self.atributos['c4']
            e.n0.atributos['disp'] = e.n0.atributos['disp'] - f
            e.n1.atributos['disp'] = e.n1.atributos['disp'] + f

        disp = 0
        for n in self.grafo.nodos.values():
            disp = max(disp, numpy.linalg.norm(n.atributos['disp']))
            n.atributos['pos'] = n.atributos['pos'] + n.atributos['disp']

        # print(disp * len(self.grafo.nodos), self.atributos['k'])
        if (disp * len(self.grafo.nodos)) < self.atributos['k'] and self.atributos['expandir']:
            self.atributos['expandir'] = False
            print('wow')
            for a in self.grafo.nodos.values():
                a.atributos['disp'] = numpy.array([0, 0])
                for b in self.grafo.nodos.values():
                    if a != b:
                        f = a.atributos['pos'] - b.atributos['pos']
                        d = numpy.linalg.norm(f)
                        f = (f / d) * fr(self.atributos['k'], d)
                        a.atributos['disp'] = a.atributos['disp'] - self.atributos['c4'] * f

            for n in self.grafo.nodos.values():
                n.atributos['pos'] = n.atributos['pos'] + n.atributos['disp'] * (0.1 / self.atributos['c4'])

        return False