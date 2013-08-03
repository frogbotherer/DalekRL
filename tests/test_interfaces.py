# test imports
from unit_environment import DalekTest
from nose.tools import *
from mock import Mock, MagicMock, patch

# lang imports
from functools import reduce
from math import hypot

# item under test
import libtcodpy as libtcod
import items
import interfaces

class InterfaceTest(DalekTest):
    pass

class PositionTest(InterfaceTest):

    def setUp(self):
        self.positions = [
            [ (4,3),   (9,2)    ],
            [ (-4,-3), (-9,-2)  ],
            [ (0,0), (0,0)      ],
            [ (100000000,100000000), (-100000000,-100000000) ],
            [ (1,-1), (-1,1)    ],
            ]

        self.angle_positions = [
            [ (0,1),  (1,0),   0.5 ],
            [ (0,1),  (0,-1),  1.0 ],
            [ (0,1),  (-1,0),  0.5 ],
            [ (5,0),  (5,0),   0.0 ],
            [ (0,0),  (1,0),   0.5 ],
            [ (0,0),  (-1,0),   0.5 ],
            [ (0,0),  (0,0),   0.0 ],
            [ (0,1),  (1,1),   0.25 ],
            ]

    def test_should_add_position(self):
        
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1[0], rp1[1])
            p2 = interfaces.Position(rp2[0], rp2[1])

            p3 = p1 + p2

            assert_equal( p3.x, p1.x+p2.x )
            assert_equal( p3.y, p1.y+p2.y )

    def test_should_add_tuple(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1[0], rp1[1])
            p2 = rp2

            p3 = p1 + p2

            assert_equal( p3.x, p1.x+p2[0] )
            assert_equal( p3.y, p1.y+p2[1] )

    def test_should_sub_position(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1[0], rp1[1])
            p2 = interfaces.Position(rp2[0], rp2[1])

            p3 = p1 - p2

            assert_equal( p3.x, p1.x-p2.x )
            assert_equal( p3.y, p1.y-p2.y )

    def test_should_sub_tuple(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1[0], rp1[1])
            p2 = rp2

            p3 = p1 - p2

            assert_equal( p3.x, p1.x-p2[0] )
            assert_equal( p3.y, p1.y-p2[1] )

    def test_should_init_with_tuple(self):
        for (rp1, rp2) in self.positions:
            p = interfaces.Position(rp1)
            assert_equal(p.x,rp1[0])
            assert_equal(p.y,rp1[1])

    def test_should_init_with_position(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1[0],rp1[1])
            p2 = interfaces.Position(p1)

            assert_equal(p1,p2)
            assert_is_not(p1,p2)
            assert_equal(p1.x,p2.x)
            assert_equal(p1.y,p2.y)

    def test_should_be_greater_than_position(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 > p2:
                assert p1.distance_to((0,0)) > p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x>p2.x), "%s > %s" %(p1,p2)

            else:
                assert p1.distance_to((0,0)) <= p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x<=p2.x), "%s <= %s" %(p1,p2)
                
    def test_should_be_greater_than_tuple(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 > rp2:
                assert p1.distance_to((0,0)) > p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x>p2.x), "%s > %s" %(p1,p2)

            else:
                assert p1.distance_to((0,0)) <= p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x<=p2.x), "%s <= %s" %(p1,p2)

    def test_should_be_less_than_position(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 < p2:
                assert p1.distance_to((0,0)) < p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x<p2.x), "%s < %s" %(p1,p2)

            else:
                assert p1.distance_to((0,0)) >= p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x>=p2.x), "%s >= %s" %(p1,p2)

    def test_should_be_less_than_tuple(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 < rp2:
                assert p1.distance_to((0,0)) < p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x<p2.x), "%s < %s" %(p1,p2)

            else:
                assert p1.distance_to((0,0)) >= p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x>=p2.x), "%s >= %s" %(p1,p2)

    def test_should_be_equal_to_position(self):
        for (rp1, rp2) in self.positions:
            assert_equal( interfaces.Position(rp1), interfaces.Position(rp1) )
            assert_equal( interfaces.Position(rp2), interfaces.Position(rp2) )

    def test_should_be_equal_to_tuple(self):
        for (rp1, rp2) in self.positions:
            assert_equal( interfaces.Position(rp1), rp1 )
            assert_equal( interfaces.Position(rp2), rp2 )

    def test_should_be_hashable(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            h1  = {p1: 1}
            h2  = {p2: 2}

            assert_equal(h1[p1],1)
            assert_equal(h2[p2],2)

            assert_equal(h1[rp1],1)
            assert_equal(h2[rp2],2)

    def test_should_calc_distance_to_position(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)

            # check symmetry too
            d1 = p1.distance_to(p2)
            d2 = p2.distance_to(p1)

            assert_equal(d1,d2)
            assert_equal(d1,hypot(p2.x-p1.x,p2.y-p1.y))

    def test_should_calc_distance_to_tuple(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)

            # check symmetry too
            d1 = p1.distance_to(rp2)
            d2 = p2.distance_to(rp1)

            assert_equal(d1,d2)
            assert_equal(d1,hypot(p2.x-p1.x,p2.y-p1.y))

    def test_should_calc_angle_between_position(self):
        for (rp1, rp2, angle) in self.angle_positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            assert_equal(p1.angle_to(p2),angle)
            assert_equal(p2.angle_to(p1),angle)

    def test_should_calc_angle_between_tuple(self):
        for (rp1, rp2, angle) in self.angle_positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            assert_equal(p1.angle_to(rp2),angle,"%s v %s = %f? %f"%(p1,p2,angle,p1.angle_to(p2)))
            assert_equal(p2.angle_to(rp1),angle)


