#!/usr/bin/env python3

import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'DalekRL', False)

libtcod.sys_set_fps(LIMIT_FPS)

while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0,  libtcod.white)
    libtcod.console_put_char(0, 1, 1, '@',libtcod.BKGND_NONE)
    libtcod.console_flush()
