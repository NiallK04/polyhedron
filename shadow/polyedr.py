from math import pi, acos
from functools import reduce
from operator import add
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Segment:
    """ Одномерный отрезок """
    # Параметры конструктора: начало и конец отрезка (числа)

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    def __repr__(self):
        return f"{self.beg}, {self.fin}"

    # Отрезок вырожден?
    def is_degenerate(self):
        return self.beg >= self.fin

    # Пересечение с отрезком
    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    # Разность отрезков
    # Разность двух отрезков всегда является списком из двух отрезков!
    def subtraction(self, other):
        return [Segment(
            self.beg, self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)]





class Edge:
    """ Ребро полиэдра """
    # Начало и конец стандартного одномерного отрезка
    SBEG, SFIN = 0.0, 1.0

    # Параметры конструктора: начало и конец ребра (точки в R3)
    def __init__(self, beg, fin):
        self.vid = False
        self.beg, self.fin = beg, fin
        # Список «просветов»
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]
        self.s = self.gaps

    def __repr__(self):
        return f"{self.beg}, {self.fin}"

    # Учёт тени от одной грани
    def shadow(self, facet):
        # «Вертикальная» грань не затеняет ничего
        if facet.is_vertical():
            return
        # Нахождение одномерной тени на ребре
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(
                facet.vertexes[0], facet.h_normal()))
        if shade.is_degenerate():
            return
        # Преобразование списка «просветов», если тень невырождена
        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [
            s for s in reduce(add, gaps, []) if not s.is_degenerate()]


    # Преобразование одномерных координат в трёхмерные
    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    def is_fully_visible(self):
        if len(self.gaps) != 0 and self.gaps == self.s:
            self.vid = True



    # Пересечение ребра с полупространством, задаваемым точкой (a)
    # на плоскости и вектором внешней нормали (n) к ней
    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = - f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)




class Facet:
    """ Грань полиэдра """
    # Параметры конструктора: список вершин

    def __init__(self, vertexes):
        self.vid = False
        self.vertexes = vertexes
        self.edges = []
        for n in range(len(vertexes)):
            self.edges.append(Edge(vertexes[n - 1], vertexes[n]))

    def get_c(self, c):
        self.c = c

    def upd(self, edges_mod):
        tmp = []
        for i in self.edges:
            for j in edges_mod:
                if i.beg == j.beg and i.fin == j.fin:
                    tmp.append(j)
        self.edges = tmp

        self.is_fully_visible()


    # «Вертикальна» ли грань?
    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    def is_fully_visible(self):
        k = 0
        for i in self.edges:
            if i.vid:
                 k += 1

        self.vid = (k == len(self.edges))
    # Нормаль к «горизонтальному» полупространству
    def h_normal(self):
        n = (
            self.vertexes[1] - self.vertexes[0]).cross(
            self.vertexes[2] - self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    def is_angle_ok(self):
        return acos(abs((self.h_normal().dot(Polyedr.V)) / \
        (abs(self.h_normal())*abs(Polyedr.V)))) <= pi/7


    def is_center_ok(self):
        return self.center().x ** 2 + self.center().y ** 2 < 4 * self.c ** 2

    # Нормали к «вертикальным» полупространствам, причём k-я из них
    # является нормалью к грани, которая содержит ребро, соединяющее
    # вершины с индексами k-1 и k
    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    # Вспомогательный метод
    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * \
            (-1.0) if n.dot(self.vertexes[k - 1] - self.center()) < 0.0 else n

    # Центр грани
    def center(self):
        return sum(self.vertexes, R3(0.0, 0.0, 0.0)) * \
            (1.0 / len(self.vertexes))

    def area(self):
        area = 0.0
        for i in range(len(self.vertexes) - 2):
            v1 = self.vertexes[0]
            v2 = self.vertexes[i + 1]
            v3 = self.vertexes[i + 2]
            area += 0.5 * abs((v2 - v1).cross(v3 - v1))
        return area


class Polyedr:
    """ Полиэдр """
    # вектор проектирования
    V = R3(0.0, 0.0, 1.0)

    # Параметры конструктора: файл, задающий полиэдр
    def __init__(self, file):
        self.area = 0
        # списки вершин, рёбер и граней полиэдра
        self.vertexes, self.edges, self.facets = [], [], []

        # список строк файла
        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    # обрабатываем первую строку; buf - вспомогательный массив
                    buf = line.split()
                    # коэффициент гомотетии
                    c = float(buf.pop(0))
                    # углы Эйлера, определяющие вращение
                    alpha, beta, gamma = (float(x) * pi / 180.0 for x in buf)
                elif i == 1:
                    # во второй строке число вершин, граней и рёбер полиэдра
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    # задание всех вершин полиэдра
                    x, y, z = (float(x) for x in line.split())
                    self.vertexes.append(R3(x, y, z).rz(
                        alpha).ry(beta).rz(gamma) * c)
                else:
                    # вспомогательный массив
                    buf = line.split()
                    # количество вершин очередной грани
                    size = int(buf.pop(0))
                    # массив вершин этой грани
                    vertexes = list(self.vertexes[int(n) - 1] for n in buf)
                    # задание рёбер грани
                    for n in range(size):
                        self.edges.append(Edge(vertexes[n - 1], vertexes[n]))

                    # задание самой грани
                    facet1 = Facet(vertexes)
                    self.facets.append(facet1)
                    facet1.get_c(c)

            for e in self.edges:
                for f in self.facets:
                    e.shadow(f)
                e.is_fully_visible()
            for f in self.facets:
                f.upd(self.edges)
            self.mod()


    def mod(self):
        for i in self.facets:
            print(i.vid, i.is_angle_ok(), i.is_center_ok())
            if i.vid and i.is_angle_ok() and i.is_center_ok():
                self.area += i.area()
        return self.area
    # Метод изображения полиэдра
    def draw(self, tk):
        tk.clean()
        for e in self.edges:
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))
