#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import Carryable, Activatable, Activator, CountUp, Mappable, TurnTaker
from ui import HBar, Message

class Item(Carryable, Activatable, Mappable):
    def __init__(self, owner, colour):
        pos = None
        if not isinstance(owner, Activator):
            pos   = owner
            owner = None
        Mappable.__init__(self,pos,'!',colour)
        Activatable.__init__(self,owner)
        if pos is None:
            self.is_visible = False

    def __str__(self):
        if self.owner is None:
            return "%s at %s"%(self.__class__.__name__,self.pos)
        else:
            return "%s held by %s"%(self.__class__.__name__,self.owner)

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

    def random(rng,pos,lclamp=0.0,hclamp=1.0):
        """random item at pos using rng. raising lclamp removes bad items; lowering hclamp removes good items"""
        t = libtcod.random_get_float(rng,lclamp,hclamp)

        if t < 0.8:
            return Tangler(pos,libtcod.random_get_int_mean(rng,1,2,4))
        elif t < 0.9:
            return HandTeleport(pos,libtcod.random_get_int(rng,10,20))
        else:
            return Cloaker(pos,libtcod.random_get_int(rng,15,25))


class CoolDownItem(Item, CountUp, TurnTaker):
    def __init__(self,owner,count_to,item_colour=libtcod.green,bar_colour=libtcod.dark_green):
        Item.__init__(self,owner,item_colour)
        CountUp.__init__(self,count_to)
        TurnTaker.__init__(self,100)
        self.bar = HBar(None, None, bar_colour, libtcod.dark_grey, True, False, str(self), str.ljust)
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
    def __init__(self,owner,uses,item_colour=libtcod.orange,bar_colour=libtcod.red):
        Item.__init__(self,owner,item_colour)
        self.max_uses = uses
        self.uses = uses
        self.bar = HBar(None, None, bar_colour, libtcod.dark_grey, True, False, str(self), str.ljust)
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


class Cloaker(CoolDownItem):
    def __init__(self,owner,uses):
        CoolDownItem.__init__(self,owner,uses,libtcod.light_blue,libtcod.dark_blue)
        self.hidden_at = None

    def __str__(self):
        return "Cloaker"

    def activate(self):
        if not CoolDownItem.activate(self):
            return False
        self.owner.is_visible = False
        self.hidden_at = self.owner.pos
        self.inc()
        return True
    
    def take_turn(self):

        # only run cooldown whilst effect inactive
        if self.hidden_at is None:
            CoolDownItem.take_turn(self)

        # player moved; unhide them
        elif self.hidden_at != self.owner.pos:
            self.owner.is_visible = True
            self.hidden_at = None



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


class Evidence(Item):
    def __str__(self):
        return "Evidence"

    def __init__(self,pos):
        Item.__init__(self,pos,libtcod.yellow)
