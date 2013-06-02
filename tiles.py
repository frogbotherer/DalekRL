#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable, Traversable, Transparent

class Tile(Mappable,Traversable,Transparent):
    def __init__(self, pos, symbol, colour, walk_cost=0.0, transparency=0.0):
        Mappable.__init__(self,pos,symbol,colour,remains_in_place=True)
        Traversable.__init__(self,walk_cost)
        Transparent.__init__(self,transparency)

class Wall(Tile):
    def __init__(self, pos):
        Tile.__init__(self, pos, '#', libtcod.light_grey)

class Floor(Tile):
    def __init__(self, pos):
        Tile.__init__(self, pos, '.', libtcod.dark_grey, 1.0, 1.0)

#class Stairs(Tile):
#    def __init__(self, pos):
#        Tile.__init__(self, pos, '<', libtcod.grey, 1.0)

class Glass(Tile):
    def __init__(self, pos):
        Tile.__init__(self, pos, '0', libtcod.light_grey, 0.0, 1.0)
