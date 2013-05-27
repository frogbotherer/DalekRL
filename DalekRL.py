#!/usr/bin/env python3
# system imports
import os

# libtcod
import libtcodpy as libtcod

# our imports
from interfaces import Position
from monsters import *
from maps import Map

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30
RANDOM_SEED = 1999

# init window
font = os.path.join(b'resources', b'consolas10x10_gs_tc.png')
libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, b'DalekRL')
libtcod.sys_set_fps(LIMIT_FPS)

# init random
RNG = libtcod.random_new_from_seed(RANDOM_SEED)

# stuff
map = Map()

player = Player(Position(10,10),'@',libtcod.white)
map.add(player)

mpos = []
while len(mpos)<10:
    p = Position(libtcod.random_get_int(RNG,1,SCREEN_WIDTH),libtcod.random_get_int(RNG,1,SCREEN_HEIGHT))
    if not p in mpos:
        mpos.append(p)
        map.add(Dalek(p))


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
}
def handle_keys():
    key = libtcod.console_wait_for_keypress(True)
    if key.pressed and chr(key.c) in KEYMAP:
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
