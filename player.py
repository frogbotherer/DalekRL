#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import Mappable, Activator, Activatable, TurnTaker, Position
from items import Item, Evidence
from tiles import Tile
from ui import UI, Menu
from errors import GameOverError, InvalidMoveError

import sys

class Player (Mappable,Activator,TurnTaker):
    # these don't really belong here
    SCREEN_SIZE = Position(80,50)
    LIMIT_FPS = 10
    MAX_TIMEOUT = 5

    def __init__(self,pos=None):
        Mappable.__init__(self,pos,'@',libtcod.white)
        TurnTaker.__init__(self,0)
        self.items = [Item.random(None,self,2,1.5),Item.random(None,self,1),None]
        self.turns = 0
        self.evidence = []
        self.levels_seen = 0
        
        self.KEYMAP = {
            'k': self.move_n,
            'j': self.move_s,
            'h': self.move_w,
            'l': self.move_e,
            'y': self.move_nw,
            'u': self.move_ne,
            'b': self.move_sw,
            'n': self.move_se,
            '.': self.do_nothing,
            '1': self.use_item1,
            '2': self.use_item2,
            '3': self.use_item3,
            'q': sys.exit,
            'r': self.reset_game,
            ' ': self.interact,
            }



    def __str__(self):
        return "Player at %s" % self.pos

    def use_item(self,slot):
        assert slot<len(self.items), "Using undefined item slot"
        if self.items[slot] is None:
            return
        assert isinstance(self.items[slot],Activatable)
        
        return self.items[slot].activate()

    def draw_ui(self,pos,max_size=80):
        for i in range(len(self.items)):
            libtcod.console_print(0, pos.x, pos.y+i, "%d."%(i+1))
            if self.items[i] is None:
                libtcod.console_print(0, pos.x+3, pos.y+i, "--- Nothing ---")
            else:
                self.items[i].draw_ui(pos+(3,i), 40)

    def pickup(self,i):
        assert isinstance(i,Item), "Can't pick up a %s"%i

        if isinstance(i,Evidence):
            self.evidence.append(i)
            self.map.remove(i)
            return

        item_index = None
        if not None in self.items:
            # prompt to drop something; drop it

            ###
            # prompt code [TODO: refactor me!]
            xu = self.map.size.x//4
            yu = self.map.size.y//4
            b = Menu( Position(xu,yu), Position(xu*2,yu*2), title="Pick up" )
            b.add('x',str(i))
            b.add_spacer()
            for idx in range(len(self.items)):
                v = self.items[idx]
                b.add('%d'%(idx+1),str(v))
            b.is_visible = True
            while 1:
                b.draw()
                libtcod.console_flush()
                k = libtcod.console_wait_for_keypress(True)
                if k and k.pressed and k.c:
                    c = chr(k.c)
                    if   c == 'x':
                        break
                    elif c == '1':
                        item_index = 0
                        break
                    elif c == '2':
                        item_index = 1
                        break
                    elif c == '3':
                        item_index = 2
                        break
                    elif c == 'j':
                        b.sel_prev()
                    elif c == 'k':
                        b.sel_next()
                    elif c == ' ':
                        if b.sel_index() != 0:
                            item_index = b.sel_index()-1
                        break
            b.is_visible = False
            del b
            if item_index is None:
                return
            self.items[item_index].drop_at(self.pos)
            self.map.add(self.items[item_index])
        else:
            item_index = self.items.index(None)
        self.items[item_index] = i
        self.map.remove(i)
        i.take_by(self)

    def do_nothing(self):
        pass
    def reset_game(self):
        raise GameOverError
    def move_n(self):
        self.move( (0,-1) )
    def move_s(self):
        self.move( (0,1) )
    def move_w(self):
        self.move( (-1,0) )
    def move_e(self):
        self.move( (1,0) )
    def move_ne(self):
        self.move( (1,-1) )
    def move_nw(self):
        self.move( (-1,-1) )
    def move_se(self):
        self.move( (1,1) )
    def move_sw(self):
        self.move( (-1,1) )
    def use_item1(self):
        self.use_item(0)
    def use_item2(self):
        self.use_item(1)
    def use_item3(self):
        self.use_item(2)
    def interact(self):
        i = self.map.find_at_pos(self.pos,Item)
        if not i is None:
            self.pickup(i)
        for i in self.map.find_all_at_pos(self.pos,Tile):
            if isinstance(i,Activatable):
                i.activate(self)

    def take_turn(self):
        self.turns += 1
        try:
            # handle player input (and redraw screen)
            self.handle_keys()
        except InvalidMoveError:
            print("You can't move like that")
        self.map.prepare_fov(self.pos)

    def handle_keys(self):
        k = libtcod.Key()
        m = libtcod.Mouse()

        for t in range(Player.LIMIT_FPS*Player.MAX_TIMEOUT):
            if t%5 == 0:
                self.redraw_screen(t/Player.LIMIT_FPS)

            ev = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, k, m)
            if ev and k and k.pressed and chr(k.c) in self.KEYMAP:
                return self.KEYMAP.get(chr(k.c))()

        # redraw screen after first second after keypress
        self.redraw_screen(Player.MAX_TIMEOUT)

        # call this before going into while loop to make sure no keypresses get dropped
        ev = libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, k, m)

        while True:
            if k and k.pressed and chr(k.c) in self.KEYMAP:
                return self.KEYMAP.get(chr(k.c))()
            k = libtcod.console_wait_for_keypress(True)

    def redraw_screen(self,t):
        # draw and flush screen
        self.map.draw()
        self.draw_ui(Position(0,Player.SCREEN_SIZE.y-3))
        UI.draw_all(t)
        libtcod.console_flush()

        # clear screen
        libtcod.console_clear(0)

