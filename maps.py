#!/usr/bin/env python3

import libtcodpy as libtcod

from monsters import Monster, Player, Stairs
from interfaces import Mappable, Position, Traversable, Transparent
from items import Item
from tiles import Tile, Wall, Floor
from errors import TodoError

from functools import reduce

class Map:
    __layer_order = [Tile,Item,Monster,Player]

    def __init__(self, seed, size):
        self.player = None
        self.__layers = {
            Player: {},
            Monster: {},
            Item: {},
            Tile: {},
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
        self.__layers[layer].setdefault(obj.pos,[]).append(obj)
        obj.map = self

    def remove(self, obj, layer=None):
        """remove object from map layer"""
        assert isinstance(obj,Mappable), "%s cannot appear on map"%obj
        if layer is None:
            layer = self.__get_layer_from_obj(obj)

        assert obj.pos in self.__layers[layer].keys(), "%s not found at %s in layer %s"%(obj,obj.pos,layer)

        self.__layers[layer][obj.pos].remove(obj)
        obj.map = None

    def move(self, obj, pos, layer=None):
        """move object on map. NB. setting a Mappable's pos directly will break stuff"""
        assert isinstance(obj,Mappable), "%s cannot appear on map"%obj
        if layer is None:
            layer = self.__get_layer_from_obj(obj)

        assert obj.pos in self.__layers[layer].keys(), "%s not found at %s in layer %s"%(obj,obj.pos,layer)

        # move obj reference
        self.__layers[layer][obj.pos].remove(obj)
        self.__layers[layer].setdefault(pos,[]).append(obj)

        # update obj position
        obj.pos = pos

    def find_nearest(self, obj, layer):
        """find nearest thing in layer to obj"""
        r = 10000000 # safely larger than the map
        ro = None
        for ol in self.__layers[layer].values():
            for o in ol:
                if obj is o or not obj.is_visible:
                    continue
                d = obj.pos.distance_to(o.pos)
                if d<r:
                    r  = d
                    ro = o
        return ro

    def find_random_clear(self,rng=None):
        """find random clear cell in map"""
        if rng is None:
            rng = self.rng
        occupied = list(self.__layers[Player].keys()) + list(self.__layers[Monster].keys()) \
                 + [t[0] for t in self.__layers[Tile].items() if t[1][0].blocks_movement()]

        while 1:
            p = Position(libtcod.random_get_int(rng,0,self.size.x-1),libtcod.random_get_int(rng,0,self.size.y-1))
            if not p in occupied and not self.is_blocked(p):
                return p

    def find_at_pos(self, pos, layer=None):
        layers = [layer]
        if layer is None:
            layers = self.__layer_order

        for l in layers:
            if pos in self.__layers[l].keys():
                return self.__layers[l][pos][0]

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
            for d in self.__layers[layer].values():
                for o in d:
                    o.draw()

    def recalculate_paths(self):
        libtcod.map_clear(self.__tcod_map)
        for ol in self.__layers[Tile].values():
            for o in ol:
                is_walkable = (isinstance(o,Traversable) and not o.blocks_movement())
                is_transparent = (isinstance(o,Transparent) and not o.blocks_light())
                libtcod.map_set_properties(self.__tcod_map,o.pos.x,o.pos.y,is_transparent,is_walkable)
        #self.__tcod_pathfinder = libtcod.path_new_using_map(self.__tcod_map)
        self.__tcod_pathfinder = libtcod.dijkstra_new(self.__tcod_map)

    def prepare_fov(self, pos, radius=0):
        libtcod.map_compute_fov(self.__tcod_map, pos.x, pos.y, radius, True, libtcod.FOV_BASIC)

    def can_see(self, pos):
        return libtcod.map_is_in_fov(self.__tcod_map, pos.x, pos.y)

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

    def get_monsters(self):
        return reduce( lambda a,b: a+b, self.__layers[Monster].values(), [] )

    def get_items(self):
        return reduce( lambda a,b: a+b, self.__layers[Item].values(), [] )

    def generate(self):
        raise NotImplementedError

    def _gen_draw_map_edges(self):
        # place map edges
        for i in range(0,self.size.x):
            self.add(Wall(Position(i,0)))
            self.add(Wall(Position(i,self.size.y-1)))
        for i in range(1,self.size.y-1):
            self.add(Wall(Position(0,i)))
            self.add(Wall(Position(self.size.x-1,i)))

    def _gen_add_key_elements(self):
        # place stairs
        self.add(Stairs(self.find_random_clear(self.map_rng)))

        # place player
        self.player = Player(self.find_random_clear(self.map_rng))
        self.add(self.player)

    def _gen_finish(self):
        # calculate path information
        self.recalculate_paths()

        # calculate player's initial fov
        self.prepare_fov(self.player.pos)

    def random(seed,size):
        print(" -- MAP SEED %d --" %seed)
        #return EmptyMap(seed,size)
        #return DalekMap(seed,size)
        return TypeAMap(seed,size)

class EmptyMap(Map):
    def generate(self):
        self._gen_draw_map_edges()

        # fill with floor
        for i in range(1,self.size.x-1):
            for j in range(1,self.size.y-1):
                self.add(Floor(Position(i,j)))

        # place daleks
        for i in range(0,20):
            d = Monster.random(self.map_rng,self.find_random_clear(self.map_rng))
            self.add(d)

        # place some items
        for i in range(0,3):
            i = Item.random(self.map_rng,self.find_random_clear(self.map_rng))
            self.add(i)

        self._gen_add_key_elements()
        self._gen_finish()


class DalekMap(Map):

    def generate(self):
        self._gen_draw_map_edges()

        # put floor in
        # put a randomly-sized impassable box in the middle
        left_x   = int(libtcod.random_get_float(self.map_rng,0.1,0.4)*self.size.x)
        right_x  = int(libtcod.random_get_float(self.map_rng,0.6,0.9)*self.size.x)
        top_y    = int(libtcod.random_get_float(self.map_rng,0.1,0.4)*self.size.y)
        bottom_y = int(libtcod.random_get_float(self.map_rng,0.6,0.9)*self.size.y)
        for i in range(1,self.size.x-1):
            for j in range(1,self.size.y-1):
                if i in range(left_x,right_x+1) and j in range(top_y,bottom_y+1):
                    if i in (left_x,right_x) or j in (top_y,bottom_y):
                        self.add(Wall(Position(i,j)))
                    else:
                        pass
                else:
                    self.add(Floor(Position(i,j)))

        # place daleks
        for i in range(0,10):
            d = Monster.random(self.map_rng,self.find_random_clear(self.map_rng))
            self.add(d)

        # place some items
        for i in range(0,3):
            i = Item.random(self.map_rng,self.find_random_clear(self.map_rng))
            self.add(i)

        self._gen_add_key_elements()
        self._gen_finish()


class TypeAMap(Map):
    """Map Layout:
     * corridors of 1 and 2 tile width
     * adjoining rooms with multiple exits and interconnects
     * sub-partitioned rooms
     * 80-90% of map space used
    """

    EMPTY    = 0x0
    CORRIDOR = 0x1
    ROOM     = 0x2
    WALL     = 0x4
    DOOR     = 0x8

    COMPASS = { 'N': {'opposite':'S','clockwise':'E','anticlockwise':'W','adjacent':['W','E']},
                'S': {'opposite':'N','clockwise':'W','anticlockwise':'E','adjacent':['W','E']},
                'E': {'opposite':'W','clockwise':'S','anticlockwise':'N','adjacent':['N','S']},
                'W': {'opposite':'E','clockwise':'N','anticlockwise':'S','adjacent':['N','S']},
                }

    CORRIDOR_MAX_BENDS  = 4
    CORRIDOR_LENGTH_VAR = [0.8,1.3]
    CORRIDOR_MAX_MINOR  = 6
    CORRIDOR_MINOR_LEN  = 60
    CORRIDOR_MINOR_BEND = 1
    CORRIDOR_MINOR_FREQ = 6
    CORRIDOR_MINOR_STEP = 4
    CORRIDOR_MIN_LENGTH = 5
    SANITY_LIMIT        = 100

    def __init__(self, seed, size):
        Map.__init__(self, seed, size)
        self._map = [ [0 for y in range(size.y)] for x in range(size.x) ]

    class _ME:
        def __init__(self,tile_id,pos,size,opos=None,direction=None,length=None):
            if not isinstance(pos,Position):
                pos = Position(pos)
            if not isinstance(size,Position):
                size = Position(size)
            self.tile_id = tile_id
            self.pos = pos
            self.size = size
            # for corridors
            self.opos = opos
            self.direction = direction
            self.length = length

        def __str__(self):
            return "Internal map element %d at %s, size %s. pos=%s, dir=%s, len=%d"%(self.tile_id,self.pos,self.size,self.opos,self.direction,self.length)

        def commit(self,m):
            assert self.pos.x+self.size.x < len(m) and self.pos.y+self.size.y < len(m[0]), "Can't commit %s to grid size (%d,%d)"%(self,len(m),len(m[0]))
            for x in range(self.size.x):
                for y in range(self.size.y):
                    m[x+self.pos.x][y+self.pos.y] = self.tile_id

    def _gen_get_compass_dir(self):
        return ['N','S','E','W'][ libtcod.random_get_int(self.map_rng,0,3) ]
    def _gen_get_compass_turn(self,current_direction):
        return TypeAMap.COMPASS[current_direction]['adjacent'][ libtcod.random_get_int(self.map_rng,0,1) ]
    def _gen_get_compass_opposite(self,current_direction):
        return TypeAMap.COMPASS[current_direction]['opposite']

    def _gen_get_dir_to_closest_edge(self,pos):
        half_x = self.size.x//2
        half_y = self.size.y//2
        if pos.x < half_x:
            if pos.y < half_y:
                # NW quad
                if pos.x > pos.y:
                    return 'N'
                else:
                    return 'W'
            else:
                # SW quad
                if pos.x > self.size.y-pos.y:
                    return 'S'
                else:
                    return 'W'
        else:
            if pos.y < half_y:
                # NE quad
                if self.size.x-pos.x > pos.y:
                    return 'N'
                else:
                    return 'E'
            else:
                # SE quad
                if pos.x > pos.y:
                    return 'E'
                else:
                    return 'S'
    def _gen_get_dir_to_furthest_edge(self,pos):
        return self._gen_compass_get_opposite( self._gen_get_dir_and_dist_to_closest_edge(self,pos) )

    def _gen_get_available_dist(self,pos,direction):
        if   direction == 'N':
            return pos.y
        elif direction == 'S':
            return self.size.y-pos.y
        elif direction == 'E':
            return self.size.x-pos.x
        elif direction == 'W':
            return pos.x
        else:
            assert False, "_gen_get_available_dist called with bad direction %s"%direction

    def _gen_pos_from_dir(self, direction, distance):
        if   direction == 'N':
            return Position(0,-distance)
        elif direction == 'S':
            return Position(0,distance)
        elif direction == 'E':
            return Position(distance,0)
        elif direction == 'W':
            return Position(-distance,0)
        else:
            assert False, "_gen_pos_from_dir called with bad direction %s" % direction

    def _gen_dir_from_pos(self, pos_from, pos_to=None):
        if pos_to is None:
            pos_to = self.map.size
        v = pos_to - pos_from

        length = abs(v.x)
        direction = 'E'
        if v.x < 0:
            direction = 'W'
        if abs(v.y) > abs(v.x):
            length = abs(v.y)
            direction = 'S'
            if v.y < 0:
                direction = 'N'

        return (direction,length)

    def _gen_get_edge_tile(self, edge, border_min=0, border_max=2):
        """Random unoccupied Position() within <border_min/_max> tiles of map edge <edge>"""
        if   edge == 'N':
            return Position( libtcod.random_get_int(self.map_rng,border_min,self.size.x-border_min), libtcod.random_get_int(self.map_rng,border_min,border_max) )
        elif edge == 'S':
            return Position( libtcod.random_get_int(self.map_rng,border_min,self.size.x-border_min), self.size.y-libtcod.random_get_int(self.map_rng,border_min,border_max) )
        elif edge == 'W':
            return Position( libtcod.random_get_int(self.map_rng,border_min,border_max), libtcod.random_get_int(self.map_rng,border_min,self.size.y-border_min) )
        elif edge == 'E':
            return Position( self.size.x-libtcod.random_get_int(self.map_rng,border_min,border_max), libtcod.random_get_int(self.map_rng,border_min,self.size.y-border_min) )
        else:
            assert False, "_gen_get_edge_tile called with invalid edge %s" % edge

    def _gen_corridor_seg(self, opos, direction, length, width=1):
        size = None
        pos  = Position(opos.x,opos.y)
        if   direction == 'N':
            # adjust pos to top-left
            pos -= Position( 0, length-width )
            size = Position( width, length )
        elif direction == 'S':
            size = Position( width, length )
        elif direction == 'E':
            size = Position( length, width )
        elif direction == 'W':
            pos -= Position( length-width, 0 )
            size = Position( length, width )
        else:
            assert False, "_gen_corridor_seg called with invalid direction %s" % direction
        return self._ME(TypeAMap.CORRIDOR, pos, size, opos, direction, length)


    def _gen_corridor_to_area(self, pos, direction, edge, width, bendiness=3):
        c_segs = []
        curr_pos = pos
        num_bends = libtcod.random_get_int(self.map_rng, 2, bendiness)

        sanity = 0

        terminating_pos = self._gen_get_edge_tile(edge, self.CORRIDOR_MIN_LENGTH+width+1, self.CORRIDOR_MIN_LENGTH+width+6)
        while curr_pos.distance_to(terminating_pos) < self.CORRIDOR_MIN_LENGTH*5:
            sanity += 1
            if sanity > self.SANITY_LIMIT:
                break
            terminating_pos = self._gen_get_edge_tile(edge, self.CORRIDOR_MIN_LENGTH+width+1, self.CORRIDOR_MIN_LENGTH+width+6)

        while num_bends > 0 and curr_pos.distance_to(terminating_pos) > width+1:
            if   num_bends == 1:
                # get as close to terminating pos as possible
                d, l = self._gen_dir_from_pos( curr_pos, terminating_pos )
                c_segs.append( self._gen_corridor_seg( curr_pos, d, l, width ) )
                print("Bend 1 (last): pos %s, target %s, dir %s, len %d"%(curr_pos,terminating_pos,d,l))

            elif num_bends == 2:
                # get on same long or lat as terminating pos
                v = terminating_pos - curr_pos
                l = abs(v.x)
                if direction in ['N','S']:
                    l = abs(v.y)
                if l > self._gen_get_available_dist(curr_pos,direction):
                    direction = self._gen_get_compass_opposite(direction)
                if l > self._gen_get_available_dist(curr_pos,direction): # still!
                    l = self._gen_get_available_dist(curr_pos,direction) - self.CORRIDOR_MIN_LENGTH - width
                c_segs.append( self._gen_corridor_seg( curr_pos, direction, l, width ) )
                print("Bend 2 (pen.): pos %s, target %s, dir %s, len %d"%(curr_pos,terminating_pos,direction,l))

            else:
                # travel random distance in current direction, then turn
                c_segs.append( self._gen_corridor_seg( curr_pos, direction, libtcod.random_get_int(self.map_rng,self.CORRIDOR_MIN_LENGTH+width+1,self._gen_get_available_dist(curr_pos,direction)-self.CORRIDOR_MIN_LENGTH-width), width ) )
                print("Bend >2 (first): pos %s, target %s, dir %s, len %d"%(curr_pos,terminating_pos,direction,c_segs[-1].length))
                direction = self._gen_get_compass_turn(direction)
            num_bends -= 1
            curr_pos += self._gen_pos_from_dir( c_segs[-1].direction, c_segs[-1].length-1 )
            # correct for N/W fencepost problem
            if   c_segs[-1].direction == 'N':
                curr_pos -= (0,width-1)
            elif c_segs[-1].direction == 'W':
                curr_pos -= (width-1,0)

        return c_segs

    def _gen_corridor_wriggle(self, pos, direction, length, width, bendiness):
        c_segs    = []
        len_used  = 0
        curr_pos  = pos
        num_bends = libtcod.random_get_int(self.map_rng, 0, bendiness)

        sanity = 0
        while len_used < length:
            sanity += 1
            if sanity > self.SANITY_LIMIT:
                #assert False, "sanity hit whilst routing corridor"
                break
            len_wanted = int(libtcod.random_get_float(self.map_rng,self.CORRIDOR_LENGTH_VAR[0],self.CORRIDOR_LENGTH_VAR[1]) * (length)/(1+num_bends))
            if len_wanted + len_used > length:
                len_wanted = length - len_used
            if len_wanted < self.CORRIDOR_MIN_LENGTH:
                len_wanted = self.CORRIDOR_MIN_LENGTH
            len_avail = self._gen_get_available_dist(curr_pos,direction)

            if len_avail > len_wanted+1:
                s = self._gen_corridor_seg( curr_pos, direction, len_wanted, width )
                c_segs.append( s )
                len_used += len_wanted
                curr_pos += self._gen_pos_from_dir( direction, len_wanted-1 )
                print("iter: %d; pos: %s; dir: %s; used: %d; wanted %d; avail: %d"%(sanity,curr_pos,direction,len_used,len_wanted,len_avail))
                # correct for N/W fencepost problem
                if   direction == 'N':
                    curr_pos -= (0,width-1)
                elif direction == 'W':
                    curr_pos -= (width-1,0)

            # turn towards area with space to draw what we want
            direction = self._gen_get_compass_turn( direction )
            o = self._gen_get_compass_opposite( direction )
            #if self._gen_get_available_dist( curr_pos, direction ) < self._gen_get_available_dist( curr_pos, o ):
            if self._gen_get_available_dist( curr_pos, direction ) < self.CORRIDOR_MIN_LENGTH+width+1:
                direction = o

        return c_segs

    def generate(self):
        self._gen_draw_map_edges()
        # * corridors and rooms include just walkable tiles
        corridors = []
        rooms = []
        # * route one corridor across most of map
        #    * choose random site near one edge of map
        #    * choose random site near far edge of map
        #    * choose corridor width
        #    * choose number of corridor bends (1-4, depending on sites)
        #    * plot corridor
        print (" -- MAIN CORRIDOR --")
        d = self._gen_get_compass_dir()
        o = self._gen_get_compass_opposite(d)
        corridors += self._gen_corridor_to_area( self._gen_get_edge_tile( o, 1, 4 ),
                                         d,
                                         o,
                                         2,
                                         self.CORRIDOR_MAX_BENDS )

        # * calculate allowance for intersecting corridors (1-5)
        # * consume allowance: 1 for 1 tile width; 2 for 2 tile width, multiplied by 1 for short corridor, 2 for long
        #    * choose random length and termination points
        #    * choose random number of bends
        #    * plot corridor
#        main_corridor_marker = len(corridors)-1
#        for i in range(main_corridor_marker+1):
#            c = corridors[i]
#            # * choose random intersect on each segment of main corridor
#            print(" -- INTERSECTING CORRIDOR %d (FROM SEG %d) -- "%(i,corridors.index(c)))
#            intersect = c.opos + self._gen_pos_from_dir( c.direction, libtcod.random_get_int(self.map_rng,0,c.length-1) )
#            d = self._gen_get_compass_turn(c.direction)
#            corridors += self._gen_corridor_wriggle( intersect,
#                                             d,
#                                             libtcod.random_get_int(self.map_rng,self.CORRIDOR_MINOR_LEN//2,self.CORRIDOR_MINOR_LEN),
#                                             1,
#                                             self.CORRIDOR_MINOR_BEND )
#            intersect = c.opos + self._gen_pos_from_dir( c.direction, libtcod.random_get_int(self.map_rng,0,c.length-1) )
#            d = self._gen_get_compass_opposite(d)
#            corridors += self._gen_corridor_wriggle( intersect,
#                                             d,
#                                             libtcod.random_get_int(self.map_rng,self.CORRIDOR_MINOR_LEN//2,self.CORRIDOR_MINOR_LEN),
#                                             1,
#                                             self.CORRIDOR_MINOR_BEND )
        main_len = reduce(lambda a,b: a+b.length,corridors,0)
        used_len = 0; index_len = 0
        c_idx = 0
        sanity = 0
        while used_len < main_len:
            sanity += 1
            if sanity > self.SANITY_LIMIT:
                assert False, "broke sanity trying to add wriggle corridors"
                break
            delta_len = libtcod.random_get_int(self.map_rng,0,self.CORRIDOR_MINOR_FREQ)*self.CORRIDOR_MINOR_STEP
            index_len += delta_len
            while index_len > corridors[c_idx].length:
                index_len -= corridors[c_idx].length
                c_idx += 1
                if c_idx == len(corridors):
                    # put wriggle corridor at end of last part of main
                    c_idx -= 1
                    index_len = corridors[c_idx].length
            c = corridors[c_idx]
            intersect = c.opos + self._gen_pos_from_dir( c.direction, index_len )
            d = self._gen_get_compass_turn(c.direction)
            print("%d/%d %d/%d from %s %s for %d = %s"%(used_len,main_len,index_len,c.length,c.opos,c.direction,index_len,intersect))

            corridors += self._gen_corridor_wriggle( intersect,
                                             d,
                                             libtcod.random_get_int(self.map_rng,self.CORRIDOR_MINOR_LEN//2,self.CORRIDOR_MINOR_LEN),
                                             1,
                                             self.CORRIDOR_MINOR_BEND )

            used_len += delta_len

        # * commit corridors to map
        for c in corridors:
            c.commit(self._map)
        # * for each remaining unplotted tile
        #    * calculate largest square that can be made without overlapping a corridor+1 tile
        #    * if square size > threshold or (>0 and random chance):
        #       * if square overlaps another one
        #          * if this square size > that square size
        #             * remove that square
        #          * else continue
        #       * save square
        # [* may need to repeat this loop 2-3 times, making squares permanent at each point]
        # * for each square larger than threshold:
        #    * if random chance succeeds:
        #        * sub-divide with partitions
        # * create doors at intersects
        # * use pathing to prove map traversable
        # * populate Map object from _map
        for x in range(1,len(self._map)-1):
            for y in range(1,len(self._map[0])-1):
                t = self._map[x][y]
                if   t & self.CORRIDOR:
                    self.add(Floor(Position(x,y)))
                elif t & self.ROOM:
                    raise TodoError
                elif t & self.WALL:
                    self.add(Wall(Position(x,y)))
                elif t & self.DOOR:
                    raise TodoError
                elif t == 0:
                    # * if tile adjoins one walkable tile, it is a wall tile
                    if self._map[x-1][y-1] > 0 or \
                       self._map[x][y-1] > 0 or \
                       self._map[x+1][y-1] > 0 or \
                       self._map[x-1][y] > 0 or \
                       self._map[x][y] > 0 or \
                       self._map[x+1][y] > 0 or \
                       self._map[x-1][y+1] > 0 or \
                       self._map[x][y+1] > 0 or \
                       self._map[x+1][y+1] > 0:
                        self.add(Wall(Position(x,y)))
                else:
                    assert False, "Invalid _map data"



        #####  PSEUDO-CODE  #########################################
        # * corridors and rooms include just walkable tiles
        # * route one corridor across most of map
        #    * choose random site near one edge of map
        #    * choose random site near far edge of map
        #    * choose corridor width
        #    * choose number of corridor bends (1-4, depending on sites)
        #    * plot corridor
        # * calculate allowance for intersecting corridors (1-5)
        # * consume allowance: 1 for 1 tile width; 2 for 2 tile width, multiplied by 1 for short corridor, 2 for long
        #    * choose random intersect on main corridor
        #    * choose random length and termination points
        #    * choose random number of bends
        #    * plot corridor
        # * for each remaining unplotted tile
        #    * calculate largest square that can be made without overlapping a corridor+1 tile
        #    * if square size > threshold or (>0 and random chance):
        #       * if square overlaps another one
        #          * if this square size > that square size
        #             * remove that square
        #          * else continue
        #       * save square
        # [* may need to repeat this loop 2-3 times, making squares permanent at each point]
        # * for each square larger than threshold:
        #    * if random chance succeeds:
        #        * sub-divide with partitions
        # * create doors at intersects
        # * use pathing to prove map traversable
        # * for tile in empty tiles:
        #    * if tile adjoins one walkable tile, it is a wall tile

        # place daleks
        for i in range(0,8):
            d = Monster.random(self.map_rng,self.find_random_clear(self.map_rng))
            self.add(d)

        # place some items
        for i in range(0,4):
            i = Item.random(self.map_rng,self.find_random_clear(self.map_rng))
            self.add(i)

        self._gen_add_key_elements()
        self._gen_finish()

class TypeBMap(Map):
    """Map
     * use B-tree algorithm to create cell-shaped rooms with 1 tile gap between them
     * populate gaps with corridors
     * spawn doors
    """
    pass
