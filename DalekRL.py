#!/usr/bin/env python3

# system imports
import os
import sys

# libtcod
import libtcodpy as libtcod

# our imports
from interfaces import Position, UI
from maps import DalekMap
from errors import InvalidMoveError

SCREEN_SIZE = Position(80,50)
LIMIT_FPS = 30
RANDOM_SEED = 1999

# for now
if len(sys.argv)>1 and len(sys.argv[1])>0:
    RANDOM_SEED=int(sys.argv[1])

# init window
font = os.path.join(b'resources', b'consolas10x10_gs_tc.png')
libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_SIZE.x, SCREEN_SIZE.y, b'DalekRL')
libtcod.sys_set_fps(LIMIT_FPS)

# generate default map
map = DalekMap(RANDOM_SEED,SCREEN_SIZE-(0,4))
map.generate()
assert not map.player is None
player = map.player

# handle input
def do_nothing():
    pass
KEYMAP = {
    'k': player.move_n,
    'j': player.move_s, 
    'h': player.move_w, 
    'l': player.move_e,
    'y': player.move_nw,
    'u': player.move_ne,
    'b': player.move_sw,
    'n': player.move_se,
    '.': do_nothing,
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
    player.draw_ui(Position(0,SCREEN_SIZE.y-3))
    UI.draw_all()
    libtcod.console_flush()
    
    # clear screen
    #map.cls()
    libtcod.console_clear(0)
    
    try:
        # handle player input
        handle_keys()
    except InvalidMoveError:
        print("You can't move like that")
        continue

    # items
    for i in map.items + player.items:
        if not i is None:
            i.take_turn()

    # monster movement
    for m in map.monsters:
        m.take_turn()

