import random
import time

import algoritmos
import layout
from grafo import Grafo

# Press the green button in the gutter to run the script.
from nodo import Nodo

if __name__ == '__main__':
    random.seed(time.clock())
    g = Grafo()

    # g = algoritmos.randomBarabasi(50, 6)
    # g = algoritmos.randomGeo(100, 0.25)
    # g.guardar('grafos/geo.100.25.gv')
    #g.abrir('grafos/geo.100.25.gv')
    g.abrir('grafos/barabasi.50.6.gv')

    g.atributos['estilo.fondo'] = (250, 250, 250)
    for a in g.aristas.values():
        a.atributos['estilo.color'] = (200, 200, 200)
    for n in g.nodos.values():
        n.atributos['estilo.tamaño'] = 5 + 0.1 * len(n.atributos[Nodo.ATTR_VECINOS])
        n.atributos['estilo.color_relleno'] = (random.randint(50, 250), random.randint(50, 250), random.randint(50, 250))
        n.atributos['estilo.mostrarId?'] = False
        n.atributos['estilo.escalar?'] = False

    spring = layout.Spring(g, (1000, 1000))
    force = layout.FruchtermanReingold(g, (1000, 1000))
    g.mostrar((1000, 1000), None)



