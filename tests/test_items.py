#!/usr/bin/env python3

# test imports
from unit_environment import DalekTest
from nose.tools import *
from mock import Mock, MagicMock, patch

# lang imports
from functools import reduce

# item under test
import libtcodpy as libtcod
import items
import interfaces
import player

class ItemTest(DalekTest):

    def _test_should_be_returned_in_item_generation(self):
        libtcod.random_get_float = Mock(return_value=0.0)

        # builds internal list of accessible items
        items.Item.random(None, None)
        assert_in(items.LabCoat, reduce( lambda a,b: a+b, list(items.Item.AWESOME_MAP.values()), []))

        libtcod.random_get_float = Mock(return_value=self.item_class.awesome_acc_weight-0.01)
        print(items.Item.AWESOME_MAP)
        print(self.item_class.awesome_acc_weight-0.01)
        assert_is_instance(items.Item.random(None,None,ranks=self.item_class.awesome_rank), self.item_class)


    def _test_should_be_taken_by_actor(self):
        p   = Mock()
        pos = Mock(spec=interfaces.Position)
        i = self.item_class(pos,1.0)
        i.take_by(p)

        # what happens when you pick sth up
        assert_is(i.owner, p)
        assert_is(i.pos, None)
        assert_false(i.is_visible)

        # display in UI
        if hasattr(i,'bar'):
            assert_true(i.bar.is_visible)

    def _test_should_by_dropped_by_actor(self):
        p   = Mock()
        pos = Mock(spec=interfaces.Position)
        i = self.item_class(p,1.0)
        i.drop_at(pos)

        # what happens when you drop sth
        assert_is(i.owner, None)
        assert_is(i.pos, pos)
        assert_true(i.is_visible)

        # UI
        if hasattr(i,'bar'):
            assert_false(i.bar.is_visible)

    def _test_should_not_be_activatable(self):
        i = self.item_class(Mock(interfaces.Activator))
        assert_false(i.activate())
        assert_false(i.can_be_remote_controlled)

    def _test_should_be_activatable(self):
        p = MagicMock()
        i = self.item_class(p)
        assert_true(i.activate())


class LabCoatTest(ItemTest):

    def setUp(self):
        self.item_class = items.LabCoat

    def test_should_be_taken_by_actor(self):
        self._test_should_be_taken_by_actor()

    def test_should_by_dropped_by_actor(self):
        self._test_should_by_dropped_by_actor()

    def test_should_be_returned_in_item_generation(self):
        self._test_should_be_returned_in_item_generation()

    def test_should_not_be_activatable(self):
        self._test_should_not_be_activatable()


class NinjaSuit(ItemTest):

    def setUp(self):
        self.item_class = items.NinjaSuit

    def test_should_be_taken_by_actor(self):
        self._test_should_be_taken_by_actor()

    def test_should_by_dropped_by_actor(self):
        self._test_should_by_dropped_by_actor()

    def test_should_be_returned_in_item_generation(self):
        self._test_should_be_returned_in_item_generation()

    def test_should_not_be_activatable(self):
        self._test_should_not_be_activatable()

    def test_should_add_hidden_effect_when_taken(self):
        i = self.item_class(None)
        p = Mock(spec=interfaces.StatusEffect)
        p.add_effect = Mock(return_value=True)
        i.take_by(p)
        p.add_effect.assert_called_once_with(interfaces.StatusEffect.HIDDEN_IN_SHADOW)

    def test_should_remove_hidden_effect_when_dropped(self):
        p = Mock(spec=player.Player) # i.e. mappable; activator; statuseffect
        i = self.item_class(p)
        p.remove_effect = Mock(return_value=True)
        i.drop_at(Mock(spec=interfaces.Position))
        p.remove_effect.assert_called_once_with(interfaces.StatusEffect.HIDDEN_IN_SHADOW)

    def test_should_provide_effect_when_init_with_owner(self):
        p = Mock(spec=player.Player) # i.e. mappable; activator; statuseffect
        p.remove_effect = Mock(return_value=True)

        i = self.item_class(p)
        p.add_effect.assert_called_once_with(interfaces.StatusEffect.HIDDEN_IN_SHADOW)
