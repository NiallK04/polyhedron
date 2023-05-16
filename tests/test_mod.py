from pytest import approx
from math import sqrt
from common.r3 import R3
from shadow.polyedr import Facet, Polyedr


class TestR3:
    def test_abs(self):
        vector = R3(1.0, 1.0, 1.0)
        assert abs(vector) == approx(sqrt(3))


class Test_1:
    def test_center1(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        f.get_c(1)
        assert f.is_center_ok()

    def test_angle1(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])

        assert f.is_angle_ok()

    def test_center2(self):
        f = Facet([R3(3.0, 3.0, 3.0), R3(3.0, -3.0, -3.0), R3(6.0, 6.0, -3.0)])
        f.get_c(1)
        assert not f.is_center_ok()

    def test_angle2(self):
        f = Facet([R3(0.0, 0.0, 1.0), R3(3.0, 2.0, 0.0), R3(0.0, -3.0, 0.0)])
        assert not f.is_angle_ok()


class Test_area:
    def test1(self):
        Polyedr1 = Polyedr("data/test_pir.geom")
        assert Polyedr1.area == approx(14412)

    def test2(self):
        Polyedr2 = Polyedr("data/test_tri.geom")
        assert Polyedr2.area == approx(7200)
