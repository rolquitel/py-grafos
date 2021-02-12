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
            v.atributos['disp'] = numpy.array([0, 0])
            for u in self.grafo.nodos.values():
                if v != u:
                    delta = v.atributos['pos'] - u.atributos['pos']
                    v.atributos['disp'] = v.atributos['disp'] + (delta / mag(delta)) * fr(self.k, mag(delta))

        # fuerza de atracción
        for e in self.grafo.aristas.values():
            delta = e.n0.atributos['pos'] - e.n1.atributos['pos']
            e.n0.atributos['disp'] = e.n0.atributos['disp'] - (delta / mag(delta)) * fa(self.k, mag(delta))
            e.n1.atributos['disp'] = e.n1.atributos['disp'] + (delta / mag(delta)) * fa(self.k, mag(delta))

        # mover los nodos de acuerdo a la fuerza resultante
        dif = numpy.array([0, 0])
        for v in self.grafo.nodos.values():
            dif = dif + (v.atributos['disp'] / mag(v.atributos['disp'])) * self.avance
            v.atributos['pos'] = v.atributos['pos'] + (v.atributos['disp'] / mag(v.atributos['disp'])) * self.avance
            self.energia = self.energia + mag(v.atributos['disp']) ** 2

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
        self.avance = 50
        self.repeticiones_para_bajar = 20
        self.umbral_convergencia = len(g.nodos) / 100
        self.convergio = False
        self.energia = math.inf
        self.energia_inicial = 0
        self.progreso = 0
        self.atributos = {}
        self.pasos = 0

        # self.atributos['paso'] = self.atributos['k']

    def construye_quadtree(self):
        self.qtree = QuadTree(Rectangulo(self.grafo.I[0], self.grafo.I[1], self.grafo.F[0], self.grafo.F[1]), self.puntos_por_region)
        for v in self.grafo.nodos.values():
            p = Punto(v.atributos['pos'][0], v.atributos['pos'][1], v)
            self.qtree.insertar(p)

    def calcular_masas(self, qtree):
        qtree.atributos['centro_de_masa'] = numpy.array([0, 0])
        qtree.atributos['masa'] = 0

        for p in qtree.puntos:
            qtree.atributos['centro_de_masa'] = qtree.atributos['centro_de_masa'] + numpy.array([p.x, p.y])
            qtree.atributos['masa'] = qtree.atributos['masa'] + 1

        if qtree.esta_dividido:
            self.calcular_masas(qtree.I)
            self.calcular_masas(qtree.II)
            self.calcular_masas(qtree.III)
            self.calcular_masas(qtree.IV)

            if qtree.I.atributos['masa'] > 0:
                qtree.atributos['masa'] = qtree.atributos['masa'] + qtree.I.atributos['masa']
                qtree.atributos['centro_de_masa'] = qtree.atributos['centro_de_masa'] + qtree.I.atributos['centro_de_masa'] * \
                                                    qtree.I.atributos['masa']

            if qtree.II.atributos['masa'] > 0:
                qtree.atributos['masa'] = qtree.atributos['masa'] + qtree.II.atributos['masa']
                qtree.atributos['centro_de_masa'] = qtree.atributos['centro_de_masa'] + qtree.II.atributos['centro_de_masa'] * \
                                                    qtree.II.atributos['masa']

            if qtree.III.atributos['masa'] > 0:
                qtree.atributos['masa'] = qtree.atributos['masa'] + qtree.III.atributos['masa']
                qtree.atributos['centro_de_masa'] = qtree.atributos['centro_de_masa'] + qtree.III.atributos['centro_de_masa'] * \
                                                    qtree.III.atributos['masa']

            if qtree.IV.atributos['masa'] > 0:
                qtree.atributos['masa'] = qtree.atributos['masa'] + qtree.IV.atributos['masa']
                qtree.atributos['centro_de_masa'] = qtree.atributos['centro_de_masa'] + qtree.IV.atributos['centro_de_masa'] * \
                                                    qtree.IV.atributos['masa']

        if qtree.atributos['masa'] > 0:
            qtree.atributos['centro_de_masa'] = qtree.atributos['centro_de_masa'] / qtree.atributos['masa']

    def calcular_fuerza_de_repulsion(self, p, qtree):
        delta = p.atributos['pos'] - qtree.atributos['centro_de_masa']

        r = numpy.linalg.norm(delta)
        d = math.sqrt(qtree.limite.w * qtree.limite.h)

        if not r > 0:
            return numpy.array([0, 0])

        if d / r < self.theta or not qtree.esta_dividido:
            return (delta / r) * fr(self.k, r) * qtree.atributos['masa']
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
            v.atributos['disp'] = self.calcular_fuerza_de_repulsion(v, self.qtree)

        # fuerza de atracción
        for e in self.grafo.aristas.values():
            delta = e.n0.atributos['pos'] - e.n1.atributos['pos']
            m = mag(delta)
            if m > 0:
                e.n0.atributos['disp'] = e.n0.atributos['disp'] - (delta / m) * fa(self.k, m)
                e.n1.atributos['disp'] = e.n1.atributos['disp'] + (delta / m) * fa(self.k, m)

        # mover los nodos de acuerdo a la fuerza resultante
        for v in self.grafo.nodos.values():
            m = mag(v.atributos['disp'])
            v.atributos['pos'] = v.atributos['pos'] + (v.atributos['disp'] / m) * self.avance
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
        print(self.pasos, math.sqrt(self.energia) / (len(self.grafo.nodos) * 10), self.avance)
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
            n.atributos['disp'] = numpy.array([0, 0])

        for e in self.grafo.aristas.values():
            f = e.n0.atributos['pos'] - e.n1.atributos['pos']
            d = numpy.linalg.norm(f)
            f = (f / d) * math.log10(d / self.c2) * self.c4
            e.n0.atributos['disp'] = e.n0.atributos['disp'] - f
            e.n1.atributos['disp'] = e.n1.atributos['disp'] + f

        disp = 0
        for n in self.grafo.nodos.values():
            disp = max(disp, numpy.linalg.norm(n.atributos['disp']))
            n.atributos['pos'] = n.atributos['pos'] + n.atributos['disp']

        # print(disp * len(self.grafo.nodos), self.atributos['k'])
        if (disp * len(self.grafo.nodos)) < self.k and self.expandir:
            self.expandir = False
            for a in self.grafo.nodos.values():
                a.atributos['disp'] = numpy.array([0, 0])
                for b in self.grafo.nodos.values():
                    if a != b:
                        f = a.atributos['pos'] - b.atributos['pos']
                        d = numpy.linalg.norm(f)
                        f = (f / d) * fr(self.k, d)
                        a.atributos['disp'] = a.atributos['disp'] - self.c4 * f

            for n in self.grafo.nodos.values():
                n.atributos['pos'] = n.atributos['pos'] + n.atributos['disp'] * (0.1 / self.c4)

        self.grafo.calcular_limites()

        return False
