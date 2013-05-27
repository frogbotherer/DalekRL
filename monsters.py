#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable, Tanglable, Position

class Monster (Mappable):
    def take_turn(self):
        pass


class Dalek (Monster,Tanglable):
    def __init__(self,pos=None):
        Monster.__init__(self,pos,'D',libtcod.red)
        Tanglable.__init__(self,5)

    def take_turn(self):
        # sanity checks
        assert not self.map is None, "%s can't take turn without a map" % self

        # if tangled: untangle
        if self.untangle():
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
            raise Exception("Game Over")

        # if on monster square: tangle
        if self.pos == m.pos:
            self.tangle()
            m.tangle()




# put here for now
class Player (Mappable):
    def __init__(self,pos):
        Mappable.__init__(self,pos,'@',libtcod.white)
        self.items = [None,None,None]

#    def use_item(self,slot):
#        assert slot 
