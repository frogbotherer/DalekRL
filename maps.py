#!/usr/bin/env python3

import libtcodpy as libtcod

from monsters import Monster, Player, Dalek, Stairs
from interfaces import Mappable, Position, Traversable
from items import Item
from tiles import Tile, Wall

class Map:
    __layer_order = [Tile,Item,Monster,Player]

    def __init__(self, seed, size):
        self.player = None
        self.monsters = []
        self.__layers = {
            Player: [],
            Monster: self.monsters,
            Item: [],
            Tile: []
            }
        self.map_rng = libtcod.random_new_from_seed(seed)
        self.rng = libtcod.random_get_instance()
        self.size = size

        
    def __get_layer_from_obj(self, obj):
        for l in self.__layer_order:
            if isinstance(obj, l):
                return l
        assert False, "No map layer for %s"%obj

    def add(self, obj, layer=None):
        """add object to map layer"""
        assert isinstance(obj,Mappable), "%s cannot appear on map"%obj
        if layer is None:
            layer = self.__get_layer_from_obj(obj)
        self.__layers[layer].append(obj)
        obj.map = self

    def remove(self, obj, layer=None):
        """remove object from map layer"""
        assert isinstance(obj,Mappable), "%s cannot appear on map"%obj
        if layer is None:
            layer = self.__get_layer_from_obj(obj)
        self.__layers[layer].remove(obj)
        obj.map = None

    def find_nearest(self, obj, layer):
        """find nearest thing in layer to obj"""
        r = 10000000 # safely larger than the map
        ro = None
        for o in self.__layers[layer]:
            if obj is o or not obj.is_visible:
                continue
            d = obj.pos.distance_to(o.pos)
            if d<r:
                r  = d
                ro = o
        return ro

    def find_random_clear(self,from_map_seed=False):
        """find random clear cell in map"""
        occupied = map( lambda o: o.pos, 
                        self.__layers[Player]
                         + self.__layers[Monster]
                         + list(filter(lambda t: t.blocks_movement(), self.__layers[Tile]))
                        )
        rng = self.rng
        if from_map_seed:
            rng = self.map_rng
        while 1:
            p = Position(libtcod.random_get_int(rng,0,self.size.x-1),libtcod.random_get_int(rng,0,self.size.y-1))
            if not p in occupied:
                return p

    def find_at_pos(self, pos, layer=None):
        # TODO: this is stunningly inefficient; the map should be keyed by position
        layers = [layer]
        if layer is None:
            layers = self.__layer_order
        for l in layers:
            for o in self.__layers[l]:
                if o.pos == pos:
                    return o
        return None

    def get_walk_cost(self, pos):
        obj = self.find_at_pos(pos,Tile)
        if isinstance(obj,Traversable):
            return obj.walk_cost
        else:
            # can traverse an empty space and objects that don't implement Traversable
            return 1.0

    def is_blocked(self, pos):
        return self.get_walk_cost(pos) == 0.0

    def draw(self):
        """draw the map"""
        for layer in self.__layer_order:
            for d in self.__layers[layer]:
                d.draw()

    def cls(self):
        """clear the map"""
        for layer in self.__layer_order:
            for d in self.__layers[layer]:
                d.clear()


    def generate(self):
        raise NotImplementedError



class DalekMap(Map):

    def generate(self):
        # place map edges
        for i in range(0,self.size.x):
            self.add(Wall(Position(i,0)))
            self.add(Wall(Position(i,self.size.y-1)))
        for i in range(1,self.size.y-1):
            self.add(Wall(Position(0,i)))
            self.add(Wall(Position(self.size.x-1,i)))

        # place stairs
        self.add(Stairs(self.find_random_clear(True)))

        # place player
        self.player = Player(self.find_random_clear(True))
        self.add(self.player)

        # place daleks
        for i in range(1,10):
            d = Dalek(self.find_random_clear(True))
            self.add(d)

