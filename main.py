import random
import time

import pygame

import algoritmos
import arista
import layout
import util
from arista import Arista
from grafo import Grafo

# Press the green button in the gutter to run the script.
from nodo import Nodo
from ui import Viewport, Frame, ColorScheme, DarkGrayColorScheme, LightGrayColorScheme, BlueRedColorScheme


class MyView(Viewport):
    def key_manage(self, pressed):
        if pressed[pygame.K_b]:
            if not self.layinout:
                self.layinout = True
                self.layout = layout.BarnesHut(self.grafo)
                self.layout.umbral_convergencia = 1.0
        elif pressed[pygame.K_s]:
            if not self.layinout:
                self.layinout = True
                self.layout = layout.Spring(self.grafo)
        elif pressed[pygame.K_f]:
            if not self.layinout:
                self.layinout = True
                self.layout = layout.FruchtermanReingold(self.grafo)
        elif pressed[pygame.K_ESCAPE]:
            self.layinout = False
        elif pressed[pygame.K_a]:
            for a in self.grafo.aristas.values():
                a.atrib[arista.Arista.ATTR_ESTILO][arista.Arista.ESTILO_ANTIALIAS] = \
                    not a.atrib[arista.Arista.ATTR_ESTILO][arista.Arista.ESTILO_ANTIALIAS]
        elif pressed[pygame.K_r]:
            if not self.layinout:
                layout.Random(self.grafo).ejecutar()
        elif pressed[pygame.K_g]:
            if not self.layinout:
                layout.Grid(self.grafo).ejecutar()


if __name__ == '__main__':
    # g = algoritmos.randomErdos(300, 5000)
    # g = algoritmos.randomBarabasi(1000, 20)
    # g = algoritmos.randomGeo(700, 0.10)
    # g.guardar('grafos/geo.700.10.gv')
    # g = Grafo.abrir('grafos/geo.200.15.gv')
    # g = Grafo.abrir('grafos/barabasi.500.8.gv')

    g1 = algoritmos.grafoMalla( 5,  5, diagonales=False)
    g2 = algoritmos.grafoMalla(10, 10, diagonales=False)
    g3 = algoritmos.grafoMalla(15, 15, diagonales=False)
    g4 = algoritmos.grafoMalla(20, 10, diagonales=False)

    LightGrayColorScheme().apply_to_graph(g1)
    DarkGrayColorScheme().apply_to_graph(g2)
    ColorScheme().apply_to_graph(g3)
    BlueRedColorScheme().apply_to_graph(g4)

    layout.Random(g1).ejecutar()
    layout.Random(g2).ejecutar()
    layout.Random(g3).ejecutar()
    layout.Random(g4).ejecutar()

    vp1 = MyView(g1)
    vp1.set_rect([0, 0], [600, 500])

    vp2 = MyView(g2)
    vp2.set_rect([600, 0], [600, 500])

    vp3 = MyView(g3)
    vp3.set_rect([0, 500], [600, 500])

    vp4 = MyView(g4)
    vp4.set_rect([600, 500], [600, 500])

    win = Frame()

    win.add_viewport(vp1)
    win.add_viewport(vp2)
    win.add_viewport(vp3)
    win.add_viewport(vp4)

    win.add_key_listerer(vp1)
    win.add_key_listerer(vp2)
    win.add_key_listerer(vp3)
    win.add_key_listerer(vp4)

    win.show([1200, 1000])
