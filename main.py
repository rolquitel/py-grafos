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
        elif pressed[pygame.K_d]:
            algoritmos.eventoDorogovtsevMendes(self.grafo)


if __name__ == '__main__':
    # g = algoritmos.randomErdos(300, 5000)
    # g = algoritmos.randomBarabasi(250, 20)
    # g = algoritmos.randomGeo(300, 0.10)
    # g.guardar('grafos/geo.700.10.gv')
    # g1 = Grafo.abrir('grafos/geo.200.15.gv')
    g = Grafo.abrir('grafos/barabasi.500.8.gv')

    # g1 = algoritmos.grafoMalla( 5,  5, diagonales=False)
    # g = algoritmos.grafoDorogovtsevMendesV2(150)

    bfs = Grafo()

    algoritmos.BFS(bfs, g)
    ColorScheme().apply_to_graph(bfs)

    vp1 = MyView(g)
    vp1.set_rect([0, 0], [600, 1000])

    vp2 = MyView(bfs)
    vp2.set_rect([600, 0], [600, 1000])

    win = Frame()

    win.add_viewport(vp1)
    win.add_viewport(vp2)

    win.add_key_listerer(vp1)
    win.add_key_listerer(vp2)

    win.show([1200, 1000])
