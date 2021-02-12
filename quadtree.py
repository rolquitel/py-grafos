import math

import pygame


class Punto:
    def __init__(self, x, y, datos):
        self.x = x
        self.y = y
        self.datos = datos


class Rectangulo:
    def __init__(self, xi, yi, xf, yf):
        self.xi = min(xi, xf)
        self.yi = min(yi, yf)
        self.xf = max(xi, xf)
        self.yf = max(yi, yf)
        self.w = xf - xi
        self.h = yf - yi

    def contiene(self, point):
        return self.xi <= point.x <= self.xf and self.yi <= point.y <= self.yf

    def intersecta(self, otro):
        return not (otro.xi > self.xf or otro.xf < self.xi or otro.yi > self.yf or otro.yf < self.yi)


class Circulo:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.r2 = r * r

    def contiene(self, punto):
        d = (punto.x - self.x) ** 2 + (punto.y - self.y) ** 2
        return d <= self.r2

    def intersecta(self, rect):
        xDist = abs((rect.xi + rect.xf) / 2 - self.x);
        yDist = abs((rect.yi + rect.yf) / 2 - self.y);

        r = self.r
        w = rect.xf - rect.xi;
        h = rect.yf - rect.yf;

        edges = (xDist - w) ** 2 + (yDist - h) ** 2

        if xDist > (r + w) or yDist > (r + h):
            return False

        if xDist <= w or yDist <= h:
            return True

        return edges <= self.r2


class QuadTree:
    def __init__(self, limite=Rectangulo(0, 0, 1, 1), capacidad=8):
        if capacidad < 1:
            capacidad = 1

        self.limite = limite
        self.capacidad = capacidad
        self.puntos = []
        self.esta_dividido = False
        self.atributos = {}

    def subdividir(self):
        xi = self.limite.xi
        yi = self.limite.yi
        xf = self.limite.xf
        yf = self.limite.yf
        xc = (xi + xf) / 2
        yc = (yi + yf) / 2

        I = Rectangulo(xc, yc, xf, yf)
        II = Rectangulo(xi, yc, xc, yf)
        III = Rectangulo(xi, yi, xc, yc)
        IV = Rectangulo(xc, yi, xf, yc)

        self.I = QuadTree(I, self.capacidad)
        self.II = QuadTree(II, self.capacidad)
        self.III = QuadTree(III, self.capacidad)
        self.IV = QuadTree(IV, self.capacidad)

        self.esta_dividido = True

    def insertar(self, punto):
        if not self.limite.contiene(punto):
            return False

        if len(self.puntos) < self.capacidad:
            self.puntos.append(punto)
            return True

        if not self.esta_dividido:
            self.subdividir()

        return self.I.insertar(punto) or self.II.insertar(punto) or self.III.insertar(punto) or self.IV.insertar(punto)

    def buscar(self, rango, encontrados=[]):
        if not rango.intersecta(self.limite):
            return encontrados

        for p in self.puntos:
            if rango.contiene(p):
                encontrados.append(p)

        if self.esta_dividido:
            self.I.buscar(rango, encontrados)
            self.II.buscar(rango, encontrados)
            self.III.buscar(rango, encontrados)
            self.IV.buscar(rango, encontrados)

        return encontrados

    def dibujar(self, sup, color, transf):
        xi = self.limite.xi
        yi = self.limite.yi
        xf = self.limite.xf
        yf = self.limite.yf
        I = transf.transformar([xi, yi])
        F = transf.transformar([xf, yf])
        pygame.draw.rect(sup, color, (I[0], I[1], F[0] - I[0], F[1] - I[1]), width=1)
        # dibujar_rect_punteado(sup, color, I, F)

        if self.esta_dividido:
            self.I.dibujar(sup, color, transf)
            self.II.dibujar(sup, color, transf)
            self.III.dibujar(sup, color, transf)
            self.IV.dibujar(sup, color, transf)

        # for p in self.puntos:
        #     P = transf.transformar([p.x, p.y])
        #     pygame.draw.line(sup, color, (P[0] - 5, P[1] - 5), (P[0] + 5, P[1] + 5))
        #     pygame.draw.line(sup, color, (P[0] - 5, P[1] + 5), (P[0] + 5, P[1] - 5))
