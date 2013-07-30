#!/usr/bin/env python3

# testing imports
from behave import *
from mock import patch, Mock

# game imports
import maps
import player
import interfaces

@given('the default test map')
def step_impl(context):
    p = player.Player()
    p.redraw_screen = Mock()
    context.map = maps.EmptyMap(0, interfaces.Position(80,46), p)
    context.map.generate()
