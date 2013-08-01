#!/usr/bin/env python3

# testing imports
import behave
from mock import patch, MagicMock
from nose.tools import *

# game imports
import items
import tiles
import interfaces
import monsters
from errors import TodoError

# lang imports
import re # for sub

# helpers
def strip_prepositions(text):
    return re.sub('(?:^the )|(?:^an? )','',text)

def clean_actor_and_object(context,actor,thing):
    """returns instance of actor and class of thing"""
    thing = strip_prepositions(thing)

    if thing == 'nothing':
        i_class = None
    else:
        i_class = items.Item.get_item_by_name(thing)

    return (clean_actor(context,actor), i_class)

def clean_actor(context,actor):
    actor = strip_prepositions(actor)
    if actor.lower() == 'player':
        return context.map.player
    else:
        raise TodoError

def clean_enemy(context,enemy):
    enemy = strip_prepositions(enemy)
    if enemy == 'nothing':
        return None
    else:
        return monsters.Monster.get_monster_by_name(enemy)

def clean_status_effect(effect):
    effect = effect.upper().replace(' ','_')
    if hasattr(interfaces.StatusEffect,effect):
        return getattr(interfaces.StatusEffect,effect)
    else:
        raise AttributeError


@given('{thing} on the ground where the {actor} is standing')
def step_impl(context,thing,actor):
    a, i_class = clean_actor_and_object(context,actor,thing)

    context.map.add(i_class(a.pos))


@given('{actor} is wearing {thing}')
@patch('player.Menu')
def step_impl(context,MockMenu,actor,thing):
    MockMenu().get_key = MagicMock(return_value='1')

    a, i_class = clean_actor_and_object(context,actor,thing)
    context.item_slots_to_test = []

    if thing == 'nothing':
        # should be a.drop_all() or something
        for k in a.slot_items.keys():
            i = a.slot_items[k]
            i.drop_at(None)
            a.slot_items[k] = None
            del i
            context.item_slots_to_test.append(k)
            
    elif not i_class in [c.__class__ for c in list(a.slot_items.values())]:
        i = i_class(a)
        a.slot_items[i.valid_slot] = None # clear out slot first to stop is_wearing from dropping defaults
        a.pickup(i)
        context.item_slots_to_test.append(i.valid_slot)

@given('{brightness} light level')
def step_impl(context,brightness):
    brightness = strip_prepositions(brightness)
    b = {'very dim': 0.1,
         'dim':      0.3,
         'low':      0.5,
         'medium':   0.7,
         'bright':   1.0,
         'very bright': 1.2}.get(brightness,1.0)

    context.map.add(tiles.FlatLight(interfaces.Position(1,1),context.map.size-interfaces.Position(1,1),b))
    context.map.recalculate_lighting()


@given('{enemy} enemy near {actor}')
def step_impl(context,enemy,actor):
    a = clean_actor(context,actor)
    e_class = clean_enemy(context,enemy)

    e = e_class(a.pos+interfaces.Position(2,2))
    context.map.add(e)


@when('{thing} is picked up by {actor}')
@patch('player.Menu')
def step_impl(context,MockMenu,thing,actor):
    a, i_class = clean_actor_and_object(context,actor,thing)

    MockMenu().get_key = MagicMock(return_value='1')

    if thing != 'nothing':
        a.interact()


@when('{thing} is dropped by {actor}')
@patch('player.Menu')
def step_impl(context,MockMenu,thing,actor):
    a, i_class = clean_actor_and_object(context,actor,thing)

    def mm_add(k,v):
        if v == str(i_class(None)):
            MockMenu().get_key = MagicMock(return_value=k)
    MockMenu().add     = mm_add

    if thing != 'nothing':
        a.drop()


@when('turns are taken')
def step_impl(context):
    interfaces.TurnTaker.take_all_turns()


@then('{actor} is wearing {thing}')
def step_impl(context,actor,thing):
    a, i_class = clean_actor_and_object(context,actor,thing)

    
    if thing == 'nothing':
        for k in context.item_slots_to_test:
            # assert all appropriate slots empty
            assert_is(a.slot_items[k],None)

    else:
        got = [c for c in list(a.slot_items.values()) if isinstance(c,i_class)]
        assert_equal( len(got), 1 )

        # check that the item we've got is in the correct slot
        if isinstance(got[0], items.SlotItem):
            assert_is( a.slot_items[got[0].valid_slot], got[0] )


@then('{thing} is on the ground where {actor} is standing')
def step_impl(context,thing,actor):
    a, i_class = clean_actor_and_object(context,actor,thing)

    i = context.map.find_all_at_pos(a.pos,items.Item)
    if thing == 'nothing':
        assert_equal(i,[])

    else:
        assert_equal(len(i),1)
        assert_is_instance(i[0],i_class)


@then('{actor} has the {effect} effect')
def step_impl(context,actor,effect):
    a = clean_actor(context,actor)
    e = clean_status_effect(effect)

    assert_is_instance(a,interfaces.StatusEffect)
    assert_true(a.has_effect(e))


@then('{actor} does not have the {effect} effect')
def step_impl(context,actor,effect):
    a = clean_actor(context,actor)
    e = clean_status_effect(effect)

    assert_is_instance(a,interfaces.StatusEffect)
    assert_false(a.has_effect(e))


@then('{enemy} is alerted to {actor}')
def step_impl(context,enemy,actor):
    a = clean_actor(context,actor)
    e_class = clean_enemy(context,enemy)

    # sanity to be sure we've got the right thing
    e = context.map.find_all(e_class,monsters.Monster)
    assert_equal(len(e),1)
    e = e[0]
    assert_is_instance(e,monsters.AI)
    assert_is_instance(e,e_class)

    # is monster in an alerted state?
    assert isinstance(e.state,monsters.MS_SeekingPlayer) or isinstance(e.state,monsters.MS_InvestigateSpot), "%s is in %s state"%(e,e.state)


@then('{enemy} is not alerted to {actor}')
def step_impl(context,enemy,actor):
    a = clean_actor(context,actor)
    e_class = clean_enemy(context,enemy)

    # sanity to be sure we've got the right thing
    e = context.map.find_all(e_class,monsters.Monster)
    assert_equal(len(e),1)
    e = e[0]
    assert_is_instance(e,monsters.AI)
    assert_is_instance(e,e_class)

    # is monster in an alerted state?
    assert not isinstance(e.state,monsters.MS_SeekingPlayer) and not isinstance(e.state,monsters.MS_InvestigateSpot), "%s is in %s state"%(e,e.state)

