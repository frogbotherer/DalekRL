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
import monsters
import tiles
import errors
import ui

class MapsTest(DalekTest):
    pass

class MapTest(MapsTest):
    def setUp(self):
        self.player = Mock(spec_set=player.Player)
        self.map    = maps.Map(None,interfaces.Position(3,3),self.player)

    def test_should_add_obj_to_correct_layer_if_not_given(self):
        p = interfaces.Position(1,1)
        for (o, layer) in (
            (tiles.Wall(p), tiles.Tile),
            (tiles.EvidencePanel(p), tiles.Tile),
            (monsters.Dalek(p), monsters.Monster),
            (monsters.StaticCamera(p), monsters.Monster),
            (items.HandTeleport(p,1.0), items.Item),
            (items.RemoteControl(p,1.0), items.Item),
            ):
            assert_is(self.map.add(o),None)

            assert_is(self.map.find_at_pos(p,layer),o)
            assert_is(o.map,self.map)

            assert_is(self.map.remove(o),None)
            assert_is(self.map.find_at_pos(p,layer),None)

    def test_should_add_obj_to_given_layer(self):
        p = interfaces.Position(1,1)
        for (o, layer) in (
            (tiles.Wall(p), tiles.Tile),
            (tiles.EvidencePanel(p), tiles.Tile),
            (monsters.Dalek(p), monsters.Monster),
            (monsters.StaticCamera(p), monsters.Monster),
            (items.HandTeleport(p,1.0), items.Item),
            (items.RemoteControl(p,1.0), items.Item),
            ):

            assert_is(self.map.add(o,layer),None)

            assert_is(o.map,self.map)
            assert_is(self.map.find_at_pos(p,layer),o)

            assert_is(self.map.remove(o,layer),None)
            assert_is(self.map.find_at_pos(p,layer),None)

    def test_should_not_add_if_not_mappable(self):
        p = interfaces.Position(1,1)
        assert_raises(AssertionError, self.map.add, self, p)

    def test_should_remove_obj_from_given_layer(self):
        # almost exactly the same
        p = interfaces.Position(1,1)
        for (o, layer) in (
            (tiles.Wall(p), tiles.Tile),
            (tiles.EvidencePanel(p), tiles.Tile),
            (monsters.Dalek(p), monsters.Monster),
            (monsters.StaticCamera(p), monsters.Monster),
            (items.HandTeleport(p,1.0), items.Item),
            (items.RemoteControl(p,1.0), items.Item),
            ):

            assert_is(self.map.add(o,layer),None)
            assert_is(o.map,self.map)
            assert_is(self.map.find_at_pos(p,layer),o)

            assert_is(self.map.remove(o,layer),None)

            assert_is(o.pos,None)
            assert_is(self.map.find_at_pos(p,layer),None)

    def test_should_remove_obj_from_correct_layer_if_not_given(self):
        # repeat of test above
        p = interfaces.Position(1,1)
        for (o, layer) in (
            (tiles.Wall(p), tiles.Tile),
            (tiles.EvidencePanel(p), tiles.Tile),
            (monsters.Dalek(p), monsters.Monster),
            (monsters.StaticCamera(p), monsters.Monster),
            (items.HandTeleport(p,1.0), items.Item),
            (items.RemoteControl(p,1.0), items.Item),
            ):

            assert_is(self.map.add(o,layer),None)
            assert_is(o.map,self.map)
            assert_is(self.map.find_at_pos(p,layer),o)

            assert_is(self.map.remove(o),None)

            assert_is(o.pos,None)
            assert_is(self.map.find_at_pos(p,layer),None)

    def test_should_prevent_removal_of_obj_not_on_map(self):
        p = interfaces.Position(1,1)
        o = tiles.Wall(p)
        assert_raises(AssertionError, self.map.remove, o)

    def test_should_prevent_movement_when_not_added_to_map(self):
        p = interfaces.Position(1,1)
        o = tiles.Wall(p)

        assert_raises(AssertionError, self.map.move, o, p+(1,1))

    def test_should_prevent_movement_outside_of_map_bounds(self):
        p = interfaces.Position(1,1)
        o = tiles.Wall(p)
        assert_is(self.map.add(o),None)

        for (x,y) in (
            (-1,0),
            (9,9),
            (-1,9),
            ):
            m = interfaces.Position(x,y)
            assert_raises(errors.InvalidMoveError,self.map.move,o,m)

    def test_should_use_layer_parameter_if_given(self):
        p = interfaces.Position(1,1)
        p1 = p + (1,1)
        for (o, layer) in (
            (tiles.Wall(p), tiles.Tile),
            (tiles.EvidencePanel(p), tiles.Tile),
            (monsters.Dalek(p), monsters.Monster),
            (monsters.StaticCamera(p), monsters.Monster),
            (items.HandTeleport(p,1.0), items.Item),
            (items.RemoteControl(p,1.0), items.Item),
            ):
            assert_is(self.map.add(o,layer),None)

            assert_equal(self.map.move(o,p1,layer),0.0)

            assert_is(o.map,self.map)
            assert_is(self.map.find_at_pos(p,layer),None)
            assert_is(self.map.find_at_pos(p1,layer),o)
            assert_equal(o.pos,p1)

            assert_is(self.map.remove(o,layer),None)
            assert_is(self.map.find_at_pos(p,layer),None)        

    def test_should_call_try_leaving_on_traversables_at_current_pos(self):
        p = interfaces.Position(1,1)
        p1 = p + (1,0)
        ts = [
            Mock(spec = tiles.Floor),
            Mock(spec = tiles.Floor),
            ]
        o = monsters.Dalek(p)
        for t in ts:
            t.pos = p
            t.try_leaving = Mock(return_value=True)
            self.map.add(t)
        self.map.add(o)

        t1 = Mock(spec=tiles.Floor)
        t1.pos = p1
        t1.try_movement = Mock(return_value=1.0)
        self.map.add(t1)

        assert_equal(self.map.move(o,p1),1.0)

        for t in ts:
            t.try_leaving.assert_called_once_with(o)
        assert_equal(t1.try_leaving.call_count,0)

    def test_should_call_try_movement_on_all_traversables_at_destination_pos(self):
        p = interfaces.Position(1,1)
        p1 = p + (1,0)
        ts = [
            Mock(spec = tiles.Floor),
            Mock(spec = tiles.Floor),
            ]
        o = monsters.Dalek(p)
        for t in ts:
            t.pos = p1
            t.try_movement = Mock(return_value=1.0)
            self.map.add(t)
        self.map.add(o)

        t1 = Mock(spec=tiles.Floor)
        t1.pos = p
        t1.try_leaving = Mock(return_value=True)
        self.map.add(t1)

        assert_equal(self.map.move(o,p1),2.0)

        for t in ts:
            t.try_movement.assert_called_once_with(o)
        assert_equal(t1.try_movement.call_count,0)

    @nottest
    def test_should_fail_if_obj_pos_data_out_of_sync_with_map(self):
        pass

    @nottest
    def test_should_update_pos_and_last_pos_data_in_sync_with_map(self):
        pass

    @nottest
    def test_should_return_zero_if_no_move(self):
        pass

    @nottest
    def test_should_return_high_value_if_large_movement_cost(self):
        pass

    @nottest
    def test_should_find_all_items_of_given_type(self):
        pass

    @nottest
    def test_should_find_all_items_of_type_based_on_layer(self):
        pass

    @nottest
    def test_should_return_empty_list_if_nothing_found(self):
        pass

    @nottest
    def test_should_find_nearest_of_type_to_obj(self):
        pass

    @nottest
    def test_should_not_count_self_as_nearest(self):
        pass

    @nottest
    def test_should_only_use_given_layer_for_search(self):
        pass

    @nottest
    def test_should_only_find_visible_obj_if_requested(self):
        pass

    @nottest
    def test_should_find_all_type_within_r_of_obj(self):
        pass

    @nottest
    def test_should_only_find_visible_obj_within_r_if_requested(self):
        pass

    @nottest
    def test_should_return_empty_list_if_no_obj_in_radius(self):
        pass

    @nottest
    def test_should_exclude_if_r_equal_to_distance(self):
        pass

    @nottest
    def test_should_find_random_clear(self):
        pass

    @nottest
    def test_should_raise_error_if_no_clear_spaces_available(self):
        pass

    @nottest
    def test_should_use_given_rng_to_find_clear(self):
        pass

    @nottest
    def test_should_count_player_pos_as_occupied(self):
        pass

    @nottest
    def test_should_count_monster_pos_as_occupied(self):
        pass

    @nottest
    def test_should_count_tiles_as_occupied_if_they_block_movement(self):
        pass

    @nottest
    def test_should_find_first_item_in_list_of_items_at_pos_given_layer(self):
        pass

    @nottest
    def test_should_find_first_item_in_first_layer(self):
        pass

    @nottest
    def test_should_return_none_if_nothing_at_pos(self):
        pass

    @nottest
    def test_should_find_all_at_pos_given_layers(self):
        pass

    @nottest
    def test_should_return_empty_list_if_nothing_at_pos(self):
        pass

    @nottest
    def test_should_get_walk_cost_from_sum_of_traversables_at_pos_if_present(self):
        pass

    @nottest
    def test_should_get_walk_cost_as_zero_if_no_traversables(self):
        pass

    @nottest
    def test_should_check_all_traversables_at_pos_to_determine_whether_blocks_or_not(self):
        pass

    @nottest
    def test_should_define_pos_as_blocked_if_no_traversables_there(self):
        pass

    @nottest
    def test_should_draw_all_mappables_when_draw_called(self):
        pass

    @nottest
    def test_should_recalculate_moving_lights_only_if_no_dirty_pos_set(self):
        pass

    @nottest
    def test_should_recalculate_paths_and_lighting_if_dirty_pos_set(self):
        pass

    @nottest
    def test_should_recalculate_all_paths_if_no_pos_given(self):
        pass

    @nottest
    def test_should_recalculate_only_paths_that_cross_given_pos_list(self):
        pass

    @nottest
    def test_should_defer_calculation_unless_force_now_set(self):
        pass

    @nottest
    def test_should_treat_occasionally_blocking_as_always_blocking_when_testing_paths_for_mapping(self):
        pass

    @nottest
    def test_should_cache_fov_data_against_mappables(self):
        pass

    @nottest
    def test_should_prepare_fov_for_player_using_pos_and_radius(self):
        pass

    @nottest
    def test_should_accumulate_fov_calculations_if_requested(self):
        pass

    @nottest
    def test_should_recalculate_all_lighting(self):
        pass

    @nottest
    def test_should_recalculate_only_moving_lighting(self):
        pass

    @nottest
    def test_should_only_recalculate_lighting_that_passes_through_list_of_pos(self):
        pass

    @nottest
    def test_should_indicate_whether_obj_is_visibly_lit(self):
        pass

    @nottest
    def test_should_treat_hidden_in_shadow_obj_as_not_visible_in_brighter_conditions(self):
        pass

    @nottest
    def test_should_provide_light_colour_including_intensity(self):
        pass

    #TODO: tests for debug_lighting

    @nottest
    def test_blind_obj_should_not_be_able_to_see_anything(self):
        pass

    @nottest
    def test_should_raise_error_if_checking_sight_of_non_mappable(self):
        pass

    @nottest
    def test_should_only_see_visible_obj(self):
        pass

    @nottest
    def test_should_see_nothing_if_angle_of_vis_is_zero(self):
        pass

    @nottest
    def test_should_only_see_if_target_in_light(self):
        pass

    @nottest
    def test_should_only_see_if_target_in_angle_of_vis(self):
        pass

    @nottest
    def test_should_only_see_if_los_to_target(self):
        pass

    @nottest
    def test_should_use_simple_los_check_for_drawing(self):
        pass

    @nottest
    def test_should_show_all_in_radius_when_using_xray_fov(self):
        pass

    @nottest
    def test_should_use_dijkstra_path_from_pos_to_pos(self):
        pass

    @nottest
    def test_should_only_return_first_n_steps_for_pathing(self):
        pass

    @nottest
    def test_should_destroy_all_tcod_resources_on_close(self):
        pass

    @nottest
    def test_should_destroy_all_tcod_resources_on_del(self):
        pass

    @nottest
    def test_should_get_all_monsters(self):
        pass

    @nottest
    def test_should_get_all_items(self):
        pass

    # don't test abstract generate method

    # TODO: map generation functions
