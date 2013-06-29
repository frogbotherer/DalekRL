#!/usr/bin/env python3

import libtcodpy as libtcod
from math import hypot
import weakref

from errors import InvalidMoveError
from ui import Message

class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x,self.y))

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

    def __init__(self, pos, symbol, colour, remains_in_place=False, unseen_symbol=None, unseen_colour=libtcod.darkest_grey):
        self.map = None
        self.pos = pos
        self.last_known_pos = pos
        self.symbol = symbol
        self.colour = colour
        self.remains_in_place = remains_in_place

        self.is_visible = True
        self.has_been_seen = False
        self.unseen_symbol = (unseen_symbol is None) and self.symbol or unseen_symbol
        self.unseen_colour = unseen_colour

    ##
    # movement
    def move(self, delta):
        """move by a delta"""
        return self.move_to(self.pos+delta)
 
    def move_to(self, pos):
        """move by an absolute"""
        assert not self.remains_in_place, "trying to move immovable object %s" % self
        # test whether movement is valid
        if not self.map is None and self.map.is_blocked(pos):
            raise InvalidMoveError( "Can't move %s to %s"%(self,pos) )

        self.map.move(self, pos)

    ##
    # drawing
    def draw(self):
        # NB. this gets called a lot!
        if not self.is_visible:
            return
        colour = self.colour
        symbol = self.unseen_symbol
        if not self.map._drawing_can_see(self.pos):
            if self.has_been_seen and self.remains_in_place:
                colour = self.unseen_colour
                symbol = self.unseen_symbol
            else:
                return
        libtcod.console_put_char_ex(0, self.pos.x, self.pos.y, self.symbol, colour, libtcod.BKGND_NONE)
        self.has_been_seen = True


class TurnTaker:
    turn_takers = []

    def __init__(self, initiative):
        """Lowest initiative goes first"""
        self.initiative = initiative
        TurnTaker.turn_takers.append(weakref.ref(self))        
        TurnTaker.turn_takers.sort( key = lambda x: x() is None and 100000 or x().initiative )

    def take_turn(self):
        raise NotImplementedError

    def take_all_turns():
        for tref in TurnTaker.turn_takers:
            t = tref()
            if t is None:
                TurnTaker.turn_takers.remove(tref)
            else:
                t.take_turn()

    def clear_all():
        for tref in TurnTaker.turn_takers:
            t = tref()
            if not t is None:
                del t
        TurnTaker.turn_takers = []

    def refresh_turntaker(self):
        if not weakref.ref(self) in TurnTaker.turn_takers:
            # might be a faster way to do this
            TurnTaker.turn_takers.append(weakref.ref(self))        
            TurnTaker.turn_takers.sort( key = lambda x: x() is None and 100000 or x().initiative )        

class Traversable:
    def __init__(self, walk_cost=0.0, may_block_movement=False):
        # 0.0 => can't traverse
        # 1.0 => traverse with no penalty
        self.walk_cost = walk_cost
        # False => try_movement always True
        # True  => try_movement might return False
        self.may_block_movement = may_block_movement

    def try_leaving(self,obj):
        return True

    def try_movement(self,obj):
        return True

    def blocks_movement(self, is_for_mapping=False):
        return (self.walk_cost == 0.0) and (not is_for_mapping or self.may_block_movement)

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
    def __init__(self,owner=None):
        assert isinstance(owner,Activator) or owner is None, "%s can't activate %s"%(owner,self)
        self.owner = owner

    def activate(self,activator=None):
        assert isinstance(self.owner,Activator) or isinstance(activator,Activator), "%s can't be activated" % self
        return True

class Alertable:
    def __init__(self,listen_radius=10):
        self.listen_radius = listen_radius

    def alert(self,to_pos):
        if hasattr(self,'pos'):
            return to_pos.distance_to(self.pos) <= self.listen_radius
        else:
            return True


class Talker:
    def __init__(self):
        self.__phrases = {}
        self.is_talking = False
        self.__chat = Message(None, "", True)
        self.__chat.is_visible = False
        self.__chat.timeout = 2.0

    def add_phrases(self,key,phrases,probability=0.05,is_shouting=False):
        if not key in self.__phrases.keys():
            self.__phrases[key] = {}
        self.__phrases[key]['probability'] = probability
        self.__phrases[key]['is_shouting'] = is_shouting
        self.__phrases[key]['phrases']     = phrases
        return self

    def stop_talk(self):
        self.__chat.is_visible = False
        self.is_talking = False

    def talk(self, key=None):
        if self.is_talking:
            self.stop_talk()
        if not key in self.__phrases.keys():
            return
        if libtcod.random_get_float(None,0.0,1.0)<self.__phrases[key]['probability']:
            #assert key in self.__phrases.keys(), "Talker %s has no vocab for key %s"%(self,key)
            self.__chat.pos = self.pos-(0,1)
            self.__chat.text = self.__phrases[key]['phrases'][libtcod.random_get_int(None,0,len(self.__phrases[key]['phrases'])-1)]
            self.is_talking = True
            self.__chat.is_visible = True
            if isinstance(self,Shouter) and self.__phrases[key]['is_shouting']:
                self.shout()
    

class Shouter:
    def __init__(self,audible_radius=10):
        assert isinstance(self,Mappable), "Shouter must be a mappable object" # bad mi??
        self.audible_radius=audible_radius

    def shout(self,at_pos=None):
        if at_pos is None:
            at_pos = self.pos

        for a in self.map.find_all_within_r(self,Alertable,self.audible_radius):
            a.alert(at_pos)

