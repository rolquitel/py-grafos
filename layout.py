import abc
import math
import random
import numpy
from abc import ABC

import node
import graph
from quadtree import QuadTree, Rectangle, Point

stop_layinout = False


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
        self.graph = g
        self.attr = {}

    @abc.abstractmethod
    def step(self):
        return False

    def run(self):
        global stop_layinout
        while not stop_layinout:
            if self.step():
                return


class Random(Layout):
    def step(self):
        for v in self.graph.nodes.values():
            v.attr[node.ATTR_POS] = numpy.array(
                [random.random(), random.random()])

        return True


class Grid(Layout):
    def step(self):
        dim = numpy.array([1000, 1000])
        lado = int(math.ceil(math.sqrt(len(self.graph.nodes))))
        tam = dim / (lado + 2)
        origen = dim / 2

        n = 0
        for v in self.graph.nodes.values():
            x = tam[0] * int((n % lado) + 1) - origen[0]
            y = tam[1] * int((n / lado) + 1) - origen[1]
            v.attr[node.ATTR_POS] = numpy.array([x, y])
            n = n + 1
        return True


#####################################################################################################################
class FruchtermanReingold(Layout):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de equilibrio de fuerza de Fruchterman y Reigold (1991)
    con la mejora introducida por R. Fletcher (2000) para el enfriamiento del procesamiento
    """

    def __init__(self, g, k=50, t=0.95, advance=20, conv_threshold=3.0):
        super().__init__(g)
        # math.sqrt((self.res[0] * self.res[1]) / len(self.grafo.nodes))
        self.k = k
        self.t = t
        self.advance = advance
        self.conv_threshold = min(conv_threshold, len(g.nodes) / 100)
        self.converged = False
        self.energy = math.inf
        self.progress = 0

    def step(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        if self.converged:
            return

        # para el enfriamiento
        prev_energy = self.energy
        self.energy = 0

        with graph.WRITING_LOCK:
            # fuerza de repulsion
            for v in self.graph.nodes.values():
                v.attr[node.ATTR_DISP] = numpy.array([0, 0])
                for u in self.graph.nodes.values():
                    if v != u:
                        delta = v.attr[node.ATTR_POS] - u.attr[node.ATTR_POS]
                        m_delta = mag(delta)
                        if m_delta > 0:
                            v.attr[node.ATTR_DISP] = v.attr[node.ATTR_DISP] + \
                                (delta / m_delta) * fr(self.k, m_delta)

            # fuerza de atracción
            for e in self.graph.edges.values():
                delta = e.n0.attr[node.ATTR_POS] - e.n1.attr[node.ATTR_POS]
                e.n0.attr[node.ATTR_DISP] = e.n0.attr[node.ATTR_DISP] - \
                    (delta / mag(delta)) * fa(self.k, mag(delta))
                e.n1.attr[node.ATTR_DISP] = e.n1.attr[node.ATTR_DISP] + \
                    (delta / mag(delta)) * fa(self.k, mag(delta))

            # mover los nodes de acuerdo a la fuerza resultante
            dif = numpy.array([0, 0])
            for v in self.graph.nodes.values():
                dif = dif + (v.attr[node.ATTR_DISP] /
                             mag(v.attr[node.ATTR_DISP])) * self.advance
                v.attr[node.ATTR_POS] = v.attr[node.ATTR_POS] + (
                    v.attr[node.ATTR_DISP] / mag(v.attr[node.ATTR_DISP])) * self.advance
                self.energy = self.energy + mag(v.attr[node.ATTR_DISP]) ** 2

        self.update_step(prev_energy)

        if mag(dif) < self.conv_threshold or self.advance < self.conv_threshold:
            self.converged = True

        return self.converged

    def update_step(self, prev_energy):
        """
        Actualizar la magnitud del cambio de posición de los nodos, de acuerdo a como lo menciona R. Fletcher (2000)
        :param energia_anteior: valor de energía anterior
        :return: None
        """
        if self.energy < prev_energy:
            self.progress = self.progress + 1

            if self.progress >= 5:
                self.progress = 0
                self.advance = self.t * self.advance

        else:
            self.progress = 0
            self.advance = self.t * self.advance


#####################################################################################################################
ATTR_CENTER_OF_MASS = 1
ATTR_MASS = 0


class BarnesHut(Layout):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de equilibrio de fuerza de Fruchterman y Reigold (1991)
    con la mejora introducida por R. Fletcher (2000) para el enfriamiento del procesamiento
    """

    def __init__(self, g, k=50, t=0.95, advance=20, conv_threshold=3.0, points_by_region=4):
        super().__init__(g)
        self.qtree = None
        self.points_by_region = points_by_region
        self.theta = 1
        self.k = k
        self.t = t
        self.advance = advance
        self.reps_for_down = 5
        self.conv_threshold = min(conv_threshold, len(g.nodes) / 100)
        self.converged = False
        self.energy = math.inf
        self.initial_energy = 0
        self.progress = 0
        self.steps = 0

    def build_quadtree(self):
        self.qtree = QuadTree(Rectangle(self.graph.extent[0][0], self.graph.extent[0][1], self.graph.extent[1][0],
                                        self.graph.extent[1][1]), self.points_by_region)
        for v in self.graph.nodes.values():
            p = Point(v.attr[node.ATTR_POS][0], v.attr[node.ATTR_POS][1], v)
            self.qtree.insert(p)

    def compute_mass(self, qtree):
        qtree.attr[ATTR_CENTER_OF_MASS] = numpy.array([0, 0])
        qtree.attr[ATTR_MASS] = 0

        for p in qtree.points:
            qtree.attr[ATTR_CENTER_OF_MASS] = qtree.attr[ATTR_CENTER_OF_MASS] + \
                numpy.array([p.x, p.y])
            qtree.attr[ATTR_MASS] = qtree.attr[ATTR_MASS] + 1

        if qtree.is_divided:
            self.compute_mass(qtree.I)
            self.compute_mass(qtree.II)
            self.compute_mass(qtree.III)
            self.compute_mass(qtree.IV)

            if qtree.I.attr[ATTR_MASS] > 0:
                qtree.attr[ATTR_MASS] += qtree.I.attr[ATTR_MASS]
                qtree.attr[ATTR_CENTER_OF_MASS] = qtree.attr[ATTR_CENTER_OF_MASS] + \
                    qtree.I.attr[ATTR_CENTER_OF_MASS] * \
                    qtree.I.attr[ATTR_MASS]

            if qtree.II.attr[ATTR_MASS] > 0:
                qtree.attr[ATTR_MASS] += qtree.II.attr[ATTR_MASS]
                qtree.attr[ATTR_CENTER_OF_MASS] = qtree.attr[ATTR_CENTER_OF_MASS] + \
                    qtree.II.attr[ATTR_CENTER_OF_MASS] * \
                    qtree.II.attr[ATTR_MASS]

            if qtree.III.attr[ATTR_MASS] > 0:
                qtree.attr[ATTR_MASS] += qtree.III.attr[ATTR_MASS]
                qtree.attr[ATTR_CENTER_OF_MASS] = qtree.attr[ATTR_CENTER_OF_MASS] + \
                    qtree.III.attr[ATTR_CENTER_OF_MASS] * \
                    qtree.III.attr[ATTR_MASS]

            if qtree.IV.attr[ATTR_MASS] > 0:
                qtree.attr[ATTR_MASS] += qtree.IV.attr[ATTR_MASS]
                qtree.attr[ATTR_CENTER_OF_MASS] = qtree.attr[ATTR_CENTER_OF_MASS] + \
                    qtree.IV.attr[ATTR_CENTER_OF_MASS] * \
                    qtree.IV.attr[ATTR_MASS]

        if qtree.attr[ATTR_MASS] > 0:
            qtree.attr[ATTR_CENTER_OF_MASS] = qtree.attr[ATTR_CENTER_OF_MASS] / \
                qtree.attr[ATTR_MASS]

    def compute_repulsion_force(self, p, qtree):
        force = numpy.array([0.0, 0.0])

        vec = p.data.attr[node.ATTR_POS] - qtree.attr[ATTR_CENTER_OF_MASS]
        r = numpy.linalg.norm(vec)
        # d = math.sqrt(qtree.limite.w * qtree.limite.h)
        d = min(qtree.limits.w, qtree.limits.h)

        if not r > 0:
            return numpy.array([0.0, 0.0])

        if d / r < self.theta or not qtree.is_divided:
            force = force + (vec / r) * fr(self.k, r) * qtree.attr[ATTR_MASS]
            return force
        else:
            force = force + self.compute_repulsion_force(p, qtree.I)
            force = force + self.compute_repulsion_force(p, qtree.II)
            force = force + self.compute_repulsion_force(p, qtree.III)
            force = force + self.compute_repulsion_force(p, qtree.IV)
            return force

    def step(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        # if self.convergio:
        #     return

        self.steps += 1
        self.build_quadtree()
        self.compute_mass(self.qtree)

        # para el enfriamiento
        prev_energy = self.energy
        self.energy = 0

        with graph.WRITING_LOCK:
            # fuerza de repulsion
            for v in self.graph.nodes.values():
                p = Point(v.attr[node.ATTR_POS][0],
                          v.attr[node.ATTR_POS][1], v)
                v.attr[node.ATTR_DISP] = self.compute_repulsion_force(
                    p, self.qtree)

            # fuerza de atracción
            for e in self.graph.edges.values():
                delta = e.n0.attr[node.ATTR_POS] - e.n1.attr[node.ATTR_POS]
                m = mag(delta)
                if m > 0:
                    e.n0.attr[node.ATTR_DISP] -= (delta / m) * fa(self.k, m)
                    e.n1.attr[node.ATTR_DISP] += (delta / m) * fa(self.k, m)

            # mover los nodes de acuerdo a la fuerza resultante
            for v in self.graph.nodes.values():
                m = mag(v.attr[node.ATTR_DISP])
                v.attr[node.ATTR_POS] = v.attr[node.ATTR_POS] + \
                    (v.attr[node.ATTR_DISP] / m) * self.advance
                self.energy += m ** 2

        if not self.converged:
            self.update_step(prev_energy)

        return self.converged

    def update_step(self, energia_anterior):
        """
        Actualizar la magnitud del cambio de posición de los nodes, de acuerdo a como lo menciona R. Fletcher (2000)
        :param energia_anterior: valor de energía anterior
        :return: None
        """
        # print(self.pasos, math.sqrt(self.energia) / (len(self.grafo.nodes) * 10), self.avance)
        if math.sqrt(self.energy) / (len(self.graph.nodes) * 10) < self.conv_threshold or self.advance < 1:
            print('Layout converged.')
            self.converged = True

        # self.avance = min(math.sqrt(self.energia) / (len(self.grafo.nodes) * 10), 2 * self.avance)

        if self.energy < energia_anterior:
            self.progress = self.progress + 1

            if self.progress >= self.reps_for_down:
                self.progress = 0
                self.advance = self.t * self.advance

        else:
            self.progress = 0
            self.advance = self.t * self.advance


#####################################################################################################################
class Spring(Layout):
    """
    Clase que calcula la disposición de un grafo mediante el algoritmo de resortes presentado por P. Eades (1984)
    """

    def __init__(self, g):
        super().__init__(g)
        self.c1 = 1
        self.c2 = 50
        self.c3 = 1
        self.c4 = 10
        self.expand = False
        # math.sqrt((self.res[0] * self.res[1]) / len(self.graph.nodes))
        self.k = 50

    def step(self):
        """
        Ejecuta un paso del algoritmo de disposición
        :return: True si el algoritmo ha convergido, False de otra forma
        """
        with graph.WRITING_LOCK:
            for n in self.graph.nodes.values():
                n.attr[node.ATTR_DISP] = numpy.array([0, 0])

            for e in self.graph.edges.values():
                f = e.n0.attr[node.ATTR_POS] - e.n1.attr[node.ATTR_POS]
                d = numpy.linalg.norm(f)
                try:
                    f = (f / d) * math.log10(d / self.c2) * self.c4
                except ValueError:
                    continue
                e.n0.attr[node.ATTR_DISP] = e.n0.attr[node.ATTR_DISP] - f
                e.n1.attr[node.ATTR_DISP] = e.n1.attr[node.ATTR_DISP] + f

            disp = 0
            for n in self.graph.nodes.values():
                disp = max(disp, numpy.linalg.norm(n.attr[node.ATTR_DISP]))
                n.attr[node.ATTR_POS] = n.attr[node.ATTR_POS] + \
                    n.attr[node.ATTR_DISP]

            # print(disp * len(self.grafo.nodes), self.atrib['k'])
            if (disp * len(self.graph.nodes)) < self.k and self.expand:
                self.expand = False
                for a in self.graph.nodes.values():
                    a.attr[node.ATTR_DISP] = numpy.array([0, 0])
                    for b in self.graph.nodes.values():
                        if a != b:
                            f = a.attr[node.ATTR_POS] - b.attr[node.ATTR_POS]
                            d = numpy.linalg.norm(f)
                            f = (f / d) * fr(self.k, d)
                            a.attr[node.ATTR_DISP] = a.attr[node.ATTR_DISP] - \
                                self.c4 * f

                for n in self.graph.nodes.values():
                    n.attr[node.ATTR_POS] = n.attr[node.ATTR_POS] + \
                        n.attr[node.ATTR_DISP] * (0.1 / self.c4)

        return False
