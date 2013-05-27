#!/usr/bin/env python3
# system imports
import os

# libtcod
import libtcodpy as libtcod

# our imports
from interfaces import *

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30

# init window
font = os.path.join(b'resources', b'consolas10x10_gs_tc.png')
libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, b'DalekRL')
libtcod.sys_set_fps(LIMIT_FPS)

# stuff
class Player (Drawable):
    pass

player = Player(Position(10,10),'@',libtcod.white)

# handle input
KEYMAP = {
    'j': player.move_up,
    'k': player.move_down, 
    'h': player.move_left, 
    'l': player.move_right, 
}
def handle_keys():
    key = libtcod.console_wait_for_keypress(True)
    if key.pressed and chr(key.c) in KEYMAP:
            KEYMAP.get(chr(key.c))()

# main loop
while not libtcod.console_is_window_closed():
    player.draw()
    libtcod.console_flush()
    
    player.clear()
    handle_keys()
