#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable, Traversable, Transparent, TurnTaker, CountUp, Position
from ui import HBar

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

class Door(Tile,CountUp):
    def __init__(self, pos):
        Tile.__init__(self, pos, '+', libtcod.light_grey, 0.3, 0.0)
        CountUp.__init__(self, 3)
        self.open = False
        self.bar = HBar(Position(pos.x-1,pos.y-1),3,libtcod.light_green,libtcod.darkest_grey)
        self.bar.max_value = self.count_to-1
        self.bar.timeout = 5.0

    def try_movement(self, obj):
        if self.inc():
            self.open = True
            self.symbol = '-'
            self.colour = libtcod.dark_grey
            self.transparency = 1.0
            self.bar.is_visible = False
            if obj is self.map.player:
                self.map.recalculate_paths()
                self.map.prepare_fov(self.map.player.pos)
            return True
        else:
            if self.map.can_see(self.pos):
                self.bar.is_visible = True
                self.bar.value = self.count_to-self.count
            return False
