import random
import time

import algoritmos
import layout
from arista import Arista
from grafo import Grafo

# Press the green button in the gutter to run the script.
from nodo import Nodo

if __name__ == '__main__':
    # random.seed(time.clock())
    g = Grafo()

    g = algoritmos.grafoMalla(15, diagonales=True)
    # g = algoritmos.randomErdos(300, 5000)
    # g = algoritmos.randomBarabasi(1000, 20)
    # g = algoritmos.randomGeo(700, 0.10)
    # g.guardar('grafos/geo.700.10.gv')
    # g.abrir('grafos/geo.300.15.gv')
    # g.abrir('grafos/barabasi.500.8.gv')

    g.estilo(Grafo.ESTILO_FONDO, (250, 250, 250))
    for a in g.aristas.values():
        a.atrib[Arista.ATTR_ESTILO][Arista.ESTILO_COLOR] = (200, 200, 200)
    for n in g.nodos.values():
        n.estilo(Nodo.ESTILO_TAMANO, 5 + 0.1 * len(n.atrib[Nodo.ATTR_VECINOS]))
        n.estilo(Nodo.ESTILO_COL_RELLENO, (random.randint(50, 250), random.randint(50, 250), random.randint(50, 250)))

    g.mostrar((1000, 1000), None)
