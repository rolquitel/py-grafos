import abc
import math
import numpy
from abc import ABC

from quadtree import QuadTree, Rectangulo, Punto

parar_layout = False


class Layout(ABC):
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

    def ejecutar(self):
        global parar_disposicion
        while not parar_layout:
            if self.paso():
                return


#####################################################################################################################
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
class FruchtermanReingold(Layout):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de equilibrio de fuerza de Fruchterman y Reigold (1991)
    con la mejora introducida por R. Fletcher (2000) para el enfriamiento del procesamiento
    """

    def __init__(self, g, res):
        self.grafo = g
        self.res = numpy.array(res)
        self.k = math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos))
        self.t = 0.95
        self.avance = 20
        self.umbral_convergencia = 1e-3
        self.convergio = False
        self.energia = math.inf
        self.progreso = 0
        self.atributos = {}

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
            v.atrib['disp'] = numpy.array([0, 0])
            for u in self.grafo.nodos.values():
                if v != u:
                    delta = v.atrib['pos'] - u.atrib['pos']
                    v.atrib['disp'] = v.atrib['disp'] + (delta / mag(delta)) * fr(self.k, mag(delta))

        # fuerza de atracción
        for e in self.grafo.aristas.values():
            delta = e.n0.atrib['pos'] - e.n1.atrib['pos']
            e.n0.atrib['disp'] = e.n0.atrib['disp'] - (delta / mag(delta)) * fa(self.k, mag(delta))
            e.n1.atrib['disp'] = e.n1.atrib['disp'] + (delta / mag(delta)) * fa(self.k, mag(delta))

        # mover los nodos de acuerdo a la fuerza resultante
        dif = numpy.array([0, 0])
        for v in self.grafo.nodos.values():
            dif = dif + (v.atrib['disp'] / mag(v.atrib['disp'])) * self.avance
            v.atrib['pos'] = v.atrib['pos'] + (v.atrib['disp'] / mag(v.atrib['disp'])) * self.avance
            self.energia = self.energia + mag(v.atrib['disp']) ** 2

        self.actualizar_paso(energia_anterior)

        if mag(dif) < self.umbral_convergencia or self.avance < self.umbral_convergencia:
            self.convergio = True

        self.grafo.calcular_limites()

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

    def __init__(self, g, res):
        self.grafo = g
        self.res = numpy.array(res)
        self.qtree = None
        self.puntos_por_region = 6
        self.theta = 1
        self.k = math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos))
        self.t = 0.95
        self.avance = 25
        self.repeticiones_para_bajar = 5
        self.umbral_convergencia = min(3.0, len(g.nodos) / 100)
        self.convergio = False
        self.energia = math.inf
        self.energia_inicial = 0
        self.progreso = 0
        self.atributos = {}
        self.pasos = 0

        # self.atrib['paso'] = self.atrib['k']

    def construye_quadtree(self):
        self.qtree = QuadTree(Rectangulo(self.grafo.extent[0][0], self.grafo.extent[0][1], self.grafo.extent[1][0], self.grafo.extent[1][1]), self.puntos_por_region)
        for v in self.grafo.nodos.values():
            p = Punto(v.atrib['pos'][0], v.atrib['pos'][1], v)
            self.qtree.insertar(p)

    def calcular_masas(self, qtree):
        qtree.atrib['centro_de_masa'] = numpy.array([0, 0])
        qtree.atrib['masa'] = 0

        for p in qtree.puntos:
            qtree.atrib['centro_de_masa'] = qtree.atrib['centro_de_masa'] + numpy.array([p.x, p.y])
            qtree.atrib['masa'] = qtree.atrib['masa'] + 1

        if qtree.esta_dividido:
            self.calcular_masas(qtree.I)
            self.calcular_masas(qtree.II)
            self.calcular_masas(qtree.III)
            self.calcular_masas(qtree.IV)

            if qtree.I.atrib['masa'] > 0:
                qtree.atrib['masa'] = qtree.atrib['masa'] + qtree.I.atrib['masa']
                qtree.atrib['centro_de_masa'] = qtree.atrib['centro_de_masa'] + qtree.I.atrib['centro_de_masa'] * \
                                                qtree.I.atrib['masa']

            if qtree.II.atrib['masa'] > 0:
                qtree.atrib['masa'] = qtree.atrib['masa'] + qtree.II.atrib['masa']
                qtree.atrib['centro_de_masa'] = qtree.atrib['centro_de_masa'] + qtree.II.atrib['centro_de_masa'] * \
                                                qtree.II.atrib['masa']

            if qtree.III.atrib['masa'] > 0:
                qtree.atrib['masa'] = qtree.atrib['masa'] + qtree.III.atrib['masa']
                qtree.atrib['centro_de_masa'] = qtree.atrib['centro_de_masa'] + qtree.III.atrib['centro_de_masa'] * \
                                                qtree.III.atrib['masa']

            if qtree.IV.atrib['masa'] > 0:
                qtree.atrib['masa'] = qtree.atrib['masa'] + qtree.IV.atrib['masa']
                qtree.atrib['centro_de_masa'] = qtree.atrib['centro_de_masa'] + qtree.IV.atrib['centro_de_masa'] * \
                                                qtree.IV.atrib['masa']

        if qtree.atrib['masa'] > 0:
            qtree.atrib['centro_de_masa'] = qtree.atrib['centro_de_masa'] / qtree.atrib['masa']

    def calcular_fuerza_de_repulsion(self, p, qtree):
        delta = p.atrib['pos'] - qtree.atrib['centro_de_masa']

        r = numpy.linalg.norm(delta)
        d = math.sqrt(qtree.limite.w * qtree.limite.h)

        if not r > 0:
            return numpy.array([0, 0])

        if d / r < self.theta or not qtree.esta_dividido:
            return (delta / r) * fr(self.k, r) * qtree.atrib['masa']
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
            v.atrib['disp'] = self.calcular_fuerza_de_repulsion(v, self.qtree)

        # fuerza de atracción
        for e in self.grafo.aristas.values():
            delta = e.n0.atrib['pos'] - e.n1.atrib['pos']
            m = mag(delta)
            if m > 0:
                e.n0.atrib['disp'] -= (delta / m) * fa(self.k, m)
                e.n1.atrib['disp'] += (delta / m) * fa(self.k, m)

        # mover los nodos de acuerdo a la fuerza resultante
        for v in self.grafo.nodos.values():
            m = mag(v.atrib['disp'])
            v.atrib['pos'] = v.atrib['pos'] + (v.atrib['disp'] / m) * self.avance
            self.energia += m ** 2

        self.actualizar_paso(energia_anterior)
        self.grafo.calcular_limites()

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

    def __init__(self, g, res):
        self.grafo = g
        self.res = numpy.array(res)
        self.atributos = {}
        self.c1 = 1
        self.c2 = 25
        self.c3 = 1
        self.c4 = 10
        self.expandir = False
        self. k = math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodos))

    def paso(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        for n in self.grafo.nodos.values():
            n.atrib['disp'] = numpy.array([0, 0])

        for e in self.grafo.aristas.values():
            f = e.n0.atrib['pos'] - e.n1.atrib['pos']
            d = numpy.linalg.norm(f)
            f = (f / d) * math.log10(d / self.c2) * self.c4
            e.n0.atrib['disp'] = e.n0.atrib['disp'] - f
            e.n1.atrib['disp'] = e.n1.atrib['disp'] + f

        disp = 0
        for n in self.grafo.nodos.values():
            disp = max(disp, numpy.linalg.norm(n.atrib['disp']))
            n.atrib['pos'] = n.atrib['pos'] + n.atrib['disp']

        # print(disp * len(self.grafo.nodos), self.atrib['k'])
        if (disp * len(self.grafo.nodos)) < self.k and self.expandir:
            self.expandir = False
            for a in self.grafo.nodos.values():
                a.atrib['disp'] = numpy.array([0, 0])
                for b in self.grafo.nodos.values():
                    if a != b:
                        f = a.atrib['pos'] - b.atrib['pos']
                        d = numpy.linalg.norm(f)
                        f = (f / d) * fr(self.k, d)
                        a.atrib['disp'] = a.atrib['disp'] - self.c4 * f

            for n in self.grafo.nodos.values():
                n.atrib['pos'] = n.atrib['pos'] + n.atrib['disp'] * (0.1 / self.c4)

        self.grafo.calcular_limites()

        return False
