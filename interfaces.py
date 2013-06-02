#!/usr/bin/env python3

import libtcodpy as libtcod
from math import hypot

from errors import InvalidMoveError
from ui import Message

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

    def __init__(self, pos, symbol, colour, remains_in_place=False):
        self.map = None
        self.pos = pos
        self.last_known_pos = pos
        self.symbol = symbol
        self.colour = colour
        self.remains_in_place = remains_in_place
        self.is_visible = True
        self.has_been_seen = False

    ##
    # movement
    def move(self, delta):
        """move by a delta"""
        assert not self.remains_in_place, "trying to move immovable object %s" % self
        # test whether movement is valid
        if not self.map is None and self.map.is_blocked(self.pos+delta):
            raise InvalidMoveError( "Can't move %s by %s"%(self,delta) )
            
        self.pos += delta
 
    def move_to(self, pos):
        """move by an absolute"""
        assert not self.remains_in_place, "trying to move immovable object %s" % self
        # test whether movement is valid
        if not self.map is None and self.map.is_blocked(pos):
            raise InvalidMoveError( "Can't move %s to %s"%(self,pos) )
        self.pos = pos


    ##
    # drawing
    def draw(self):
        if not self.is_visible:
            return
        colour = self.colour
        if not self.map.can_see(self.pos):
            if self.has_been_seen and self.remains_in_place:
                colour = libtcod.darkest_grey
            else:
                return
        libtcod.console_put_char_ex(0, self.pos.x, self.pos.y, self.symbol, colour, libtcod.BKGND_NONE)
        self.has_been_seen = True
 
#    def clear(self):
#        if not self.is_visible: # this probably needs to be cleverer
#            return
#
#        #erase the character that represents this object
#        libtcod.console_put_char(0, self.pos.x, self.pos.y, ' ', libtcod.BKGND_NONE)


class Traversable:
    def __init__(self, walk_cost=0.0):
        # 0.0 => can't traverse
        # 1.0 => traverse with no penalty
        self.walk_cost = walk_cost

    def blocks_movement(self):
        return self.walk_cost == 0.0

class Transparent:
    def __init__(self, transparency=0.0):
        # 0.0 => completely opaque
        # 1.0 => completely transparent
        self.transparency = transparency

    def blocks_light(self):
        return self.transparency == 0.0


class CountUp:
    """things that count up (e.g. multi-turn stairs traversal)"""
    def __init__(self,count_to,c=0):
        self.count_to = count_to
        self.count    = c

    def inc(self):
        if self.full():
            return True
        self.count += 1
        return self.full()

    def reset(self,c=0):
        self.count = c

    def full(self):
        return self.count == self.count_to


class Carryable:
    pass

class Activator:
    pass

class Activatable:
    def __init__(self,owner):
        assert isinstance(owner,Activator), "%s can't activate %s"%(owner,self.__classname__)
        self.owner = owner

    def activate(self):
        raise NotImplementedError("%s can't be activated"%self.__classname__)

class Talker:
    def __init__(self,phrases,probability=0.05):
        self.__phrases = phrases
        self.__probability = probability
        self.is_talking = False
        self.__chat = Message(None, "", True)
        self.__chat.is_visible = False
        self.__chat.timeout = 2.0

    def talk(self):
        if self.is_talking:
            self.__chat.is_visible = False
            self.is_talking = False

        elif libtcod.random_get_float(None,0.0,1.0)<self.__probability:
            self.__chat.pos = self.pos-(0,1)
            self.__chat.text = self.__phrases[libtcod.random_get_int(None,0,len(self.__phrases)-1)]
            self.is_talking = True
            self.__chat.is_visible = True
    
