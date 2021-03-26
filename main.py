import math
import sys
import threading
from time import sleep
import pygame

import algoritmos
import ui
import layout
from graph import Graph

from node import Node
from ui import Viewport, Frame, ColorScheme, DarkGrayColorScheme, LightGrayColorScheme, BlueRedColorScheme


class MyView(Viewport):
    def key_manage(self, pressed):
        if pressed[pygame.K_b]:
            if not self.layinout:
                self.layinout = True
                self.layout = layout.BarnesHut(self.graph)
                self.layout.conv_threshold = 1.0
        elif pressed[pygame.K_s]:
            if not self.layinout:
                self.layinout = True
                self.layout = layout.Spring(self.graph)
        elif pressed[pygame.K_f]:
            if not self.layinout:
                self.layinout = True
                self.layout = layout.FruchtermanReingold(self.graph)
        elif pressed[pygame.K_ESCAPE]:
            self.layinout = False
        elif pressed[pygame.K_a]:
            for a in self.graph.edges.values():
                a.atrib[ui.ATTR_STYLE][ui.STYLE_ANTIALIAS] = \
                    not a.atrib[ui.ATTR_STYLE][ui.STYLE_ANTIALIAS]
        elif pressed[pygame.K_r]:
            if not self.layinout:
                layout.Random(self.graph).run()
        elif pressed[pygame.K_g]:
            if not self.layinout:
                layout.Grid(self.graph).run()
        elif pressed[pygame.K_d]:
            algoritmos.event_DorogovtsevMendes(self.graph)


if __name__ == '__main__':
    # g = algoritmos.randomErdos(300, 5000)
    # g = algoritmos.randomBarabasi(250, 20)
    # g = algoritmos.randomGeo(300, 0.10)
    # g.guardar('grafos/geo.700.10.gv')
    # g1 = Grafo.abrir('grafos/geo.200.15.gv')
    # g1 = Grafo.abrir('grafos/barabasi.200.8.gv')

    # g1 = algoritmos.gridGraph(10,  10, diagonals=False)
    g1 = algoritmos.DorogovtsevMendesGraph(150)

    g2 = g1.clone()
    bfs = Graph()
    dfs = Graph()

    # layout.Random(g2).ejecutar()

    # ColorScheme().apply_to_graph(g1)
    # ColorScheme().apply_to_graph(g2)
    # ColorScheme().apply_to_graph(bfs)
    # ColorScheme().apply_to_graph(dfs)

    # algoritmos.BFS(bfs, g1)
    # algoritmos.DFS(dfs, g2)

    tiempo = 50000 / len(g1.nodes)

    bfsThread = threading.Thread(target=algoritmos.BFS, args=(bfs, g1, tiempo))
    dfsThread = threading.Thread(target=algoritmos.DFS, args=(dfs, g2, tiempo))

    vp1 = MyView(g1, layout=layout.BarnesHut(g1))
    vp1.set_rect([0, 0], [600, 500])

    vp2 = MyView(bfs, layout=layout.FruchtermanReingold(bfs, t=0.9999, advance=math.sqrt(len(g1.nodes)) / 2))
    vp2.set_rect([600, 0], [600, 500])

    vp3 = MyView(g2, layout=layout.BarnesHut(g2))
    vp3.set_rect([0, 500], [600, 500])

    vp4 = MyView(dfs, layout=layout.FruchtermanReingold(dfs, t=0.9999, advance=math.sqrt(len(g1.nodes)) / 2))
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

    bfsThread.start()
    dfsThread.start()

    win.show([1200, 1000])

    print('Wait until all threads have finished.')
