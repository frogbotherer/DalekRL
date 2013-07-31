#!/usr/bin/env python3

# testing imports
import behave
from mock import patch, MagicMock
from nose.tools import *

# game imports
import items
from errors import TodoError

# lang imports
import re # for sub

# helpers
def strip_prepositions(text):
    return re.sub('(?:^the )|(?:^an? )','',text)

def clean_actor_and_object(context,actor,thing):
    """returns instance of actor and class of thing"""
    actor = strip_prepositions(actor)
    thing = strip_prepositions(thing)

    if actor.lower() == 'player':
        a = context.map.player
    else:
        raise TodoError

    if thing == 'nothing':
        i_class = None
    else:
        i_class = items.Item.get_item_by_name(thing)

    return (a, i_class)


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
            a.slot_items[k] = None
            context.item_slots_to_test.append(k)
            
    elif not i_class in [c.__class__ for c in list(a.slot_items.values())]:
        i = i_class(a)
        a.slot_items[i.valid_slot] = None # clear out slot first to stop is_wearing from dropping defaults
        a.pickup(i)
        context.item_slots_to_test.append(i.valid_slot)


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

