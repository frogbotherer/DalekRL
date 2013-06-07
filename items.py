#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import Carryable, Activatable, Activator, CountUp, Mappable
from ui import HBar, Message

class Item(Carryable, Activatable, Mappable):
    def __init__(self, owner):
        pos = None
        if not isinstance(owner, Activator):
            pos   = owner
            owner = None
        Mappable.__init__(self,pos,'!',libtcod.green)
        Activatable.__init__(self,owner)
        if pos is None:
            self.is_visible = False

    def __str__(self):
        if self.owner is None:
            return "%s at %s"%(self.__class__.__name__,self.pos)
        else:
            return "%s held by %s"%(self.__class__.__name__,self.owner)

    def take_turn(self):
        pass

    def draw_ui(self,pos,max_width=40):
        pass

    def drop_at(self,pos):
        self.owner = None
        self.pos = pos
        self.is_visible = True

    def take_by(self,owner):
        self.owner = owner
        self.pos = None
        self.is_visible = False

    def random(rng,pos):
        return Tangler(pos,libtcod.random_get_int_mean(rng,1,2,4))


class CoolDownItem(Item, CountUp):
    def __init__(self,owner,count_to):
        Item.__init__(self,owner)
        CountUp.__init__(self,count_to)
        self.bar = HBar(None, None, libtcod.dark_green, libtcod.dark_grey, True, False, str(self), str.ljust)
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

    def drop_at(self,pos):
        Item.drop_at(self,pos)
        self.bar.is_visible = False

    def take_by(self,owner):
        Item.take_by(self,owner)
        self.bar.is_visible = True


class LimitedUsesItem(Item):
    def __init__(self,owner,uses):
        Item.__init__(self,owner)
        self.max_uses = uses
        self.uses = uses
        self.bar = HBar(None, None, libtcod.red, libtcod.dark_grey, True, False, str(self), str.ljust)
        self.bar.is_visible = False

    def draw_ui(self,pos,max_width=40):
        self.bar.pos = pos
        self.bar.size = max_width
        self.bar.value = self.uses
        self.bar.max_value = self.max_uses
        self.bar.is_visible = True

    def activate(self):
        if self.uses == 0:
            return False

        self.uses -= 1
        return True

    def drop_at(self,pos):
        Item.drop_at(self,pos)
        self.bar.is_visible = False

    def take_by(self,owner):
        Item.take_by(self,owner)
        self.bar.is_visible = True


class HandTeleport(CoolDownItem):
    def __str__(self):
        return "Hand Teleport"

    def activate(self):
        if not CoolDownItem.activate(self):
            return False

        self.owner.move_to(self.owner.map.find_random_clear())
        return True


from tangling import Tanglable, Tangle
from monsters import Monster

class Tangler(LimitedUsesItem):
    def __str__(self):
        return "Tangler"

    def activate(self):
        # TODO: make this find the nearest untangled tanglable
        m = self.owner.map.find_nearest(self.owner,Monster)
        if isinstance(m, Tanglable) and not m.is_tangled() and LimitedUsesItem.activate(self):
            t = Tangle()
            t.add(m)
            return True

        return False
