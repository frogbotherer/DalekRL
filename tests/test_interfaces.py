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
import maps
import player
import tiles
import errors

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


class MappableTest(InterfaceTest):
    
    def setUp(self):
        self.map = Mock(spec=maps.Map)
        self.map.player = Mock(spec_set=player.Player)
        self.map.player.has_effect = Mock(return_value=False)
        self.map.light_level = Mock(return_value=5.0)
        self.map.light_colour = Mock(return_value=libtcod.white)
        libtcod.console_put_char_ex = Mock()

    def tearDown(self):
        libtcod.console_put_char_ex.reset_mock()

    def test_should_prevent_movement_if_fixed_in_place(self):
        m = interfaces.Mappable(interfaces.Position(1,1),'x',libtcod.white,remains_in_place=True)
        self.map.add(m)
        assert_true(m.remains_in_place)
        assert_raises(AssertionError,m.move,(1,1))
        assert_raises(AssertionError,m.move_to,(2,2))

    def test_should_fail_movement_if_not_on_map(self):
        m = interfaces.Mappable(interfaces.Position(1,1),'x',libtcod.white)
        assert_is(m.map,None)
        assert_raises(AssertionError,m.move,(1,1))
        assert_raises(AssertionError,m.move_to,(2,2))

    def test_should_move_by_delta(self):
        for d in (
            (1,1),
            (10,10),
            (-1,-1),
            (-10,10),
            ):
            map = Mock(spec_set=maps.Map)
            m = interfaces.Mappable(interfaces.Position(1,1),'x',libtcod.white)
            m.map = map
            m.move(d)
            map.move.assert_called_once_with(m, m.pos + d)

    def test_should_move_to_valid_pos(self):
        for d in (
            (1,1),
            (10,10),
            (40,26),
            ):
            map = Mock(spec_set=maps.Map)
            m = interfaces.Mappable(interfaces.Position(1,1),'x',libtcod.white)
            m.map = map
            m.move_to(d)
            map.move.assert_called_once_with(m, d)

    def test_should_prevent_movement_to_invalid_pos(self):
        for d in (
            (-1,-1),
            (-10,10),
            (90,55),
            ):
            map = Mock(spec_set=maps.Map)
            map.move = Mock(side_effect=errors.InvalidMoveError())
            m = interfaces.Mappable(interfaces.Position(1,1),'x',libtcod.white)
            m.map = map
            assert_raises(errors.InvalidMoveError,m.move_to, d)
            map.move.assert_called_once_with(m, d)

    def test_should_not_be_lit_if_not_on_map(self):
        m = interfaces.Mappable(None,'x',libtcod.white)
        m.map = Mock(spec_set=maps.Map)
        assert_is(m.pos,None)
        assert_false(m.is_lit)

        m.map = None
        m.pos = Mock(spec_set=interfaces.Position)
        assert_false(m.is_lit)

    def test_should_use_map_data_for_lighting_tests(self):
        m = interfaces.Mappable(Mock(spec_set=interfaces.Position),'x',libtcod.white)
        m.map = Mock(spec_set=maps.Map)
        m.map.is_lit = Mock(return_value=True)
        assert_true(m.is_lit)
        m.map.is_lit.assert_called_once_with(m)

    def test_should_give_low_light_level_when_not_on_map(self):
        m = interfaces.Mappable(Mock(spec_set=interfaces.Position),'x',libtcod.white)
        assert_equal(m.light_level,interfaces.LightSource.INTENSITY_L_CLAMP)

    def test_should_give_transparent_light_level_if_transparent(self):
        # seems Mock() doesn't play nicely with @property
        class T(interfaces.Mappable,interfaces.Transparent):
            transparent_light_level = 5.0

        m = T(Mock(spec_set=interfaces.Position),'x',libtcod.white)
        m.map = self.map
        assert_equal(m.light_level,5.0)

    def test_should_use_map_data_for_light_level(self):
        m = interfaces.Mappable(Mock(spec_set=interfaces.Position),'x',libtcod.white)
        m.map = self.map
        #m.map.light_level = Mock(return_value=5.0)
        assert_equal(m.light_level,5.0)
        m.map.light_level.assert_called_once_with(m.pos)

    def test_should_not_be_drawn_if_not_visible(self):
        m = interfaces.Mappable(Mock(spec_set=interfaces.Position),'x',libtcod.white)
        m.map = self.map
        m.is_visible = False

        assert_is(m.draw(),None)

        assert_equal(libtcod.console_put_char_ex.call_count,0)

    def test_should_not_be_drawn_if_not_visible_to_player_and_not_previously_seen(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white)
        m.map = self.map
        m.visible_to_player = False

        assert_false(m.has_been_seen)
        assert_is(m.draw(),None)
        assert_false(m.has_been_seen)

    def test_should_be_drawn_according_to_incident_light_level(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white)
        m.map = self.map
        m.visible_to_player = True

        for (my_colour,colour,level) in (
            (libtcod.white,libtcod.white,1.0),
            (libtcod.white,libtcod.red,0.5),
            (libtcod.white,libtcod.white,interfaces.LightSource.INTENSITY_L_CLAMP+0.1),
            (libtcod.green,libtcod.white,1.0),
            (libtcod.red,libtcod.blue,1.2),
            #(libtcod.green,interfaces.LightSource.INTENSITY_L_CLAMP), # see below
            ):
            m.colour = my_colour
            self.map.light_level = Mock(return_value=level)
            self.map.light_colour = Mock(return_value=colour*level)
            assert_is(m.draw(),None)
            #self.map.light_level.assert_called_once_with(m) # copied for performance into m
            self.map.light_colour.assert_called_once_with(p)
            libtcod.console_put_char_ex.assert_called_with(0,p.x,p.y,'x',my_colour*colour*level,libtcod.BKGND_NONE)

    def test_should_use_unseen_tile_when_static_and_not_visible(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white, unseen_symbol='y', unseen_colour=libtcod.red)
        m.map = self.map
        m.visible_to_player = False
        m.has_been_seen = True
        m.remains_in_place = True

        assert_is(m.draw(),None)
        libtcod.console_put_char_ex.assert_called_with(0,p.x,p.y,'y',libtcod.red,libtcod.BKGND_NONE)

    def test_should_not_be_drawn_if_moving_and_not_visible(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white, unseen_symbol='y', unseen_colour=libtcod.red)
        m.map = self.map
        m.visible_to_player = False
        m.has_been_seen = True
        m.remains_in_place = False

        assert_is(m.draw(),None)
        assert_equal(libtcod.console_put_char_ex.call_count,0)

    def test_should_use_unseen_tile_when_remembered_and_in_dark(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white, unseen_symbol='y', unseen_colour=libtcod.red)
        m.map = self.map
        m.visible_to_player = True
        m.has_been_seen = True
        m.remains_in_place = True
        self.map.light_level = Mock(return_value=interfaces.LightSource.INTENSITY_L_CLAMP-0.1)
        self.map.light_colour = Mock(return_value=libtcod.white*(interfaces.LightSource.INTENSITY_L_CLAMP-0.1))

        assert_is(m.draw(),None)
        self.map.light_colour.assert_called_once_with(p)
        libtcod.console_put_char_ex.assert_called_with(0,p.x,p.y,'y',libtcod.red,libtcod.BKGND_NONE)

    def test_should_not_be_drawn_if_moving_remembered_and_in_dark(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white, unseen_symbol='y', unseen_colour=libtcod.red)
        m.map = self.map
        m.visible_to_player = True
        m.has_been_seen = True
        m.remains_in_place = False
        self.map.light_level = Mock(return_value=interfaces.LightSource.INTENSITY_L_CLAMP-0.1)
        self.map.light_colour = Mock(return_value=libtcod.white*(interfaces.LightSource.INTENSITY_L_CLAMP-0.1))

        assert_is(m.draw(),None)
        self.map.light_colour.assert_called_once_with(p)
        assert_equal(libtcod.console_put_char_ex.call_count,0)

    def test_should_see_moving_tile_as_bright_with_infravision(self):
        # TODO: should be 'warm tile'
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white, unseen_symbol='y', unseen_colour=libtcod.red)
        m.map = self.map
        m.visible_to_player = True
        m.has_been_seen = True
        m.remains_in_place = False
        self.map.light_level = Mock(return_value=interfaces.LightSource.INTENSITY_L_CLAMP-0.1)
        self.map.light_colour = Mock(return_value=libtcod.white*(interfaces.LightSource.INTENSITY_L_CLAMP-0.1))

        self.map.player.has_effect.side_effect = lambda x: x == interfaces.StatusEffect.INFRAVISION

        assert_is(m.draw(),None)
        assert_equal(self.map.light_colour.call_count,0) # don't need to test light colour if max lit
        libtcod.console_put_char_ex.assert_called_with(0,p.x,p.y,'x',libtcod.white,libtcod.BKGND_NONE)

    def test_should_see_stationary_tile_as_dim_with_infravision(self):
        # TODO: should be 'cold tile'
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white, unseen_symbol='y', unseen_colour=libtcod.red)
        m.map = self.map
        m.visible_to_player = True
        m.has_been_seen = True
        m.remains_in_place = True
        self.map.light_level = Mock(return_value=interfaces.LightSource.INTENSITY_L_CLAMP-0.1)
        self.map.light_colour = Mock(return_value=libtcod.white*(interfaces.LightSource.INTENSITY_L_CLAMP-0.1))

        self.map.player.has_effect.side_effect = lambda x: x == interfaces.StatusEffect.INFRAVISION

        assert_is(m.draw(),None)
        self.map.light_colour.assert_called_once_with(p)
        libtcod.console_put_char_ex.assert_called_with(0,p.x,p.y,'y',libtcod.red,libtcod.BKGND_NONE)

    def test_should_invert_lighting_with_night_vision(self):
        pass

    def test_should_flag_as_seen_once_drawn(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white)
        m.map = self.map
        m.visible_to_player = True

        assert_false(m.has_been_seen)
        assert_is(m.draw(),None)
        assert_true(m.has_been_seen)
