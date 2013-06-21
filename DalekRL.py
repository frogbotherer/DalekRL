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
from errors import InvalidMoveError, GameOverError, LevelWinError

SCREEN_SIZE = Position(80,50)
LIMIT_FPS = 10
RANDOM_SEED = 1999
MAP = None
player = None

# for now
if len(sys.argv)>1 and len(sys.argv[1])>0:
    RANDOM_SEED=int(sys.argv[1])-3

# init window
font = os.path.join(b'resources', b'consolas10x10_gs_tc.png')
libtcod.console_set_custom_font(font, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_SIZE.x, SCREEN_SIZE.y, b'DalekRL')
libtcod.sys_set_fps(LIMIT_FPS)


def do_nothing():
    pass


def reset(keep_player=False):
    global SCREEN_SIZE, RANDOM_SEED, MAP, KEYMAP, player
    evidence = []
    turns    = 0
    if not player is None:
        print("Game Over")
        print("%d evidence in %d turns" %(len(player.evidence),player.turns))

        if keep_player:
            evidence = player.evidence
            turns    = player.turns

    if not MAP is None:
        MAP.close()
        del MAP
    #del player
    RANDOM_SEED += 3
    UI.clear_all()
    print("UI CLEAR")
    TurnTaker.clear_all()
    print("STATICS CLEARED")
    MAP = Map.random(RANDOM_SEED,SCREEN_SIZE-(0,4))
    MAP.generate()
    player          = MAP.player
    player.evidence = evidence
    player.turns    = turns
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
        '2': player.use_item2,
        '3': player.use_item3,
        'q': sys.exit,
        'r': reset,
        ' ': player.interact,
        }

# handle input

def handle_keys():
    MAX_TIMEOUT = 5
    k = libtcod.Key()
    m = libtcod.Mouse()

    for t in range(LIMIT_FPS*MAX_TIMEOUT):
        if t%5 == 0:
            redraw_screen(t/LIMIT_FPS)

        ev = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, k, m)
        if ev and k and k.pressed and chr(k.c) in KEYMAP:
            return KEYMAP.get(chr(k.c))()

    # redraw screen after first second after keypress
    redraw_screen(MAX_TIMEOUT)

    # call this before going into while loop to make sure no keypresses get dropped
    ev = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, k, m)

    while True:
        if k and k.pressed and chr(k.c) in KEYMAP:
            return KEYMAP.get(chr(k.c))()
        k = libtcod.console_wait_for_keypress(True)


def redraw_screen(t):
    # draw and flush screen
    MAP.draw()
    player.draw_ui(Position(0,SCREEN_SIZE.y-3))
    UI.draw_all(t)
    libtcod.console_flush()
    
    # clear screen
    #map.cls()
    libtcod.console_clear(0)


# main loop
reset()
while not libtcod.console_is_window_closed():

    # this should all belong in player.take_turn, I think :P
    player.take_turn()
    try:
        # handle player input (and redraw screen)
        handle_keys()
    except InvalidMoveError:
        print("You can't move like that")
        continue
    player.map.prepare_fov(player.pos)

    try:
        # monster movement and items
        TurnTaker.take_all_turns()
    except GameOverError:
        reset(False)
    except LevelWinError:
        reset(True)


