#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable, Position, Activatable, Activator, CountUp
from items import HandTeleport
from errors import GameOverError
from ui import HBar


class Monster (Mappable):
    def take_turn(self):
        pass

    def __str__(self):
        return "%s at %s" %(self.__class__.__name__,self.pos)



from tangling import Tanglable

class Dalek (Monster,Tanglable):
    def __init__(self,pos=None):
        Monster.__init__(self,pos,'D',libtcod.red)
        Tanglable.__init__(self,5)

    def take_turn(self):
        # sanity checks
        assert not self.map is None, "%s can't take turn without a map" % self

        # if not visible, do nothing
        if not self.is_visible:
            return

        # find player
        p = self.map.find_nearest(self,Player)

        # move towards them
        d = self.pos - p.pos
        v = Position(0,0)

        if d.x > 0:
            v.x = -1
        elif d.x < 0:
            v.x = 1
        if d.y > 0:
            v.y = -1
        elif d.y < 0:
            v.y = 1

        self.move(v)

        # find monster
        m = self.map.find_nearest(self,Monster)

        # if on player square: lose
        if self.pos == p.pos:
            raise GameOverError("Game Over")

        # if on monster square: tangle
        if self.pos == m.pos:
            self.tangle(m)


    


# put here for now
class Player (Mappable,Activator):
    def __init__(self,pos):
        Mappable.__init__(self,pos,'@',libtcod.white)
        self.items = [HandTeleport(self),None,None]

    def use_item(self,slot):
        assert slot<len(self.items), "Using undefined item slot"
        if self.items[slot] is None:
            return
        assert isinstance(self.items[slot],Activatable)
        
        return self.items[slot].activate()


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


class Stairs(Monster,CountUp,Tanglable):
    def __init__(self, pos):
        Monster.__init__(self, pos, '<', libtcod.grey)
        CountUp.__init__(self, 10)
        Tanglable.__init__(self, 10)

        self.bar = HBar(Position(pos.x-2,pos.y-1),5,libtcod.light_blue,libtcod.darkest_grey)
        self.bar.max_value = self.count_to

    def take_turn(self):
        if self.pos == self.map.player.pos:
            if self.count == 0:
                self.bar.is_visible = True
            if self.inc():
                raise GameOverError("You have escaped!")
            else:
                self.bar.value = self.count_to-self.count
        else:
            self.bar.is_visible = False
            self.bar.value = 0
            self.reset()


    
