#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import Carryable, Activatable, CountUp
from ui import Bar, Message

class Item(Carryable, Activatable):
    def __str__(self):
        return "%s held by %s"%(self.__class__.__name__,self.owner)

    def take_turn(self):
        pass

class CoolDownItem(Item, CountUp):
    def __init__(self,owner,count_to):
        Item.__init__(self,owner)
        CountUp.__init__(self,count_to)

    def take_turn(self):
        return self.inc()

    def activate(self):
        if not self.full():
            print ("%s still on cooldown, %d turns remaining"%(self,self.count_to-self.count))
            # still on cooldown
            return False
        self.reset()
        return True


class HandTeleport(CoolDownItem):
    def activate(self):
        if not CoolDownItem.activate(self):
            return False

        p = self.owner.map.find_random_clear()
        self.owner.pos = p
        return True

