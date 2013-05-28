#!/usr/bin/env python3

import libtcodpy as libtcod
from monsters import Monster, Player, Dalek
from interfaces import Mappable, Position
from items import Item

class Tile:
    pass

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
        occupied = map( lambda o: o.pos, self.__layers[Player] + self.__layers[Monster] )
        rng = self.rng
        if from_map_seed:
            rng = self.map_rng
        while 1:
            p = Position(libtcod.random_get_int(rng,1,self.size.x),libtcod.random_get_int(rng,1,self.size.y))
            if not p in occupied:
                return p

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
        self.player = Player(self.find_random_clear(True))
        self.add(self.player)

        for i in range(1,10):
            d = Dalek(self.find_random_clear(True))
            self.add(d)

