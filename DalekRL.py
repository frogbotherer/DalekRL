#!/usr/bin/env python3

# system imports
import os
import sys

# libtcod
import libtcodpy as libtcod

# our imports
from interfaces import Position
from monsters import *
from maps import DalekMap

SCREEN_SIZE = Position(80,50)
LIMIT_FPS = 30
RANDOM_SEED = 1999

# init window
font = os.path.join(b'resources', b'consolas10x10_gs_tc.png')
libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_SIZE.x, SCREEN_SIZE.y, b'DalekRL')
libtcod.sys_set_fps(LIMIT_FPS)

# generate default map
map = DalekMap(RANDOM_SEED,SCREEN_SIZE)
map.generate()
assert not map.player is None
player = map.player

# handle input
KEYMAP = {
    'k': player.move_n,
    'j': player.move_s, 
    'h': player.move_w, 
    'l': player.move_e,
    'y': player.move_nw,
    'u': player.move_ne,
    'b': player.move_sw,
    'n': player.move_se,
    '1': player.use_item1,
    'q': sys.exit,
}

def handle_keys():
    key = None
    while not ( key and key.pressed and chr(key.c) in KEYMAP ):
        key = libtcod.console_wait_for_keypress(True)
    KEYMAP.get(chr(key.c))()

# main loop
while not libtcod.console_is_window_closed():

    # draw and flush screen
    map.draw()
    libtcod.console_flush()
    
    # clear screen
    map.cls()
    
    # handle player input
    handle_keys()

    # monster movement
    for m in map.monsters:
        m.take_turn()
