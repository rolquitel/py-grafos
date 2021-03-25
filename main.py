import random
import time
import threading
import pygame

import algoritmos
import arista
import layout
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
                a.atrib[arista.ATTR_ESTILO][arista.ESTILO_ANTIALIAS] = \
                    not a.atrib[arista.ATTR_ESTILO][arista.ESTILO_ANTIALIAS]
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
    # g1 = Grafo.abrir('grafos/barabasi.200.8.gv')

    g1 = algoritmos.grafoMalla( 10,  10, diagonales=False)
    # g1 = algoritmos.grafoDorogovtsevMendesV2(150)

    g2 = g1.clonar()
    bfs = Grafo()
    dfs = Grafo()

    # layout.Random(g2).ejecutar()

    # ColorScheme().apply_to_graph(g1)
    # ColorScheme().apply_to_graph(g2)
    # ColorScheme().apply_to_graph(bfs)
    # ColorScheme().apply_to_graph(dfs)

    # algoritmos.BFS(bfs, g1)
    # algoritmos.DFS(dfs, g2)

    bfsThread = threading.Thread(target=algoritmos.BFS, args=(bfs, g1, 500))
    dfsThread = threading.Thread(target=algoritmos.DFS, args=(dfs, g2, 500))

    bfsThread.start()
    dfsThread.start()

    vp1 = MyView(g1)
    vp1.set_rect([0, 0], [600, 500])

    vp2 = MyView(bfs)
    vp2.set_rect([600, 0], [600, 500])

    vp3 = MyView(g2)
    vp3.set_rect([0, 500], [600, 500])

    vp4 = MyView(dfs)
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

    print('Wait until all threads have finished.')