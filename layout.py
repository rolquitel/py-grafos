import abc
import math
import random
import numpy
from abc import ABC
from nodo import Nodo
from quadtree import QuadTree, Rectangulo, Punto

parar_layout = False


def fr(k, x):
    """
    Fuerza de repulsion
    :param k:
    :param x:
    :return:
    """
    return (k ** 2) / x


def fa(k, x):
    """
    Fuerza de atracción
    :param k:
    :param x:
    :return:
    """
    # return k * math.log10(x / k)
    return (x ** 2) / k


def mag(v2d):
    """
    Magnitud de un vector 2d
    :param v2d:
    :return:
    """
    return math.sqrt((v2d[0] ** 2) + (v2d[1] ** 2))


#####################################################################################################################
class Layout(ABC):
    """
    Clase abstracta para el cálculo de la disposición (layout) de un grafo
    """

    def __init__(self, g):
        __metaclass__ = abc.ABCMeta
        self.grafo = g
        self.atributos = {}

    @abc.abstractmethod
    def paso(self):
        return False

    def ejecutar(self):
        global parar_disposicion
        while not parar_layout:
            if self.paso():
                return


class Random(Layout):
    def paso(self):
        for v in self.grafo.nodos.values():
            v.atrib[Nodo.ATTR_POS] = numpy.array([random.random(), random.random()])

        return True


class Grid(Layout):
    def paso(self):
        dim = numpy.array([1000, 1000])
        lado = int(math.ceil(math.sqrt(len(self.grafo.nodos))))
        tam = dim / (lado + 2)
        origen = dim / 2

        n = 0
        for v in self.grafo.nodos.values():
            x = tam[0] * int((n % lado) + 1) - origen[0]
            y = tam[1] * int((n / lado) + 1) - origen[1]
            v.atrib[Nodo.ATTR_POS] = numpy.array([x, y])
            n = n + 1
        return True


#####################################################################################################################
class FruchtermanReingold(Layout):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de equilibrio de fuerza de Fruchterman y Reigold (1991)
    con la mejora introducida por R. Fletcher (2000) para el enfriamiento del procesamiento
    """

    def __init__(self, g):
        super().__init__(g)
        self.k = 50  # math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos))
        self.t = 0.95
        self.avance = 20
        self.umbral_convergencia = 1e-3
        self.convergio = False
        self.energia = math.inf
        self.progreso = 0

    def paso(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        if self.convergio:
            return

        # para el enfriamiento
        energia_anterior = self.energia
        self.energia = 0

        # fuerza de repulsion
        for v in self.grafo.nodos.values():
            v.atrib[Nodo.ATTR_DESP] = numpy.array([0, 0])
            for u in self.grafo.nodos.values():
                if v != u:
                    delta = v.atrib[Nodo.ATTR_POS] - u.atrib[Nodo.ATTR_POS]
                    v.atrib[Nodo.ATTR_DESP] = v.atrib[Nodo.ATTR_DESP] + (delta / mag(delta)) * fr(self.k, mag(delta))

        # fuerza de atracción
        for e in self.grafo.aristas.values():
            delta = e.n0.atrib[Nodo.ATTR_POS] - e.n1.atrib[Nodo.ATTR_POS]
            e.n0.atrib[Nodo.ATTR_DESP] = e.n0.atrib[Nodo.ATTR_DESP] - (delta / mag(delta)) * fa(self.k, mag(delta))
            e.n1.atrib[Nodo.ATTR_DESP] = e.n1.atrib[Nodo.ATTR_DESP] + (delta / mag(delta)) * fa(self.k, mag(delta))

        # mover los nodos de acuerdo a la fuerza resultante
        dif = numpy.array([0, 0])
        for v in self.grafo.nodos.values():
            dif = dif + (v.atrib[Nodo.ATTR_DESP] / mag(v.atrib[Nodo.ATTR_DESP])) * self.avance
            v.atrib[Nodo.ATTR_POS] = v.atrib[Nodo.ATTR_POS] + (
                    v.atrib[Nodo.ATTR_DESP] / mag(v.atrib[Nodo.ATTR_DESP])) * self.avance
            self.energia = self.energia + mag(v.atrib[Nodo.ATTR_DESP]) ** 2

        self.actualizar_paso(energia_anterior)

        if mag(dif) < self.umbral_convergencia or self.avance < self.umbral_convergencia:
            self.convergio = True

        return self.convergio

    def actualizar_paso(self, energia_anteior):
        """
        Actualizar la magnitud del cambio de posición de los nodos, de acuerdo a como lo menciona R. Fletcher (2000)
        :param energia_anteior: valor de energía anterior
        :return: None
        """
        if self.energia < energia_anteior:
            self.progreso = self.progreso + 1

            if self.progreso >= 5:
                self.progreso = 0
                self.avance = self.t * self.avance

        else:
            self.progreso = 0
            self.avance = self.t * self.avance


#####################################################################################################################
class BarnesHut(Layout):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de equilibrio de fuerza de Fruchterman y Reigold (1991)
    con la mejora introducida por R. Fletcher (2000) para el enfriamiento del procesamiento
    """
    ATTR_CENTRO_MASA = 1
    ATTR_MASA = 0

    def __init__(self, g):
        super().__init__(g)
        self.qtree = None
        self.puntos_por_region = 6
        self.theta = 1
        self.k = 50  # math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos))
        self.t = 0.95
        self.avance = 25
        self.repeticiones_para_bajar = 5
        self.umbral_convergencia = min(3.0, len(g.nodos) / 100)
        self.convergio = False
        self.energia = math.inf
        self.energia_inicial = 0
        self.progreso = 0
        self.pasos = 0

    def construye_quadtree(self):
        self.qtree = QuadTree(Rectangulo(self.grafo.extent[0][0], self.grafo.extent[0][1], self.grafo.extent[1][0],
                                         self.grafo.extent[1][1]), self.puntos_por_region)
        for v in self.grafo.nodos.values():
            p = Punto(v.atrib[Nodo.ATTR_POS][0], v.atrib[Nodo.ATTR_POS][1], v)
            self.qtree.insertar(p)

    def calcular_masas(self, qtree):
        qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] = numpy.array([0, 0])
        qtree.atrib[BarnesHut.ATTR_MASA] = 0

        for p in qtree.puntos:
            qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] = qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] + numpy.array([p.x, p.y])
            qtree.atrib[BarnesHut.ATTR_MASA] = qtree.atrib[BarnesHut.ATTR_MASA] + 1

        if qtree.esta_dividido:
            self.calcular_masas(qtree.I)
            self.calcular_masas(qtree.II)
            self.calcular_masas(qtree.III)
            self.calcular_masas(qtree.IV)

            if qtree.I.atrib[BarnesHut.ATTR_MASA] > 0:
                qtree.atrib[BarnesHut.ATTR_MASA] += qtree.I.atrib[BarnesHut.ATTR_MASA]
                qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] = qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] + \
                                                          qtree.I.atrib[BarnesHut.ATTR_CENTRO_MASA] * \
                                                          qtree.I.atrib[BarnesHut.ATTR_MASA]

            if qtree.II.atrib[BarnesHut.ATTR_MASA] > 0:
                qtree.atrib[BarnesHut.ATTR_MASA] += qtree.II.atrib[BarnesHut.ATTR_MASA]
                qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] = qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] + \
                                                          qtree.II.atrib[BarnesHut.ATTR_CENTRO_MASA] * \
                                                          qtree.II.atrib[BarnesHut.ATTR_MASA]

            if qtree.III.atrib[BarnesHut.ATTR_MASA] > 0:
                qtree.atrib[BarnesHut.ATTR_MASA] += qtree.III.atrib[BarnesHut.ATTR_MASA]
                qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] = qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] + \
                                                          qtree.III.atrib[BarnesHut.ATTR_CENTRO_MASA] * \
                                                          qtree.III.atrib[BarnesHut.ATTR_MASA]

            if qtree.IV.atrib[BarnesHut.ATTR_MASA] > 0:
                qtree.atrib[BarnesHut.ATTR_MASA] += qtree.IV.atrib[BarnesHut.ATTR_MASA]
                qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] = qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] + \
                                                          qtree.IV.atrib[BarnesHut.ATTR_CENTRO_MASA] * \
                                                          qtree.IV.atrib[BarnesHut.ATTR_MASA]

        if qtree.atrib[BarnesHut.ATTR_MASA] > 0:
            qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] = qtree.atrib[BarnesHut.ATTR_CENTRO_MASA] / \
                                                      qtree.atrib[BarnesHut.ATTR_MASA]

    def calcular_fuerza_de_repulsion(self, p, qtree):
        delta = p.atrib[Nodo.ATTR_POS] - qtree.atrib[BarnesHut.ATTR_CENTRO_MASA]

        r = numpy.linalg.norm(delta)
        d = math.sqrt(qtree.limite.w * qtree.limite.h)

        if not r > 0:
            return numpy.array([0, 0])

        if d / r < self.theta or not qtree.esta_dividido:
            return (delta / r) * fr(self.k, r) * qtree.atrib[BarnesHut.ATTR_MASA]
        else:
            fuerza = self.calcular_fuerza_de_repulsion(p, qtree.I)
            fuerza = fuerza + self.calcular_fuerza_de_repulsion(p, qtree.II)
            fuerza = fuerza + self.calcular_fuerza_de_repulsion(p, qtree.III)
            fuerza = fuerza + self.calcular_fuerza_de_repulsion(p, qtree.IV)
            return fuerza

    def paso(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        if self.convergio:
            return

        self.pasos += 1
        self.construye_quadtree()
        self.calcular_masas(self.qtree)

        # para el enfriamiento
        energia_anterior = self.energia
        self.energia = 0

        # fuerza de repulsion
        for v in self.grafo.nodos.values():
            v.atrib[Nodo.ATTR_DESP] = self.calcular_fuerza_de_repulsion(v, self.qtree)

        # fuerza de atracción
        for e in self.grafo.aristas.values():
            delta = e.n0.atrib[Nodo.ATTR_POS] - e.n1.atrib[Nodo.ATTR_POS]
            m = mag(delta)
            if m > 0:
                e.n0.atrib[Nodo.ATTR_DESP] -= (delta / m) * fa(self.k, m)
                e.n1.atrib[Nodo.ATTR_DESP] += (delta / m) * fa(self.k, m)

        # mover los nodos de acuerdo a la fuerza resultante
        for v in self.grafo.nodos.values():
            m = mag(v.atrib[Nodo.ATTR_DESP])
            v.atrib[Nodo.ATTR_POS] = v.atrib[Nodo.ATTR_POS] + (v.atrib[Nodo.ATTR_DESP] / m) * self.avance
            self.energia += m ** 2

        self.actualizar_paso(energia_anterior)

        return self.convergio

    def actualizar_paso(self, energia_anterior):
        """
        Actualizar la magnitud del cambio de posición de los nodos, de acuerdo a como lo menciona R. Fletcher (2000)
        :param energia_anterior: valor de energía anterior
        :return: None
        """
        # print(self.pasos, math.sqrt(self.energia) / (len(self.grafo.nodos) * 10), self.avance)
        if math.sqrt(self.energia) / (len(self.grafo.nodos) * 10) < self.umbral_convergencia or self.avance < 1:
            print('Convergió.')
            self.convergio = True

        # self.avance = min(math.sqrt(self.energia) / (len(self.grafo.nodos) * 10), 2 * self.avance)

        if self.energia < energia_anterior:
            self.progreso = self.progreso + 1

            if self.progreso >= self.repeticiones_para_bajar:
                self.progreso = 0
                self.avance = self.t * self.avance

        else:
            self.progreso = 0
            self.avance = self.t * self.avance


#####################################################################################################################
class Spring(Layout):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de resortes presentado por P. Eades (1984)
    """

    def __init__(self, g):
        super().__init__(g)
        self.c1 = 1
        self.c2 = 25
        self.c3 = 1
        self.c4 = 10
        self.expandir = False
        self.k = 50  # math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos))

    def paso(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        for n in self.grafo.nodos.values():
            n.atrib[Nodo.ATTR_DESP] = numpy.array([0, 0])

        for e in self.grafo.aristas.values():
            f = e.n0.atrib[Nodo.ATTR_POS] - e.n1.atrib[Nodo.ATTR_POS]
            d = numpy.linalg.norm(f)
            try:
                f = (f / d) * math.log10(d / self.c2) * self.c4
            except ValueError:
                continue
            e.n0.atrib[Nodo.ATTR_DESP] = e.n0.atrib[Nodo.ATTR_DESP] - f
            e.n1.atrib[Nodo.ATTR_DESP] = e.n1.atrib[Nodo.ATTR_DESP] + f

        disp = 0
        for n in self.grafo.nodos.values():
            disp = max(disp, numpy.linalg.norm(n.atrib[Nodo.ATTR_DESP]))
            n.atrib[Nodo.ATTR_POS] = n.atrib[Nodo.ATTR_POS] + n.atrib[Nodo.ATTR_DESP]

        # print(disp * len(self.grafo.nodos), self.atrib['k'])
        if (disp * len(self.grafo.nodos)) < self.k and self.expandir:
            self.expandir = False
            for a in self.grafo.nodos.values():
                a.atrib[Nodo.ATTR_DESP] = numpy.array([0, 0])
                for b in self.grafo.nodos.values():
                    if a != b:
                        f = a.atrib[Nodo.ATTR_POS] - b.atrib[Nodo.ATTR_POS]
                        d = numpy.linalg.norm(f)
                        f = (f / d) * fr(self.k, d)
                        a.atrib[Nodo.ATTR_DESP] = a.atrib[Nodo.ATTR_DESP] - self.c4 * f

            for n in self.grafo.nodos.values():
                n.atrib[Nodo.ATTR_POS] = n.atrib[Nodo.ATTR_POS] + n.atrib[Nodo.ATTR_DESP] * (0.1 / self.c4)

        return False
