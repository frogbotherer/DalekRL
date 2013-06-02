#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import Carryable, Activatable, CountUp
from ui import HBar, Message

class Item(Carryable, Activatable):
    def __str__(self):
        return "%s held by %s"%(self.__class__.__name__,self.owner)

    def take_turn(self):
        pass

    def draw_ui(self,pos,max_width=40):
        pass


class CoolDownItem(Item, CountUp):
    def __init__(self,owner,count_to):
        Item.__init__(self,owner)
        CountUp.__init__(self,count_to)
        self.bar = HBar(None, None, libtcod.red, libtcod.dark_grey, True, False, str(self), str.ljust)
        self.bar.is_visible = False

    def take_turn(self):
        return self.inc()

    def activate(self):
        if not self.full():
            print ("%s still on cooldown, %d turns remaining"%(self,self.count_to-self.count))
            # still on cooldown
            return False
        self.reset(-1) # because we immediately inc()
        return True

    def draw_ui(self,pos,max_width=40):
        self.bar.pos = pos
        self.bar.size = max_width
        self.bar.value = self.count
        self.bar.max_value = self.count_to
        self.bar.is_visible = True


class HandTeleport(CoolDownItem):
    def __str__(self):
        return "Hand Teleport"

    def activate(self):
        if not CoolDownItem.activate(self):
            return False

        p = self.owner.map.find_random_clear()
        self.owner.pos = p
        return True

