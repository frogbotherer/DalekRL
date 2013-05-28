#!/usr/bin/env python3

import libtcodpy as libtcod
from monsters import Monster, Player, Dalek
from interfaces import Mappable, Position


class Tile:
    pass
class Item:
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
        self.rng = libtcod.random_new_from_seed(seed)
        self.size = size

        
    def add(self, obj, layer=None):
        """add object to map layer"""
        assert isinstance(obj,Mappable), "%s cannot appear on map"%obj
        if layer is None:
            for l in self.__layer_order:
                if isinstance(obj, l):
                    layer = l
        assert layer in self.__layer_order, "No such map layer %s"%layer

        self.__layers[layer].append(obj)
        obj.map = self

    def find_nearest(self, obj, layer):
        """find nearest thing in layer to obj"""
        r = 10000000 # safely larger than the map
        ro = None
        for o in self.__layers[layer]:
            if obj is o:
                continue
            d = obj.pos.distance_to(o.pos)
            if d<r:
                r  = d
                ro = o
        return ro

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
        self.player = Player(Position(10,10))
        self.add(self.player)

        mpos = []
        while len(mpos)<10:
            p = Position(libtcod.random_get_int(self.rng,1,self.size.x),libtcod.random_get_int(self.rng,1,self.size.y))
            if not p in mpos:
                mpos.append(p)
                self.add(Dalek(p))

