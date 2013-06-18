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

class Door(Tile,CountUp,TurnTaker):
    OPEN = {'symbol':'.','colour':libtcod.dark_grey,'transparency':1.0,'walkcost':1.0,
            'timer':6, 'barcolour': libtcod.light_red
            }
    CLOSING = {'symbol':'-','colour':libtcod.grey,'transparency':1.0,'walkcost':1.0,
               'timer':4, 'barcolour': libtcod.light_red
               }
    CLOSED = {'symbol':'+','colour':libtcod.light_grey,'transparency':0.0,'walkcost':0.3,
              'timer':4, 'barcolour': libtcod.light_green
              }
    def __init__(self, pos):
        Tile.__init__(self, pos, Door.CLOSED['symbol'], Door.CLOSED['colour'], Door.CLOSED['walkcost'], Door.CLOSED['transparency'])
        CountUp.__init__(self, Door.CLOSED['timer'])
        TurnTaker.__init__(self,5)
        self.state = Door.CLOSED
        self.bar = HBar(Position(pos.x-1,pos.y-1),3,Door.CLOSED['barcolour'],libtcod.darkest_grey)
        self.bar.max_value = self.count_to-1
        self.bar.timeout = 5.0

    def _open(self):
        self.__change(Door.OPEN)
        self.map.recalculate_paths()
        self.map.prepare_fov(self.map.player.pos)

    def _closed(self):
        self.__change(Door.CLOSED)
        self.map.recalculate_paths()
        self.map.prepare_fov(self.map.player.pos)

    def _closing(self):
        self.__change(Door.CLOSING)

    def __change(self,state_dat):
        self.state = state_dat
        self.symbol = state_dat['symbol']
        self.colour = state_dat['colour']
        self.transparency = state_dat['transparency']
        self.walk_cost = state_dat['walkcost']
        self.count_to = state_dat['timer']
        self.bar.fgcolours = [state_dat['barcolour']]
        self.reset()

    def try_movement(self, obj):
        if self.state is Door.OPEN:
            return True

        elif self.state is Door.CLOSING:
            self.reset()
            return True

        else: # Door.CLOSED
            if self.inc():
                self.bar.is_visible = False
                self._open()
                #if obj is self.map.player: # i think we need to do this anyway
                #    self.map.recalculate_paths()
                #    self.map.prepare_fov(self.map.player.pos)
                return True
            else:
                if self.map.can_see(self.pos):
                    self.bar.is_visible = True
                    self.bar.value = self.count_to-self.count
                return False

    def take_turn(self):
        if self.state is Door.CLOSED:
            return

        else: # open or closing
            if self.inc():
                self.bar.is_visible = False
                if self.state is Door.OPEN:
                    self._closing()
                else: # closing
                    self._closed()
            elif self.state is Door.CLOSING:
                # don't show state whilst open
                if self.map.can_see(self.pos):
                    self.bar.is_visible = True
                    self.bar.value = self.count_to-self.count
                else:
                    self.bar.is_visible = False
