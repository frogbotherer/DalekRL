#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import Mappable, Activator, Activatable, TurnTaker, Position, StatusEffect, HasInventory, Talker
from items import Item, SlotItem, Evidence, XRaySpecs, RunningShoes
from tiles import Tile
from ui import UI, Menu
from errors import GameOverError, InvalidMoveError

import sys
from time import sleep

class Player (Mappable,Activator,TurnTaker,StatusEffect,HasInventory):
    # these don't really belong here
    SCREEN_SIZE = Position(80,50)
    LIMIT_FPS = 15
    MAX_TIMEOUT = 5

    def __init__(self,pos=None):
        Mappable.__init__(self,pos,'@',libtcod.white)
        StatusEffect.__init__(self)
        TurnTaker.__init__(self,1)
        HasInventory.__init__(self,3,(SlotItem.HEAD_SLOT,SlotItem.BODY_SLOT,SlotItem.FEET_SLOT))
        self.items = [Item.random(None,self,2,1.5),Item.random(None,self,1),None]
        self.slot_items = {
            SlotItem.HEAD_SLOT: XRaySpecs(self),
            SlotItem.BODY_SLOT: None,
            SlotItem.FEET_SLOT: RunningShoes(self),
            }
        self.turns = 0
        self.evidence = []
        self.levels_seen = 1
        
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
            '4': self.use_head,
            '5': self.use_body,
            '6': self.use_feet,
            'q': sys.exit,
            'r': self.reset_game,
            ' ': self.interact,
            }



    def __str__(self):
        return "Player at %s" % self.pos

    def use_item(self,slot):
        assert slot in self.slot_items.keys() or slot<len(self.items), "Using undefined item slot"

        item = None
        if slot in self.slot_items.keys():
            item = self.slot_items[slot]
        elif isinstance(slot,int):
            item = self.items[slot]

        if item is None:
            return
        assert isinstance(item,Activatable)
        
        return item.activate()

    def draw_ui(self,pos,max_size=80):
        # UI constants TODO: move them
        COL_W = 24
        C_MARGIN_W = 1

        # print inventory items
        for i in range(len(self.items)):
            libtcod.console_print(0, pos.x, pos.y+i, "%d."%(i+1))
            if self.items[i] is None:
                libtcod.console_print(0, pos.x+3, pos.y+i, "--- Nothing ---")
            else:
                self.items[i].draw_ui(pos+(3,i), COL_W)

        # print slot items
        i = 4
        for s in (SlotItem.HEAD_SLOT,SlotItem.BODY_SLOT,SlotItem.FEET_SLOT):
            libtcod.console_print(0, pos.x+COL_W+3+C_MARGIN_W, pos.y+i-4, "%d."%(i))
            if self.slot_items[s] is None:
                libtcod.console_print(0, pos.x+COL_W+3+C_MARGIN_W+3, pos.y+i-4, "--- Nothing ---")
            else:
                self.slot_items[s].draw_ui(pos+(COL_W+3+C_MARGIN_W+3,i-4), COL_W)
            i += 1
        
        # print info
        libtcod.console_print(0, pos.x + COL_W*2 + C_MARGIN_W*2 + 3+3, pos.y,   "Level:    %5d" % self.levels_seen)
        libtcod.console_print(0, pos.x + COL_W*2 + C_MARGIN_W*2 + 3+3, pos.y+1, "Evidence: %5d" % len(self.evidence))
        libtcod.console_print(0, pos.x + COL_W*2 + C_MARGIN_W*2 + 3+3, pos.y+2, "Turns:    %5d" % self.turns)

    def reset_fov(self):
        if self.has_effect(StatusEffect.BLIND):
            return self.map.prepare_fov(self.pos,4)
        elif self.has_effect(StatusEffect.X_RAY_VISION):
            return self.map.prepare_fov(self.pos,10)
        else:
            return self.map.prepare_fov(self.pos,0)

    def pickup(self,i):
        """returns True if i picked up successfully"""
        # TODO: move all this into HasInventory interface
        assert isinstance(i,Item), "Can't pick up a %s"%i

        if isinstance(i,Evidence):
            self.evidence.append(i)
            if not i.pos is None: # found it in a locker
                self.map.remove(i)
            return True

        item_index = None
        items      = self.items
        if isinstance(i,SlotItem):
            items  = [self.slot_items[i.valid_slot]]
        if not None in items:
            # prompt to drop something; drop it

            xu = self.map.size.x//4
            yu = self.map.size.y//4
            b = Menu( Position(xu,yu), Position(xu*2,yu*2), title="Pick Up" )
            b.add('x',str(i))
            b.add_spacer()
            for idx in range(len(items)):
                v = items[idx]
                b.add('%d'%(idx+1),str(v))
            c = b.get_key()
            if isinstance(c,str) and c.isnumeric():
                item_index = int(c) - 1

            del b
            if item_index is None or item_index >= len(items):
                return False
            items[item_index].drop_at(self.pos)
            self.map.add(items[item_index])
        else:
            item_index = items.index(None)

        if isinstance(i,SlotItem):
            self.slot_items[i.valid_slot] = i
        else:
            self.items[item_index] = i

        if not i.pos is None: # if taken from locker or other bonus
            self.map.remove(i)
        i.take_by(self)
        return True

    def do_nothing(self):
        self.move( (0,0) ) # triggers try_movement on current square
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
    def use_head(self):
        self.use_item(SlotItem.HEAD_SLOT)
    def use_body(self):
        self.use_item(SlotItem.BODY_SLOT)
    def use_feet(self):
        self.use_item(SlotItem.FEET_SLOT)
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
            pass # sometimes this is ok, like teleporting
            #print("You can't move like that")
        Talker.stop_all_talk()
        self.reset_fov()

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
        if not UI.need_update(t):
            # clearly one of the libtcod functions here causes the wait for the next frame
            sleep(1.0/Player.LIMIT_FPS)
            return

        self.map.draw()
        self.draw_ui(Position(0,Player.SCREEN_SIZE.y-3))
        UI.draw_all(t)

        libtcod.console_flush()

        # clear screen
        libtcod.console_clear(0)


    def refresh_turntaker(self):
        TurnTaker.refresh_turntaker(self)
        for i in self.items + list(self.slot_items.values()):
            if isinstance(i,TurnTaker):
                i.refresh_turntaker()

            # TODO: this isn't great :(
            if hasattr(i,'bar') and isinstance(i.bar,UI):
                i.bar.refresh_ui_list()
