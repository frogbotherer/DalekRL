#!/usr/bin/env python3

import libtcodpy as libtcod

from monsters import Monster, Player, Dalek, Stairs
from interfaces import Mappable, Position, Traversable
from items import Item
from tiles import Tile, Wall, Floor

class Map:
    __layer_order = [Tile,Item,Monster,Player]

    def __init__(self, seed, size):
        self.player = None
        self.monsters = []
        self.items = []
        self.__layers = {
            Player: [],
            Monster: self.monsters,
            Item: self.items,
            Tile: [],
            }
        self.map_rng = libtcod.random_new_from_seed(seed)
        self.rng = libtcod.random_get_instance()
        self.size = size
        self.__tcod_map = libtcod.map_new( self.size.x, self.size.y )
        self.__tcod_pathfinder = None
        
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
            if not p in occupied and not self.is_blocked(p):
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
            # can't traverse an empty space and objects that don't implement Traversable
            return 0.0

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

    def recalculate_paths(self):
        libtcod.map_clear(self.__tcod_map)
        for o in self.__layers[Tile]:
            if isinstance(o,Traversable) and o.walk_cost>0.0:
                libtcod.map_set_properties(self.__tcod_map,o.pos.x,o.pos.y,True,not o.blocks_movement())
        #self.__tcod_pathfinder = libtcod.path_new_using_map(self.__tcod_map)
        self.__tcod_pathfinder = libtcod.dijkstra_new(self.__tcod_map)

    def get_path(self,from_pos,to_pos,steps=None):
        """gets array of Position objects from from_pos to to_pos. set steps to limit number of objects to return"""
        #libtcod.path_compute(self.__tcod_pathfinder,from_pos.x,from_pos.y,to_pos.x,to_pos.y)
        # TODO: can i compute one of these for each cell on the map and cache the results, indexed by pos?
        libtcod.dijkstra_compute(self.__tcod_pathfinder,from_pos.x,from_pos.y)
        libtcod.dijkstra_path_set(self.__tcod_pathfinder,to_pos.x,to_pos.y)

        if steps is None:
            steps = libtcod.dijkstra_size(self.__tcod_pathfinder)

        p = []
        for i in range(steps):
            x,y = libtcod.dijkstra_get(self.__tcod_pathfinder,i)
            p.append(Position(x,y))

        return p

    def __del__(self):
        #libtcod.path_delete(self.__tcod_pathfinder)
        libtcod.dijkstra_delete(self.__tcod_pathfinder)

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

        # put floor in
        # put an impassable box in the middle
        for i in range(1,self.size.x-1):
            for j in range(1,self.size.y-1):
                if i in range(self.size.x//4,self.size.x*3//4+1) and j in range(self.size.y//4,self.size.y*3//4+1):
                    if i in (self.size.x//4,self.size.x*3//4) or j in (self.size.y//4,self.size.y*3//4):
                        self.add(Wall(Position(i,j)))
                    else:
                        pass
                else:
                    self.add(Floor(Position(i,j)))

        # place stairs
        self.add(Stairs(self.find_random_clear(True)))

        # place player
        self.player = Player(self.find_random_clear(True))
        self.add(self.player)

        # place daleks
        for i in range(0,10):
            d = Dalek(self.find_random_clear(True))
            self.add(d)

        # calculate path information
        self.recalculate_paths()
