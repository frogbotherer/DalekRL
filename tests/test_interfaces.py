# test imports
from unit_environment import DalekTest
from nose.tools import *
from mock import Mock, MagicMock, patch, ANY

# lang imports
from functools import reduce
from math import hypot
import gc

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
            [ (11,4), (1,1)     ],
            [ (11,4), (9,9)     ],
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
        # assert p > q
        for (px, py, qx, qy, result) in (
            ( 1,  1,  3,  3, False ),
            ( 3,  3,  1,  1, True  ),
            ( 3,  1,  1,  1, False ), # not in bounding box
            ( 3,  1,  1,  0, True  ),
            ( 1,  1,  1,  3, False ),
            ( 1,  8,  2,  3, False ),
            ( 5,  5,  6,  1, False  ),
            ):
            p1 = interfaces.Position(px,py)
            p2 = interfaces.Position(qx,qy)
            assert_equal(p1 > p2, result)

        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 > p2:
                assert p1.x > p2.x and p1.y > p2.y
            # these operators are not symmetrical!
            #else:
            #    assert p1.x <= p2.x and p1.y <= p2.y, "%s <= %s" %(p1,p2)
                
    def test_should_be_greater_than_tuple(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 > rp2:
                assert p1.x > p2.x and p1.y > p2.y
            # these operators are not symmetrical!
            #else:
            #    assert p1.distance_to((0,0)) <= p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x<=p2.x), "%s <= %s" %(p1,p2)

    def test_should_be_less_than_position(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 < p2:
                assert p1.x < p2.x and p1.y < p2.y
            # these operators are not symmetrical!
            #else:
            #    assert p1.distance_to((0,0)) >= p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x>=p2.x), "%s >= %s" %(p1,p2)

    def test_should_be_less_than_tuple(self):
        for (rp1, rp2) in self.positions:
            p1 = interfaces.Position(rp1)
            p2 = interfaces.Position(rp2)
            if p1 < rp2:
                assert p1.x < p2.x and p1.y < p2.y

            # these operators are not symmetrical!
            #else:
            #    assert p1.distance_to((0,0)) >= p2.distance_to((0,0)) or (p1.distance_to((0,0))==p2.distance_to((0,0)) and p1.x>=p2.x), "%s >= %s" %(p1,p2)

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
        class T(interfaces.Transparent,interfaces.Mappable):
            transparent_light_level = 5.0
            def __init__(self,*args,**kwargs):
                interfaces.Mappable.__init__(self,*args,**kwargs)
                interfaces.Transparent.__init__(self)

        m = T(interfaces.Position(0,0),'x',libtcod.white)
        m.map = self.map
        m.map.player = Mock(spec=player.Player)
        m.map.player.pos = interfaces.Position(1,1)
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

    def test_should_invert_lighting_with_night_vision_and_visible(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white)
        m.map = self.map
        m.visible_to_player = True

        self.map.player.has_effect.side_effect = lambda x: x == interfaces.StatusEffect.NIGHT_VISION

        for (my_colour,colour,level) in (
            (libtcod.white,libtcod.white,0.0),
            (libtcod.white,libtcod.red,0.5),
            (libtcod.white,libtcod.white,interfaces.LightSource.INTENSITY_L_CLAMP+0.1),
            (libtcod.green,libtcod.white,0.8), # close to 1.0-L_CLAMP
            (libtcod.red,libtcod.blue,0.5),
            #(libtcod.green,interfaces.LightSource.INTENSITY_L_CLAMP), # see below
            ):
            m.colour = my_colour
            self.map.light_level = Mock(return_value=level)
            self.map.light_colour = Mock(return_value=colour*level)
            assert_is(m.draw(),None)
            #self.map.light_level.assert_called_once_with(m) # copied for performance into m
            self.map.light_colour.assert_called_once_with(p)
            libtcod.console_put_char_ex.assert_called_with(0,p.x,p.y,'x',my_colour*(libtcod.white-(colour*level)),libtcod.BKGND_NONE)

    def test_should_see_remembered_tiles_as_usual_with_night_vision(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white, unseen_symbol='y', unseen_colour=libtcod.red)
        m.map = self.map
        m.visible_to_player = True
        m.has_been_seen = True
        m.remains_in_place = True
        # default bright white light

        self.map.player.has_effect.side_effect = lambda x: x == interfaces.StatusEffect.NIGHT_VISION

        assert_is(m.draw(),None)
        self.map.light_colour.assert_called_once_with(p)
        libtcod.console_put_char_ex.assert_called_with(0,p.x,p.y,'y',libtcod.red,libtcod.BKGND_NONE)

    def test_should_flag_as_seen_once_drawn(self):
        p = Mock(spec=interfaces.Position,x=1,y=1)
        m = interfaces.Mappable(p,'x',libtcod.white)
        m.map = self.map
        m.visible_to_player = True

        assert_false(m.has_been_seen)
        assert_is(m.draw(),None)
        assert_true(m.has_been_seen)


class LightSourceTest(InterfaceTest):
    # can't instantiate LightSource by itself
    class C(interfaces.LightSource,interfaces.Mappable):
        def __init__(self,*args,**kwargs):
            interfaces.LightSource.__init__(self,*args,**kwargs)
            interfaces.Mappable.__init__(self,None,'x',libtcod.white)

    def setUp(self):
        libtcod.map_compute_fov     = Mock()
        libtcod.map_set_properties  = Mock()
        libtcod.image_clear         = Mock()
        libtcod.image_set_key_color = Mock()
        libtcod.image_put_pixel     = Mock()
        libtcod.image_blit_rect     = Mock()
        libtcod.map_delete          = Mock()
        libtcod.image_delete        = Mock()

    def test_should_reset_when_radius_changes(self):
        c = self.C(radius=1)
        c.reset_map = Mock()
        assert_equal(c.radius,1)
        c.radius = 2
        assert_equal(c.radius,2)
        c.reset_map.assert_called_once_with()

    def test_should_still_work_as_light_after_radius_changes(self):
        c = self.C(radius=1)
        c.reset_map = Mock()
        c.prepare_fov = Mock()
        c.light_enabled = True
        p = Mock(spec=interfaces.Position)
        c.pos = p
        c.map = Mock(spec=maps.Map)
        c.radius = 3
        # stays centred in same place
        assert_equal(c.pos,p)
        # LOS et al recalculated
        c.reset_map.assert_called_once_with()
        #c.prepare_fov.assert_called_once_with(ANY) # cos its parent is a mock!
        # still enabled
        assert_true(c.light_enabled)

    def test_should_prepare_fov_over_whole_area_of_light(self):
        for (r, dia) in (
            (1,3),
            (2,5),
            (5,11),
            ):
            c = self.C(r)
            assert_is(c.prepare_fov(),None)
            libtcod.map_compute_fov.assert_called_with(ANY,r+1,r+1,r,ANY,ANY)
    
    def test_should_clear_light_map_to_black_if_reset_when_disabled(self):
        c = self.C(5)
        c.light_enabled = False

        assert_is(c.reset_map(),None)
        libtcod.image_clear.assert_called_once_with(ANY,libtcod.black)
        libtcod.image_set_key_color.assert_called_once_with(ANY,libtcod.black)
    
    def test_should_fail_if_reset_when_not_on_map(self):
        c = self.C(1)
        c.map = None
        
        assert_raises(AssertionError,c.reset_map)

        c.map = Mock(spec=maps.Map)
        c.pos = None

        assert_raises(AssertionError,c.reset_map)

    def test_should_reset_whole_light_map_when_called_with_no_pos(self):
        # TODO: apply this test with various radii (as there was a bug when radius was even number)
        # define a test light like this
        # .....        .....             
        # .....        .###.        ### 
        # ..'..   -->  .#'..   -->  #'..
        # .....        .#/..        #/..
        # .....        .....         ...
        c = self.C(radius=2)
        c.light_enabled = True
        c.intensity = 1.0
        c.pos = interfaces.Position(2,2)
        c.map = Mock(spec=maps.Map)
        m = [
                tiles.Floor(interfaces.Position(0,0)),
                tiles.Floor(interfaces.Position(1,0)),
                tiles.Floor(interfaces.Position(2,0)),
                tiles.Floor(interfaces.Position(3,0)),
                tiles.Floor(interfaces.Position(4,0)),
                tiles.Floor(interfaces.Position(0,1)),
                tiles.Floor(interfaces.Position(5,1)),
                tiles.Floor(interfaces.Position(0,2)),
                tiles.Floor(interfaces.Position(2,2)),
                tiles.Floor(interfaces.Position(3,2)),
                tiles.Floor(interfaces.Position(4,2)),
                tiles.Floor(interfaces.Position(0,3)),
                tiles.Floor(interfaces.Position(3,3)),
                tiles.Floor(interfaces.Position(4,3)),
                tiles.Floor(interfaces.Position(0,4)),
                tiles.Floor(interfaces.Position(1,4)),
                tiles.Floor(interfaces.Position(2,4)),
                tiles.Floor(interfaces.Position(3,4)),
                tiles.Floor(interfaces.Position(4,4)),
                tiles.Window(interfaces.Position(2,3)),
                ]
        c.map.find_all_within_r = Mock(return_value = m)
        libtcod.map_is_in_fov = Mock( side_effect = lambda n,x,y: x>1 and y>1 )

        assert_is(c.reset_map(None),None)

        c.map.find_all_within_r.assert_called_once_with(c,interfaces.Transparent,c.radius)
        libtcod.map_compute_fov.assert_called_once_with(ANY,c.radius+1,c.radius+1,c.radius,ANY,ANY)
        libtcod.image_clear.assert_called_once_with(ANY,libtcod.black)
        libtcod.image_set_key_color.assert_called_once_with(ANY,libtcod.black)
        for p in m:
            libtcod.map_set_properties.assert_any_call(ANY,p.pos.x,p.pos.y,isinstance(p,interfaces.Transparent) and not p.blocks_light(),True)

        for p in (
            ## would be this, but we light walls differently
            #(1,1),(2,1),(3,1),       #   ###
            #(1,2),(2,2),(3,2),(4,2), #   #'..
            #(1,3),(2,3),(3,3),(4,3), #   #/..
            #(1,4),(2,4),(3,4),(4,4), #    ...
                                         #   ###
            (2,2,255),(3,2,255),(4,2,0), #   #'..
            (2,3,255),(3,3,149),(4,3,0), #   #/..
            (2,4,0),(3,4,0),(4,4,0),     #    ...
            ):
            libtcod.image_put_pixel.assert_any_call(ANY,p[0],p[1],libtcod.white*(p[2]/255))

    def test_should_reset_only_relevant_parts_when_pos_given(self):
        for (r, cx, cy) in (
            (3, 3, 2),
            (2, 2, 3),
            (5, 8, 9),
            ):
            px = r; py = r
            c = self.C(radius=r)
            c.light_enabled = True
            c.intensity = 1.0
            c.pos = interfaces.Position(px,py)
            c.map = Mock(spec=maps.Map)
            c.map.find_all_at_pos = Mock( return_value = [tiles.Window(interfaces.Position(cx,cy))] )

            assert_is(c.reset_map(pos=interfaces.Position(cx,cy)),None)
            libtcod.map_set_properties.assert_called_once_with(ANY,cx,cy,True,True)
            libtcod.map_set_properties.reset_mock()

    def test_should_not_recalculate_if_pos_out_of_los(self):
        for (r, cx, cy) in (
            (3, 0, 0),
            (2, 4, 4),
            (5, 9, 9),
            ):
            px = r; py = r
            c = self.C(radius=r)
            c.light_enabled = True
            c.intensity = 1.0
            c.pos = interfaces.Position(px,py)
            c.prepare_fov = Mock()
            c.map = Mock(spec=maps.Map)
            c.map.find_all_at_pos = Mock( return_value = [tiles.Window(interfaces.Position(cx,cy))] )

            assert_is(c.reset_map(pos=interfaces.Position(cx,cy)),None)
            assert_equal(libtcod.map_set_properties.call_count,0)
            assert_equal(c.prepare_fov.call_count,0)

    def test_should_blit_image_data_to_console_at_given_coords(self):
        # e.g. pos (3,3), r=2
        #    |
        #  X...      ox, oy = (0,0); tlx, tly = (1,1)
        #  .....
        # -..'..
        #  .....
        #   ...      sx, sy = (5,5)
        #
        for (r, con, px, py, ox, oy, sx, sy, tlx, tly) in (
            (3, 0,   3,  3,  0,  0,  -1, -1, 0,   0  ),
            (3, 1,   9,  9,  0,  0,  -1, -1, 6,   6, ),
            (1, 1,   2,  2,  0,  0,  -1, -1, 1,   1, ),
            (4, 4,   8,  6,  0,  0,  -1, -1, 4,   2, ),
            ):
            c = self.C(radius=r)
            c.pos = interfaces.Position(px, py)
            assert_is( c.blit_to(con, ox, oy, sx, sy), None )
            libtcod.image_blit_rect.assert_called_once_with(
                ANY, con,
                tlx, tly,
                sx, sy,
                libtcod.BKGND_ADD)
            libtcod.image_blit_rect.reset_mock()

    def test_should_not_light_things_when_disabled(self):
        c = self.C(radius=3)
        c.light_enabled = False
        c.pos = interfaces.Position(4,4)
        
        for p in (
            (0,0),
            (4,4),
            (4,7),
            (7,4),
            (1,1),
            ):
            assert_false(c.lights(p))

    def test_should_not_light_things_outside_radius(self):
        c = self.C(radius=3)
        c.light_enabled = True
        c.pos = interfaces.Position(4,4)
        
        for p in (
            (0,0),
            (1,1),
            (4,8),
            (8,4),
            (6,7),
            ):
            assert_false(c.lights(p))

    def test_should_always_light_things_in_radius_if_not_testing_los(self):
        c = self.C(radius=3)
        c.light_enabled = True
        c.pos = interfaces.Position(4,4)
        
        for p in (
            (3,3),
            (4,4),
            (4,7),
            (7,4),
            (6,5),
            ):
            assert_true(c.lights(p,test_los=False))

    def test_should_use_los_data_for_lighting_check(self):
        c = self.C(radius=4)
        c.light_enabled = True
        c.intensity = 1.0
        c.pos = interfaces.Position(4,4)
        c.map = Mock(spec=maps.Map)
        libtcod.map_is_in_fov = Mock(return_value=True)

        for p in (
            (3,3),
            (4,4),
            (4,7),
            (7,4),
            (6,5),
            ):
            print(p)
            assert_true(c.lights(interfaces.Position(p)))
            libtcod.map_is_in_fov.assert_called_once_with(ANY,p[0],p[1],)
            libtcod.map_is_in_fov.reset_mock()

    def test_should_clean_up_tcod_data_on_reset(self):
        c = self.C(radius=3)
        c.map = Mock(spec=maps.Map)
        c.map.find_all_within_r = Mock(return_value=[])
        c.pos = Mock(spec=interfaces.Position)
        c.radius = 5
        libtcod.map_delete.assert_called_once_with(ANY)
        libtcod.image_delete.assert_called_once_with(ANY)

    def test_should_clean_up_tcod_data_on_del(self):
        c = self.C(radius=5)
        c.map = Mock(spec=maps.Map)
        c.map.find_all_within_r = Mock(return_value=[])
        c.pos = Mock(spec=interfaces.Position)
        #c.reset_map()  # creates references preventing c from being deleted

        del c
        gc.collect()

        libtcod.map_delete.assert_called_once_with(ANY)
        libtcod.image_delete.assert_called_once_with(ANY)

    def test_should_be_disabled_after_closed(self):
        c = self.C(radius=5)
        c.map = Mock(spec=maps.Map)
        c.map.find_all_within_r = Mock(return_value=[])
        c.pos = Mock(spec=interfaces.Position)
        c.reset_map()

        c.close()

        libtcod.map_delete.assert_called_once_with(ANY)
        libtcod.image_delete.assert_called_once_with(ANY)
        assert_false(c.light_enabled)


class FlatLightSourceTest(InterfaceTest):
    # can't instantiate LightSource by itself
    class C(interfaces.FlatLightSource,interfaces.Mappable):
        def __init__(self,*args,**kwargs):
            interfaces.FlatLightSource.__init__(self,*args,**kwargs)
            interfaces.Mappable.__init__(self,None,'x',libtcod.white)

    def setUp(self):
        libtcod.map_compute_fov     = Mock()
        libtcod.map_set_properties  = Mock()
        libtcod.image_clear         = Mock()
        libtcod.image_set_key_color = Mock()
        libtcod.image_put_pixel     = Mock()
        libtcod.image_blit_rect     = Mock()
        libtcod.map_delete          = Mock()
        libtcod.image_delete        = Mock()

    def test_should_reset_when_size_changes(self):
        s = interfaces.Position(5,5)
        c = self.C(size=s)
        c.reset_map = Mock()
        assert_equal(c.size,s)
        c.size = interfaces.Position(3,3)
        assert_equal(c.size,interfaces.Position(3,3))
        c.reset_map.assert_called_once_with()

    def test_should_still_work_as_light_after_size_changes(self):
        c = self.C(size=interfaces.Position(5,5))
        c.reset_map = Mock()
        c.prepare_fov = Mock()
        c.light_enabled = True
        p = Mock(spec=interfaces.Position)
        c.pos = p
        c.map = Mock(spec=maps.Map)
        c.size = interfaces.Position(3,3)
        # stays centred in same place
        assert_equal(c.pos,p)
        # LOS et al recalculated
        c.reset_map.assert_called_once_with()
        #c.prepare_fov.assert_called_once_with(ANY) # cos its parent is a mock!
        # still enabled
        assert_true(c.light_enabled)

    def test_should_prepare_fov_over_whole_area_of_light(self):
        for (px, py, r) in (
            (1,  3,  2),
            (5,  2,  3),
            (5, 11,  6),
            ):
            c = self.C(interfaces.Position(px,py))
            assert_is(c.prepare_fov(False),None)
            libtcod.map_compute_fov.assert_called_with(ANY,px//2,py//2,r,False,ANY)
    
    def test_should_clear_light_map_to_black_if_reset_when_disabled(self):
        c = self.C(interfaces.Position(5,5))
        c.light_enabled = False

        assert_is(c.reset_map(),None)
        libtcod.image_clear.assert_called_once_with(ANY,libtcod.black)
        libtcod.image_set_key_color.assert_called_once_with(ANY,libtcod.black)

    def test_should_fail_if_reset_when_not_on_map(self):
        c = self.C(interfaces.Position(5,5))
        c.map = None
        
        assert_raises(AssertionError,c.reset_map)

        c.map = Mock(spec=maps.Map)
        c.pos = None

        assert_raises(AssertionError,c.reset_map)

    def test_should_reset_whole_light_map_when_called_with_no_pos(self):
        c = self.C(interfaces.Position(3,3))
        c.light_enabled = True
        c.intensity = 1.0
        c.pos = interfaces.Position(2,2)
        c.map = Mock(spec=maps.Map)

        assert_is(c.reset_map(None),None)
        libtcod.image_clear.assert_called_once_with(ANY,libtcod.white)
        libtcod.image_set_key_color.assert_called_once_with(ANY,libtcod.black)

    def test_should_blit_image_data_to_console_at_given_coords(self):
        # e.g. pos (1,1), s=(5,5)
        #    |
        #  X....     ox, oy = (0,0); tlx, tly = (1,1)
        #  .....
        # -..'..
        #  .....
        #  .....     sx, sy = (5,5)
        #
        for (r, con, px, py, ox, oy, sx, sy, tlx, tly) in (
            (6, 0,   3,  3,  0,  0,  -1, -1, 2,   2  ),
            (6, 1,   9,  9,  0,  0,  -1, -1, 8,   8, ),
            (3, 1,   2,  2,  0,  0,  -1, -1, 1,   1, ),
            (8, 4,   8,  6,  0,  0,  -1, -1, 7,   5, ),
            ):
            c = self.C(size=interfaces.Position(r,r))
            c.pos = interfaces.Position(px, py)
            assert_is( c.blit_to(con, ox, oy, sx, sy), None )
            libtcod.image_blit_rect.assert_called_once_with(
                ANY, con,
                tlx, tly,
                sx, sy,
                libtcod.BKGND_ADD)
            libtcod.image_blit_rect.reset_mock()

    def test_should_not_light_things_when_disabled(self):
        c = self.C(size=interfaces.Position(7,7))
        c.light_enabled = False
        c.pos = interfaces.Position(0,0)
        
        for p in (
            (0,0),
            (4,4),
            (4,7),
            (7,4),
            (1,1),
            ):
            assert_false(c.lights(p))

    def test_should_not_light_things_outside_radius(self):
        c = self.C(size=interfaces.Position(7,7))
        c.light_enabled = True
        c.pos = interfaces.Position(2,2)
        
        for p in (
            (0,0),
            (1,0),
            (4,11),
            (11,4),
            (11,11),
            ):
            print(p)
            assert_false(c.lights(p))

class todo:


    def todo_test_should_always_light_things_in_radius_if_not_testing_los(self):
        c = self.C(radius=3)
        c.light_enabled = True
        c.pos = interfaces.Position(4,4)
        
        for p in (
            (3,3),
            (4,4),
            (4,7),
            (7,4),
            (6,5),
            ):
            assert_true(c.lights(p,test_los=False))

    def todo_est_should_use_los_data_for_lighting_check(self):
        c = self.C(radius=4)
        c.light_enabled = True
        c.intensity = 1.0
        c.pos = interfaces.Position(4,4)
        c.map = Mock(spec=maps.Map)
        libtcod.map_is_in_fov = Mock(return_value=True)

        for p in (
            (3,3),
            (4,4),
            (4,7),
            (7,4),
            (6,5),
            ):
            print(p)
            assert_true(c.lights(interfaces.Position(p)))
            libtcod.map_is_in_fov.assert_called_once_with(ANY,p[0],p[1],)
            libtcod.map_is_in_fov.reset_mock()

    def todo_test_should_clean_up_tcod_data_on_reset(self):
        c = self.C(radius=3)
        c.map = Mock(spec=maps.Map)
        c.map.find_all_within_r = Mock(return_value=[])
        c.pos = Mock(spec=interfaces.Position)
        c.radius = 5
        libtcod.map_delete.assert_called_once_with(ANY)
        libtcod.image_delete.assert_called_once_with(ANY)

    def todo_test_should_clean_up_tcod_data_on_del(self):
        c = self.C(radius=5)
        c.map = Mock(spec=maps.Map)
        c.map.find_all_within_r = Mock(return_value=[])
        c.pos = Mock(spec=interfaces.Position)
        #c.reset_map()  # creates references preventing c from being deleted

        del c
        gc.collect()

        libtcod.map_delete.assert_called_once_with(ANY)
        libtcod.image_delete.assert_called_once_with(ANY)

    def todo_test_should_be_disabled_after_closed(self):
        c = self.C(radius=5)
        c.map = Mock(spec=maps.Map)
        c.map.find_all_within_r = Mock(return_value=[])
        c.pos = Mock(spec=interfaces.Position)
        c.reset_map()

        c.close()

        libtcod.map_delete.assert_called_once_with(ANY)
        libtcod.image_delete.assert_called_once_with(ANY)
        assert_false(c.light_enabled)


class TurnTakerTest(InterfaceTest):
    class C(interfaces.TurnTaker):
        def take_turn(self):
            pass

    def tearDown(self):
        interfaces.TurnTaker.clear_all()

    def test_lowest_initiative_should_go_first(self):
        o = []

        class C(interfaces.TurnTaker):
            def take_turn(self):
                o.append(self)

        c1   = C(1)    # 2
        c5   = C(5)    # 3
        cm10 = C(-10)  # 1

        assert_is(interfaces.TurnTaker.take_all_turns(), None)

        # checks static list is in right order
        assert_is(interfaces.TurnTaker.turn_takers[0](), cm10)
        assert_is(interfaces.TurnTaker.turn_takers[1](), c1)
        assert_is(interfaces.TurnTaker.turn_takers[2](), c5)

        # check turn taken in right order
        assert_equal(len(o),3)
        assert_is(o[0],cm10)
        assert_is(o[1],c1)
        assert_is(o[2],c5)

    def test_should_create_turn_takers_as_taking_turns_by_default(self):
        a = self.C(1)
        a.take_turn = Mock()

        assert_is(interfaces.TurnTaker.take_all_turns(), None)

        a.take_turn.assert_called_once_with()

        b = self.C(1,False)
        b.take_turn = Mock()

        assert_is(interfaces.TurnTaker.take_all_turns(), None)

        assert_equal(a.take_turn.call_count,2)
        assert_equal(b.take_turn.call_count,0)
        
    def test_take_turn_should_fail_on_base_class(self):
        a = interfaces.TurnTaker(1)
        assert_raises(NotImplementedError,interfaces.TurnTaker.take_all_turns)


    def test_all_turn_takers_should_take_a_turn_on_take_all_turns(self):
        do_not_delete = []
        for i in range(10):
            c = self.C(1)
            c.take_turn = Mock()
            do_not_delete.append( c )

        assert_is(interfaces.TurnTaker.take_all_turns(), None)

        assert_equal(len(interfaces.TurnTaker.turn_takers),10)
        for c in do_not_delete:
            c.take_turn.assert_called_once_with()

    def test_should_clear_all_turn_takers_on_call(self):
        do_not_delete = []
        for i in range(10):
            c = self.C(1)
            c.take_turn = Mock()
            do_not_delete.append( c )
        
        assert_is(interfaces.TurnTaker.take_all_turns(), None)
        assert_equal(len(interfaces.TurnTaker.turn_takers),10)
        for c in do_not_delete:
            c.take_turn.assert_called_once_with()
            c.take_turn.reset_mock()

        assert_is(interfaces.TurnTaker.clear_all(), None)

        assert_equal(len(interfaces.TurnTaker.turn_takers),0)
        for c in do_not_delete:
            assert_equal(c.take_turn.call_count,0)

    def test_should_not_take_turn_on_deleted_taker(self):
        a = self.C(1)
        a.take_turn = Mock()
        b = self.C(2)
        b.take_turn = Mock()

        assert_is(interfaces.TurnTaker.take_all_turns(), None)

        a.take_turn.assert_called_once_with()
        b.take_turn.assert_called_once_with()
        a.take_turn.reset_mock()
        b.take_turn.reset_mock()

        del b
        gc.collect()

        assert_is(interfaces.TurnTaker.take_all_turns(), None)
        assert_equal(len(interfaces.TurnTaker.turn_takers),1)
        assert_is(interfaces.TurnTaker.turn_takers[0](),a)
        a.take_turn.assert_called_once_with()

    def test_refresh_should_replace_turntaker_in_static_list(self):
        a = self.C(1)
        a.take_turn = Mock()

        assert_is(interfaces.TurnTaker.take_all_turns(), None)

        a.take_turn.assert_called_once_with()
        a.take_turn.reset_mock()

        assert_is(interfaces.TurnTaker.clear_all(), None)
        assert_equal(interfaces.TurnTaker.turn_takers,[])
        assert_is(interfaces.TurnTaker.take_all_turns(), None)
        assert_equal(a.take_turn.call_count,0)

        assert_is(a.refresh_turntaker(), None)
        assert_is(interfaces.TurnTaker.turn_takers[0](), a)
        assert_is(interfaces.TurnTaker.take_all_turns(), None)
        a.take_turn.assert_called_once_with()

    def test_add_turntaker_should_add_to_list(self):
        a = self.C(1,False)
        b = self.C(2)
        assert_equal(len(interfaces.TurnTaker.turn_takers),1)
        assert_is(interfaces.TurnTaker.turn_takers[0](),b)

        assert_is(interfaces.TurnTaker.add_turntaker(a), None)

        assert_equal(len(interfaces.TurnTaker.turn_takers),2)
        assert_is(interfaces.TurnTaker.turn_takers[0](),a)
        assert_is(interfaces.TurnTaker.turn_takers[1](),b)

    def test_clear_turntaker_should_remove_count_from_list(self):
        a = self.C(1)
        b = self.C(2)
        interfaces.TurnTaker.add_turntaker(b) # again

        assert_equal(len(interfaces.TurnTaker.turn_takers),3)
        assert_is(interfaces.TurnTaker.turn_takers[0](),a)
        assert_is(interfaces.TurnTaker.turn_takers[1](),b)
        assert_is(interfaces.TurnTaker.turn_takers[2](),b)

        assert_equal(interfaces.TurnTaker.clear_turntaker(a), None)
        assert_equal(len(interfaces.TurnTaker.turn_takers),2)
        assert_is(interfaces.TurnTaker.turn_takers[0](),b)
        assert_is(interfaces.TurnTaker.turn_takers[1](),b)

        assert_equal(interfaces.TurnTaker.clear_turntaker(b,2), None)
        assert_equal(len(interfaces.TurnTaker.turn_takers),0)

    def test_clear_turntaker_should_not_raise_error_if_arg_not_in_list(self):
        a = self.C(1)
        b = self.C(2,False)

        assert_equal(len(interfaces.TurnTaker.turn_takers),1)
        assert_is(interfaces.TurnTaker.turn_takers[0](),a)

        assert_equal(interfaces.TurnTaker.clear_turntaker(b), None)

        assert_equal(len(interfaces.TurnTaker.turn_takers),1)
        assert_is(interfaces.TurnTaker.turn_takers[0](),a)


class TraversableTest(InterfaceTest):
    def test_should_always_permit_leaving_by_default(self):
        t = interfaces.Traversable(0.0)
        assert_true(t.try_leaving(Mock()))

    def test_should_return_walk_cost_if_movement_permitted(self):
        for w in (
            0.1,
            1.0,
            0.6
            ):
            t = interfaces.Traversable(w)
            assert_equal(t.try_movement(Mock()),w)

    def test_should_raise_continue_error_if_movement_blocked(self):
        t = interfaces.Traversable(0.0)
        assert_raises(errors.InvalidMoveContinueError,t.try_movement,Mock())

    def test_should_block_movement_if_walk_cost_zero(self):
        t1 = interfaces.Traversable(0.0)
        t2 = interfaces.Traversable(0.5)

        assert_true(t1.blocks_movement())
        assert_false(t2.blocks_movement())

    def test_should_permit_movement_if_testing_pathing_and_may_block(self):
        t1 = interfaces.Traversable(0.0)
        t2 = interfaces.Traversable(0.0,True)

        assert_true(t1.blocks_movement())
        assert_true(t2.blocks_movement())
        assert_false(t1.blocks_movement(is_for_mapping=True))
        assert_true(t2.blocks_movement(is_for_mapping=True))


class TransparentTest(InterfaceTest):

    def test_should_block_light_if_transparency_zero(self):
        t1 = interfaces.Transparent(0.0)
        t2 = interfaces.Transparent(0.1)
        assert_true(t1.blocks_light())
        assert_false(t2.blocks_light())

    def test_should_derive_light_level_from_map_if_translucent(self):
        m = Mock(spec=maps.Map)
        m.light_level = Mock(return_value=5.0)
        p = Mock(spec=interfaces.Position)
        t = interfaces.Transparent(0.1)
        t.map = m
        t.pos = p

        assert_equal(t.light_level,5.0)
        m.light_level.assert_called_once_with(p)

    def test_should_derive_light_level_from_next_space_towards_player(self):
        m = Mock(spec=maps.Map)
        m.light_level = Mock(return_value=5.0)
        m.player = Mock(spec=player.Player)
        p = interfaces.Position(5,5)
        t = interfaces.Transparent(0.0)
        t.map = m
        t.pos = p

        for (p_player, p_expected) in (
            ((0,5),     (4,5)),
            ((5,0),     (5,4)),
            ((9,5),     (6,5)),
            ((5,9),     (5,6)),
            ((0,0),     (4,4)),
            ((9,9),     (6,6)),
            ((0,4),     (4,4)),
            ((9,0),     (6,4)),
            ):
            m.player.pos = interfaces.Position(p_player)
            assert_equal(t.light_level,5.0)
            m.light_level.assert_called_once_with(p_expected)
            m.light_level.reset_mock()

    def test_should_derive_light_level_from_players_space_if_adjacent(self):
        m = Mock(spec=maps.Map)
        m.light_level = Mock(return_value=5.0)
        m.player = Mock(spec=player.Player)
        p = interfaces.Position(5,5)
        t = interfaces.Transparent(0.0)
        t.map = m
        t.pos = p

        for (p_player, p_expected) in (
            ((4,5),     (4,5)),
            ((5,4),     (5,4)),
            ((6,5),     (6,5)),
            ((5,6),     (5,6)),
            ((4,4),     (4,4)),
            ((6,6),     (6,6)),
            ((6,4),     (6,4)),
            ((4,6),     (4,6)),
            ):
            m.player.pos = interfaces.Position(p_player)
            assert_equal(t.light_level,5.0)
            m.light_level.assert_called_once_with(p_expected)
            m.light_level.reset_mock()

    def test_should_derive_light_colour_from_map_if_translucent(self):
        m = Mock(spec=maps.Map)
        m.light_colour = Mock(return_value=libtcod.white)
        p = Mock(spec=interfaces.Position)
        t = interfaces.Transparent(0.1)
        t.map = m
        t.pos = p

        assert_equal(t.light_colour,libtcod.white)
        m.light_colour.assert_called_once_with(p)

    def test_should_derive_light_colour_from_next_space_towards_player(self):
        m = Mock(spec=maps.Map)
        m.light_colour = Mock(return_value=libtcod.white)
        m.player = Mock(spec=player.Player)
        p = interfaces.Position(5,5)
        t = interfaces.Transparent(0.0)
        t.map = m
        t.pos = p

        for (p_player, p_expected) in (
            ((0,5),     (4,5)),
            ((5,0),     (5,4)),
            ((9,5),     (6,5)),
            ((5,9),     (5,6)),
            ((0,0),     (4,4)),
            ((9,9),     (6,6)),
            ((0,4),     (4,4)),
            ((9,0),     (6,4)),
            ):
            m.player.pos = interfaces.Position(p_player)
            assert_equal(t.light_colour,libtcod.white)
            m.light_colour.assert_called_once_with(p_expected)
            m.light_colour.reset_mock()

    def test_should_derive_light_colour_from_players_space_if_adjacent(self):
        m = Mock(spec=maps.Map)
        m.light_colour = Mock(return_value=libtcod.white)
        m.player = Mock(spec=player.Player)
        p = interfaces.Position(5,5)
        t = interfaces.Transparent(0.0)
        t.map = m
        t.pos = p

        for (p_player, p_expected) in (
            ((4,5),     (4,5)),
            ((5,4),     (5,4)),
            ((6,5),     (6,5)),
            ((5,6),     (5,6)),
            ((4,4),     (4,4)),
            ((6,6),     (6,6)),
            ((6,4),     (6,4)),
            ((4,6),     (4,6)),
            ):
            m.player.pos = interfaces.Position(p_player)
            assert_equal(t.light_colour,libtcod.white)
            m.light_colour.assert_called_once_with(p_expected)
            m.light_colour.reset_mock()


class StatusEffectTest(InterfaceTest):
    def test_should_add_effects(self):
        s = interfaces.StatusEffect()
        assert_true(s.add_effect(interfaces.StatusEffect.NIGHT_VISION))

        assert_in(interfaces.StatusEffect.NIGHT_VISION,s.current_effects)
        assert_equal(len(s.current_effects),1)

    def test_should_not_add_same_effect_twice(self):
        s = interfaces.StatusEffect()
        assert_true(s.add_effect(interfaces.StatusEffect.NIGHT_VISION))

        assert_false(s.add_effect(interfaces.StatusEffect.NIGHT_VISION))
        assert_in(interfaces.StatusEffect.NIGHT_VISION,s.current_effects)
        assert_equal(len(s.current_effects),1)

    def test_should_remove_effect(self):
        s = interfaces.StatusEffect()
        assert_true(s.add_effect(interfaces.StatusEffect.NIGHT_VISION))
        assert_in(interfaces.StatusEffect.NIGHT_VISION,s.current_effects)
        assert_equal(len(s.current_effects),1)

        assert_true(s.remove_effect(interfaces.StatusEffect.NIGHT_VISION))
        assert_equal(len(s.current_effects),0)

    def test_should_return_false_if_removing_effect_not_present(self):
        s = interfaces.StatusEffect()
        assert_true(s.add_effect(interfaces.StatusEffect.NIGHT_VISION))
        assert_in(interfaces.StatusEffect.NIGHT_VISION,s.current_effects)
        assert_equal(len(s.current_effects),1)
        
        assert_false(s.remove_effect(interfaces.StatusEffect.BLIND))

        assert_in(interfaces.StatusEffect.NIGHT_VISION,s.current_effects)
        assert_equal(len(s.current_effects),1)

    def test_should_have_effect_if_effect_added(self):
        s = interfaces.StatusEffect()
        assert_true(s.add_effect(interfaces.StatusEffect.NIGHT_VISION))

        assert_in(interfaces.StatusEffect.NIGHT_VISION,s.current_effects)
        assert_equal(len(s.current_effects),1)

        assert_true(s.has_effect(interfaces.StatusEffect.NIGHT_VISION))
        assert_false(s.has_effect(interfaces.StatusEffect.BLIND))


class CountUpTest(InterfaceTest):

    def test_should_increment_and_return_false_if_not_hitting_cap(self):
        for (c,  count_to, inc_by) in (
            (0,  10,       1),
            (0,  2,        1),
            (5,  8,        2),
            (10, 21,       10),
            ):
            cu = interfaces.CountUp(count_to,c)
            assert_false(cu.inc(inc_by))
            assert_equal(cu.count,c+inc_by)

    def test_should_increment_to_limit_and_return_true_if_hits_cap(self):
        for (c,  count_to, inc_by) in (
            (0,  1,        1),
            (1,  1,        1),
            (0,  5,        10),
            (10, 11,       10),
            ):
            cu = interfaces.CountUp(count_to,c)
            assert_true(cu.inc(inc_by))
            assert_equal(cu.count,count_to)

    def test_should_decrement_and_return_false_if_not_zero(self):
        for (c,   count_to,  dec_by) in (
            (10,  10,        1),
            (2,    2,        1),
            (3,    8,        2),
            (11,  21,       10),
            ):
            cu = interfaces.CountUp(count_to,c)
            assert_false(cu.dec(dec_by))
            assert_equal(cu.count,c-dec_by)

    def test_should_decrement_and_return_true_if_zero(self):
        for (c,   count_to,  dec_by) in (
            (1,   10,        1),
            (0,    2,        1),
            (1,    8,        2),
            (6,   21,       10),
            ):
            cu = interfaces.CountUp(count_to,c)
            assert_true(cu.dec(dec_by))
            assert_equal(cu.count,0)

    def test_should_reset_to_given_value(self):
        for r in (
            0,
            5,
            11,
            -1,
            ):
            cu = interfaces.CountUp(10)
            assert_is(cu.reset(r),None)
            assert_equal(cu.count,r)

    def test_should_be_full_when_counted_up_to_max(self):
        for (c,  count_to, rval) in (
            (1,  1,        True),
            (0,  1,        False),
            (5,  10,       False),
            (10, 10,       True),
            ):
            cu = interfaces.CountUp(count_to,c)
            assert_equal(cu.full(),rval)
            
    def test_should_assert_error_if_init_out_of_bounds(self):
        for (c,   count_to) in (
            (2,   1),
            (-1, -2),
            (100, 9),
            ):
            assert_raises(AssertionError,interfaces.CountUp,count_to,c)


class HasInventoryTest(InterfaceTest):
    def test_should_init_fixed_slots_to_none(self):
        for s in (
            (),
            (1, 2),
            ('foo', 'bar', 'baz'),
            ):
            h = interfaces.HasInventory(0, s)
            assert_equal(h.slot_keys,s)
            for k in h.slot_keys:
                assert_is(h.slot_items[k], None)
            assert_equal(len(h.slot_items.keys()),len(s))

    def test_should_init_inv_slots_to_none(self):
        for s in (
            0,
            1,
            7):
            h = interfaces.HasInventory(s)
            assert_equal(len(h.items),s)
            for i in h.items:
                assert_is(i,None)


class ActivatableTest(InterfaceTest):
    def test_should_not_be_init_with_bad_owner(self):
        assert_raises( AssertionError,
                       interfaces.Activatable.__init__,
                       Mock(spec=interfaces.Activatable),
                       Mock() # i.e. not an Activator
                       )
        a = interfaces.Activatable()
        assert_is(a.owner, None)

    def test_should_not_activate_with_bad_owner(self):
        a = interfaces.Activatable()
        a.owner = Mock() # i.e. not an Activator
        assert_raises( AssertionError,
                       a.activate )

    def test_should_not_activate_with_bad_activator(self):
        a = interfaces.Activatable()
        a.owner = Mock(spec=interfaces.Activator)
        assert_raises( AssertionError,
                       a.activate,
                       Mock() # i.e. not an Activator
                       )

    def test_should_not_activate_with_no_activator_or_owner(self):
        a = interfaces.Activatable()
        assert_raises( AssertionError,
                       a.activate
                       )

    def test_should_activate_by_default(self):
        a = interfaces.Activatable()
        assert_is(a.activate(Mock(spec=interfaces.Activator)),True)

        a.owner = Mock(spec=interfaces.Activator)
        assert_is(a.activate(),True)
        
class AlertableTest(InterfaceTest):
    class A(interfaces.Alertable,interfaces.Mappable):
        def __init__(self,pos,listen_radius=10):
            interfaces.Mappable.__init__(self,pos,'x',libtcod.white)
            interfaces.Alertable.__init__(self,listen_radius)

    def test_should_alert_to_pos_at_pri_within_radius(self):
        for (r, my_pos, alert_pos, pri) in (
            (1, (1,1),  (1,1),     interfaces.Alertable.PRI_LOW),
            (1, (1,1),  (1,2),     interfaces.Alertable.PRI_HIGH),
            (2, (1,1),  (2,2),     interfaces.Alertable.PRI_HIGH),
            (3, (3,3),  (5,4),     interfaces.Alertable.PRI_MED),
            ):
            a = self.A(interfaces.Position(my_pos),r)
            assert_true(a.alert(interfaces.Position(alert_pos),priority=pri))
            assert_equal(a.investigate_list[pri], [alert_pos])
            assert_in(a,interfaces.Alertable.ALERTABLES)

    def test_should_not_alert_to_pos_outside_radius(self):
        for (r, my_pos, alert_pos, pri) in (
            (1, (1,1),  (1,3),     interfaces.Alertable.PRI_LOW),
            (1, (1,1),  (3,1),     interfaces.Alertable.PRI_HIGH),
            (2, (1,1),  (3,3),     interfaces.Alertable.PRI_HIGH),
            (3, (3,3),  (7,4),     interfaces.Alertable.PRI_MED),
            ):
            a = self.A(interfaces.Position(my_pos),r)
            assert_false(a.alert(interfaces.Position(alert_pos),priority=pri))
            assert_equal(a.investigate_list[pri], [])
            assert_in(a,interfaces.Alertable.ALERTABLES)

    def test_should_default_priority_to_medium(self):
        p = interfaces.Position(1,1)
        a = self.A(p,10)
        assert_true(a.alert(p))
        assert_equal(a.investigate_list[interfaces.Alertable.PRI_MED], [p])
        assert_in(a,interfaces.Alertable.ALERTABLES)

    def test_should_not_clear_other_alerts_if_their_pri_is_high(self):
        p = interfaces.Position(1,1)
        a = self.A(p, 1)
        b = self.A(p, 1)
        assert_in(a,interfaces.Alertable.ALERTABLES)
        assert_in(b,interfaces.Alertable.ALERTABLES)

        assert_true(a.alert(p,interfaces.Alertable.PRI_MED))
        assert_true(b.alert(p,interfaces.Alertable.PRI_HIGH))

        assert_true(a.clear_alert(p))
        assert_equal(b.investigate_next(),p)

    def test_should_not_clear_other_alerts_if_my_pri_is_high(self):
        p = interfaces.Position(1,1)
        a = self.A(p, 1)
        b = self.A(p, 1)
        assert_in(a,interfaces.Alertable.ALERTABLES)
        assert_in(b,interfaces.Alertable.ALERTABLES)

        assert_true(a.alert(p,interfaces.Alertable.PRI_HIGH))
        assert_true(b.alert(p,interfaces.Alertable.PRI_MED))

        assert_true(a.clear_alert(p))
        assert_equal(b.investigate_next(),p)

    def test_should_clear_other_alerts_if_their_pri_is_not_high(self):
        p = interfaces.Position(1,1)
        a = self.A(p, 1)
        b = self.A(p, 1)
        assert_in(a,interfaces.Alertable.ALERTABLES)
        assert_in(b,interfaces.Alertable.ALERTABLES)

        assert_true(a.alert(p,interfaces.Alertable.PRI_LOW))
        assert_true(b.alert(p,interfaces.Alertable.PRI_MED))

        assert_true(a.clear_alert(p))
        assert_is(b.investigate_next(),None)

    def test_should_return_false_if_no_alerts_cleared(self):
        p = interfaces.Position(1,1)
        a = self.A(p, 1)
        assert_in(a,interfaces.Alertable.ALERTABLES)
        assert_false(a.clear_alert(p))

    def test_should_give_high_priority_pos_to_investigate_next(self):
        p1 = interfaces.Position(1,2)
        p2 = interfaces.Position(2,1)
        a = self.A(interfaces.Position(1,1), 2)
        assert_in(a,interfaces.Alertable.ALERTABLES)

        assert_true(a.alert(p1,interfaces.Alertable.PRI_HIGH))
        assert_true(a.alert(p2,interfaces.Alertable.PRI_LOW))

        assert_equal(a.investigate_next(),p1)
        assert_equal(a.investigate_next(),p2)
        assert_equal(a.investigate_next(),None)

    def test_should_give_med_pri_pos_to_investigate_if_no_high(self):
        p1 = interfaces.Position(1,2)
        p2 = interfaces.Position(2,1)
        a = self.A(interfaces.Position(1,1), 2)
        assert_in(a,interfaces.Alertable.ALERTABLES)

        assert_true(a.alert(p1,interfaces.Alertable.PRI_MED))
        assert_true(a.alert(p2,interfaces.Alertable.PRI_LOW))

        assert_equal(a.investigate_next(),p1)
        assert_equal(a.investigate_next(),p2)
        assert_equal(a.investigate_next(),None)

    def test_should_give_low_pri_pos_to_investigate_if_no_med_or_high(self):
        p1 = interfaces.Position(1,2)
        a = self.A(interfaces.Position(1,1), 2)
        assert_in(a,interfaces.Alertable.ALERTABLES)

        assert_true(a.alert(p1,interfaces.Alertable.PRI_LOW))

        assert_equal(a.investigate_next(),p1)
        assert_equal(a.investigate_next(),None)


