#!/usr/bin/env python3

# system imports
import os
import sys

# libtcod
import libtcodpy as libtcod

# our imports
from interfaces import Position, TurnTaker
from ui import UI
from maps import Map
from player import Player
from errors import GameOverError, LevelWinError

SCREEN_SIZE = Position(80,50)
LIMIT_FPS = 10
RANDOM_SEED = 1999
MAP = None
PLAYER = None

# for now
if len(sys.argv)>1 and len(sys.argv[1])>0:
    RANDOM_SEED=int(sys.argv[1])-1

# init window
font = os.path.join(b'resources', b'consolas10x10_gs_tc.png')
libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_SIZE.x, SCREEN_SIZE.y, b'DalekRL')
libtcod.sys_set_fps(LIMIT_FPS)

# set default text palette # TODO: merge with UI class statics
libtcod.console_set_color_control(libtcod.COLCTRL_1,libtcod.red,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_2,libtcod.dark_yellow,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_3,libtcod.light_green,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_4,libtcod.light_blue,libtcod.black)
libtcod.console_set_color_control(libtcod.COLCTRL_5,libtcod.purple,libtcod.black)


def reset(keep_player=False):
    global SCREEN_SIZE, RANDOM_SEED, MAP, PLAYER

    RANDOM_SEED += 1
    UI.clear_all()
    TurnTaker.clear_all()

    if keep_player:
        PLAYER.refresh_turntaker()
        PLAYER.levels_seen += 1

    else:

        if not PLAYER is None:
            print("Game Over")
            print("%d evidence in %d turns; %d levels seen" %(len(PLAYER.evidence),PLAYER.turns,PLAYER.levels_seen))

        PLAYER = Player()

    if not MAP is None:
        MAP.close()
        del MAP

    MAP = Map.random(RANDOM_SEED,SCREEN_SIZE-(0,4),PLAYER)
    MAP.generate()





# main loop
reset()
while not libtcod.console_is_window_closed():

    try:
        # monster movement and items
        TurnTaker.take_all_turns()
    except GameOverError:
        reset(False)
    except LevelWinError:
        reset(True)
