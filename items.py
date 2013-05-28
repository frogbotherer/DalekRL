#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import Carryable, Activatable

class Item(Carryable, Activatable):
    pass


class HandTeleport(Item):
    def activate(self):
        p = self.owner.map.find_random_clear()
        self.owner.pos = p
        return True

