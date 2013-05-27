#!/usr/bin/env python3

import libtcodpy as libtcod
from math import hypot

class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __add__(self,other):
        if isinstance(other,tuple):
            return Position(self.x + other[0], self.y + other[1])
        else:
            return Position(self.x + other.x, self.y + other.y)

    def __sub__(self,other):
        if isinstance(other,tuple):
            return Position(self.x - other[0], self.y - other[1])
        else:
            return Position(self.x - other.x, self.y - other.y)

    def __gt__(self,other):
        """Furthest from origin is largest; if tied, larger x beats larger y so that we sort left-right, top-bottom"""
        return (self.x*self.y>other.x*other.y) or (self.x>other.x)
    def __ge__(self,other):
        return (self.x*self.y>other.x*other.y) or (self.x>=other.x)
    def __eq__(self,other):
        return self.x==other.x and self.y==other.y

    def __repr__(self):
        return "Position(%d,%d)" % (self.x,self.y)

    def __str__(self):
        return "(%d,%d)" % (self.x,self.y)

    def distance_to(self,other):
        """returns distance to other"""
        return hypot(self.x-other.x,self.y-other.y)


class Mappable:
    """Can appear on the map"""

    def __init__(self,pos,symbol,colour,walk_cost=0.0):
        self.map = None
        self.pos = pos
        self.symbol = symbol
        self.colour = colour
        self.walk_cost = walk_cost

    ##
    # movement
    def move(self, delta):
        #move by the given amount
        self.pos += delta
 
    def move_to(self, pos):
        self.pos = pos

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


    ##
    # map stuff

    ##
    # drawing
    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(0, self.colour)
        libtcod.console_put_char(0, self.pos.x, self.pos.y, self.symbol, libtcod.BKGND_NONE)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(0, self.pos.x, self.pos.y, ' ', libtcod.BKGND_NONE)


class Tanglable:
    def __init__(self,tangle_turns=5):
        self.tangle_counter = 0
        self.tangle_turns = tangle_turns

    def tangle(self):
        self.tangle_counter = self.tangle_turns

    def is_tangled(self):
        return self.tangle_counter > 0

    def untangle(self):
        if not self.is_tangled():
            return False
        self.tangle_counter -= 1
        return True


# for later
class Item:
    pass
class Tile:
    pass
