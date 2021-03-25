import math

import pygame


class Point:
    def __init__(self, x, y, datos):
        self.x = x
        self.y = y
        self.data = datos


class Rectangle:
    def __init__(self, xi, yi, xf, yf):
        self.xi = min(xi, xf)
        self.yi = min(yi, yf)
        self.xf = max(xi, xf)
        self.yf = max(yi, yf)
        self.w = xf - xi
        self.h = yf - yi

    def contains(self, point):
        return self.xi <= point.x <= self.xf and self.yi <= point.y <= self.yf

    def intersects(self, otro):
        return not (otro.xi > self.xf or otro.xf < self.xi or otro.yi > self.yf or otro.yf < self.yi)


class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.r2 = r * r

    def contains(self, punto):
        d = (punto.x - self.x) ** 2 + (punto.y - self.y) ** 2
        return d <= self.r2

    def intersects(self, rect):
        xDist = abs((rect.xi + rect.xf) / 2 - self.x)
        yDist = abs((rect.yi + rect.yf) / 2 - self.y)

        r = self.r
        w = rect.xf - rect.xi
        h = rect.yf - rect.yf

        edges = (xDist - w) ** 2 + (yDist - h) ** 2

        if xDist > (r + w) or yDist > (r + h):
            return False

        if xDist <= w or yDist <= h:
            return True

        return edges <= self.r2


class QuadTree:
    def __init__(self, limits=Rectangle(0, 0, 1, 1), capacity=8):
        if capacity < 1:
            capacity = 1

        self.limits = limits
        self.capacity = capacity
        self.points = []
        self.is_divided = False
        self.attr = {}

    def subdivide(self):
        xi = self.limits.xi
        yi = self.limits.yi
        xf = self.limits.xf
        yf = self.limits.yf
        xc = (xi + xf) / 2
        yc = (yi + yf) / 2

        I = Rectangle(xc, yc, xf, yf)
        II = Rectangle(xi, yc, xc, yf)
        III = Rectangle(xi, yi, xc, yc)
        IV = Rectangle(xc, yi, xf, yc)

        self.I = QuadTree(I, self.capacity)
        self.II = QuadTree(II, self.capacity)
        self.III = QuadTree(III, self.capacity)
        self.IV = QuadTree(IV, self.capacity)

        self.is_divided = True

    def insert(self, point):
        if not self.limits.contains(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True

        if not self.is_divided:
            self.subdivide()

        return self.I.insert(point) or self.II.insert(point) or self.III.insert(point) or self.IV.insert(point)

    def query(self, range, found=[]):
        if not range.intersects(self.limits):
            return found

        for p in self.points:
            if range.contains(p):
                found.append(p)

        if self.is_divided:
            self.I.query(range, found)
            self.II.query(range, found)
            self.III.query(range, found)
            self.IV.query(range, found)

        return found

    def draw(self, sup, color, transf):
        xi = self.limits.xi
        yi = self.limits.yi
        xf = self.limits.xf
        yf = self.limits.yf
        I = transf.transformar([xi, yi])
        F = transf.transformar([xf, yf])
        pygame.draw.rect(
            sup, color, (I[0], I[1], F[0] - I[0], F[1] - I[1]), width=1)
        # dibujar_rect_punteado(sup, color, I, F)

        if self.is_divided:
            self.I.draw(sup, color, transf)
            self.II.draw(sup, color, transf)
            self.III.draw(sup, color, transf)
            self.IV.draw(sup, color, transf)

        # for p in self.puntos:
        #     P = transf.transformar([p.x, p.y])
        #     pygame.draw.line(sup, color, (P[0] - 5, P[1] - 5), (P[0] + 5, P[1] + 5))
        #     pygame.draw.line(sup, color, (P[0] - 5, P[1] + 5), (P[0] + 5, P[1] - 5))
