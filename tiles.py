#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable, Traversable, Transparent, TurnTaker, CountUp, Position, Activatable
from errors import LevelWinError, InvalidMoveError
from ui import HBar

class Tile(Mappable,Traversable,Transparent):
    def __init__(self, pos, symbol, colour, walk_cost=0.0, transparency=0.0, may_block_movement=False):
        """walk_cost == 0.0  =>  can't traverse tile
        walk_cost > 0.0; may_block_movement == True  =>  pathing shouldn't rely on tile being traversable (e.g. teleport tiles, locked doors)"""
        Mappable.__init__(self,pos,symbol,colour,remains_in_place=True)
        Traversable.__init__(self,walk_cost,may_block_movement)
        Transparent.__init__(self,transparency)

    def random_furniture(rng, pos):
        return Crate(pos)

class Wall(Tile):
    def __init__(self, pos):
        Tile.__init__(self, pos, '#', libtcod.light_grey)

class Floor(Tile):
    def __init__(self, pos):
        Tile.__init__(self, pos, '.', libtcod.dark_grey, 1.0, 1.0)

class StairsUp(Tile):
    def __init__(self, pos):
        Tile.__init__(self, pos, '<', libtcod.dark_grey, 1.0, 1.0)

class StairsDown(Tile,CountUp,TurnTaker):
    def __init__(self, pos):
        Tile.__init__(self, pos, '>', libtcod.light_grey, 1.0, 1.0)
        CountUp.__init__(self, 11)
        TurnTaker.__init__(self, 0)

        self.bar = HBar(Position(pos.x-2,pos.y-1),5,libtcod.light_blue,libtcod.darkest_grey)
        self.bar.max_value = self.count_to-1
        self.bar.timeout = 5.0

    def take_turn(self):

        if self.pos == self.map.player.pos:
            if self.count == 0:
                self.bar.is_visible = True
            if self.inc():
                raise LevelWinError("You have escaped!")
            else:
                self.bar.value = self.count_to-self.count
        elif self.count > 0:
            self.bar.is_visible = False
            self.bar.value = 0
            self.reset()

class Crate(Tile, Activatable):
    def __init__(self, pos):
        Tile.__init__(self, pos, 'N', libtcod.light_grey, 1.0, 0.8)
        Activatable.__init__(self)
        self.remains_in_place = False

    def activate(self, activator=None):
        print("activating by %s"%activator)
        # sanity
        if not (self.owner is None or self.owner is activator):
            raise InvalidMoveError("Crate already occupied by %s" % self.owner)
        assert not activator is None, "Crate activated by None"

        # climb into crate
        if self.owner is None:
            self.owner = activator
            self.owner.is_visible = False

        # climb out of crate
        else:
            self.owner.is_visible = True
            self.owner = None
        return True

    def try_leaving(self, obj):
        # prevent leaving if in crate
        return not obj is self.owner


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
        self.unseen_symbol = Door.CLOSED['symbol'] # always shows as closed when can't be seen
        self.state = Door.CLOSED
        self.bar = HBar(Position(pos.x-1,pos.y-1),3,Door.CLOSED['barcolour'],libtcod.darkest_grey)
        self.bar.max_value = self.count_to-1
        self.bar.timeout = 5.0
        self._trying_to_open = False

    def to_open(self):
        self.__change(Door.OPEN)
        self.map.recalculate_paths()
        self.map.player.reset_fov()

    def to_closed(self):
        self.__change(Door.CLOSED)
        self.map.recalculate_paths()
        self.map.player.reset_fov()

    def to_closing(self):
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
            self._trying_to_open = True
            if self.inc():
                self.bar.is_visible = False
                self.to_open()
                #if obj is self.map.player: # i think we need to do this anyway
                #    self.map.recalculate_paths()
                #    self.map.player.reset_fov()
                return True
            else:
                if self.map.can_see(self):
                    self.bar.is_visible = True
                    self.bar.value = self.count_to-self.count
                return False

    def take_turn(self):
        if self.state is Door.CLOSED:
            if self._trying_to_open:
                self._trying_to_open = False
            else:
                self.bar.is_visible = False
                self.reset()
            return

        else: # open or closing
            if self.inc():
                self.bar.is_visible = False
                if self.state is Door.OPEN:
                    self.to_closing()
                else: # closing
                    self.to_closed()
            elif self.state is Door.CLOSING:
                # don't show state whilst open
                if self.map.can_see(self):
                    self.bar.is_visible = True
                    self.bar.value = self.count_to-self.count
                else:
                    self.bar.is_visible = False


# implemented as a turn taker
#from monsters import Monster
#from player import Player
#class FloorTeleport(Tile,TurnTaker):
#    def __init__(self, pos):
#        Tile.__init__(self, pos, '^', libtcod.purple, 0.2, 1.0)
#        TurnTaker.__init__(self,1000)
#
#    def take_turn(self):
#        # sanity
#        if len(self.map.find_all_at_pos(self.pos,[Monster,Player])) == 0:
#            return
#
#        targets = self.map.find_all(FloorTeleport,Tile)
#        targets.remove(self)
#
#        if len(targets) == 0:
#            return # oops, only one telepad on the level
#
#        for obj in self.map.find_all_at_pos(self.pos,[Monster,Player]):
#            try:
#                obj.move_to( targets[libtcod.random_get_int(None,0,len(targets)-1)].pos )
#
#            except InvalidMoveError:
#                pass # teleport exit blocked?


# implemented using the try_movement() method
class FloorTeleport(Tile):
    def __init__(self, pos):
        Tile.__init__(self, pos, '^', libtcod.purple, 0.2, 1.0, True)

    def try_movement(self,obj):

        if obj.pos.distance_to(self.pos) >= 2:
            # moving to this tile from far away: must be teleporting; don't teleport again!
            return True

        try:
            targets = self.map.find_all(FloorTeleport,Tile)
            targets.remove(self)
            if len(targets) == 0:
                pass # oops, only one telepad on the level
            else:
                obj.move_to( targets[libtcod.random_get_int(None,0,len(targets)-1)].pos )

        except InvalidMoveError:
            pass # teleport exit blocked?

        return False # prevent original movement

