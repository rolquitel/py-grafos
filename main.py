import random
import time

from grafo import Grafo

# Press the green button in the gutter to run the script.
from nodo import Nodo

if __name__ == '__main__':
    random.seed(time.clock())

    # g = Grafo.randomBarabasi(100, 8)
    g = Grafo.randomGeo(60, 0.2)
    # gv = g.toGraphviz()
    # f = open('graph.gv', 'w+')
    # f.write(gv)
    # print('Ok')

    g.atributos['estilo.fondo'] = (250, 250, 250)
    for a in g.aristas.values():
        a.atributos['estilo.color'] = (128, 128, 128)
    for n in g.nodos.values():
        n.atributos['estilo.tamaño'] = 5 + 0.5 * len(n.atributos[Nodo.ATTR_VECINOS])
        n.atributos['estilo.color_relleno'] = (random.randint(50, 250), random.randint(50, 250), random.randint(50, 250))
        n.atributos['estilo.mostrarId?'] = True

    g.display((1200, 1000))



