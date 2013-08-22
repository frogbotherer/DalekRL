#!/usr/bin/env python3
"""Contains mixins and base classes for other parts of game"""

import libtcodpy as libtcod
from math import hypot, atan2, pi
import weakref

from errors import InvalidMoveContinueError
from ui import Message


class Position:
    """Utility class for managing Cartesian coordinates"""
    def __init__(self, x, y=None):
        """Initialise as Position(x,y), or Position((x,y)), Position(Position(x,y))"""
        if y is None:
            if isinstance(x, tuple) or isinstance(x, list):
                y = x[1]
                x = x[0]
            elif isinstance(x, Position):
                y = x.y
                x = x.x
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        if isinstance(other, tuple):
            return Position(self.x + other[0], self.y + other[1])
        else:
            return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if isinstance(other, tuple):
            return Position(self.x - other[0], self.y - other[1])
        else:
            return Position(self.x - other.x, self.y - other.y)

    def __gt__(self, other):
        """self > other if other would be enclosed in a box from (0,0) to self"""
        if not isinstance(other, Position):
            other = Position(other)
        #return (self.x*self.y>other.x*other.y) or (self.y==other.y and self.x>other.x)
        return (self.x > other.x and self.y > other.y)

    def __ge__(self, other):
        """self >= other if other would be enclosed in a box from (0,0) to self, including border"""
        if not isinstance(other, Position):
            other = Position(other)
        #return (self.x*self.y>other.x*other.y) or (self.y==other.y and self.x>=other.x)
        return (self.x >= other.x and self.y >= other.y)

    def __lt__(self, other):
        if not isinstance(other, Position):
            other = Position(other)
        #return (self.x*self.y<other.x*other.y) or (self.y==other.y and self.x<other.x)
        return (self.x < other.x and self.y < other.y)

    def __le__(self, other):
        if not isinstance(other, Position):
            other = Position(other)
        #return (self.x*self.y<other.x*other.y) or (self.y==other.y and self.x<=other.x)
        return (self.x <= other.x and self.y <= other.y)

    def __eq__(self, other):
        if not isinstance(other, Position):
            other = Position(other)
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "Position(%d,%d)" % (self.x, self.y)

    def __str__(self):
        return "(%d,%d)" % (self.x, self.y)

    def distance_to(self, other):
        """returns distance to other"""
        if not isinstance(other, Position):
            other = Position(other)
        return hypot(self.x - other.x, self.y - other.y)

    def angle_to(self, other):
        """returns angle in radians/pi between self and other. i.e. 0.0 => matching directions; 1.0 => opposites"""
        if not isinstance(other, Position):
            other = Position(other)
        t = (atan2(self.x, self.y) - atan2(other.x, other.y)) / pi
        if t > 1.0:
            t -= 2.0
        elif t < -1.0:
            t += 2.0
        return abs(t)


class Mappable:
    """Can appear on the map"""
    UNSEEN_COLOUR = libtcod.darkest_grey
    LIGHT_L_CLAMP = libtcod.darkest_grey
    LIGHT_H_CLAMP = libtcod.white
    LIGHT_VISIBLE = libtcod.dark_grey

    def __init__(self, pos, symbol, colour, remains_in_place=False, unseen_symbol=None, unseen_colour=UNSEEN_COLOUR):
        self.map = None
        self.pos = pos
        self.last_pos = pos
        self.symbol = symbol
        self.colour = colour
        self.remains_in_place = remains_in_place

        self.is_visible = True
        self.has_been_seen = False
        self.visible_to_player = False

        self.unseen_symbol = (unseen_symbol is None) and self.symbol or unseen_symbol
        self.unseen_colour = unseen_colour

    ##
    # movement
    def move(self, delta):
        """move by a delta"""
        return self.move_to(self.pos + delta)

    def move_to(self, pos):
        """move by an absolute"""
        assert not self.remains_in_place, "trying to move immovable object %s" % self
        ## test whether movement is valid # this lives in map.move now
        #if not self.map is None and self.map.is_blocked(pos):
        #    raise InvalidMoveError( "Can't move %s to %s"%(self,pos) )
        assert not self.map is None, "Mappable %s not on map" % self
        return self.map.move(self, pos)

    ##
    # lighting
    @property
    def is_lit(self):
        """Is this map tile lit?"""
        if self.map is None or self.pos is None:
            return False
        else:
            return self.map.is_lit(self)

    @property
    def light_level(self):
        """Light level of this map tile (0.0-1.0ish?)"""
        if self.map is None or self.pos is None:
            return LightSource.INTENSITY_L_CLAMP
        else:
            return self.map.light_level(self.pos)

    @property
    def light_colour(self):
        """Colour (and intensity) of the light in this map tile"""
        if self.map is None or self.pos is None:
            return Mappable.LIGHT_L_CLAMP
        else:
            return self.map.light_colour(self.pos)

    ##
    # drawing
    def draw(self):
        """Draw this map tile"""
        # NB. this gets called a lot!
        if not self.is_visible:
            return

        if self.visible_to_player:
            if self.map.player.has_effect(StatusEffect.INFRAVISION) and not self.remains_in_place:
                c = libtcod.white
            else:
                c = self.light_colour        # this is slow
            l = libtcod.color_get_hsv(c)[2]  # this is copied from .light_level for performance
            if self.map.player.has_effect(StatusEffect.NIGHT_VISION):
                l = 1.0 - l
                c = libtcod.white - c
            if l > LightSource.INTENSITY_L_CLAMP:
                colour = self.colour * c
                symbol = self.symbol
            else:
                if self.has_been_seen and self.remains_in_place:
                    colour = self.unseen_colour
                    symbol = self.unseen_symbol
                else:
                    return
        else:
            if self.has_been_seen and self.remains_in_place:
                colour = self.unseen_colour
                symbol = self.unseen_symbol
            else:
                return
        libtcod.console_put_char_ex(0, self.pos.x, self.pos.y, symbol, colour, libtcod.BKGND_NONE)
        self.has_been_seen = True


class LightSource(Mappable):
    """Light emitted from a single point"""
    INTENSITY_L_CLAMP = libtcod.color_get_hsv(Mappable.LIGHT_L_CLAMP)[2]
    INTENSITY_H_CLAMP = libtcod.color_get_hsv(Mappable.LIGHT_H_CLAMP)[2]
    INTENSITY_VISIBLE = libtcod.color_get_hsv(Mappable.LIGHT_VISIBLE)[2]

    def __init__(self, radius=0, intensity=1.0, light_colour=Mappable.LIGHT_H_CLAMP):
        self._radius            = radius == 0 and 100 or radius # TODO: more sensible behaviour for infinite r
        self.intensity          = intensity
        self.raw_light_colour   = light_colour
        self.light_enabled      = True
        self.__tcod_light_map   = libtcod.map_new(radius * 2 + 1, radius * 2 + 1)
        self.__tcod_light_image = libtcod.image_new(radius * 2 + 1, radius * 2 + 1)

    @property
    def radius(self):
        """Set light radius"""
        return self._radius

    @radius.setter
    def radius(self, r):
        """Change light radius"""
        if r == self._radius:
            return # because this is slow!
        e = self.light_enabled
        self.close()
        self.light_enabled      = e
        self._radius            = r
        self.__tcod_light_map   = libtcod.map_new(r * 2 + 1, r * 2 + 1)
        self.__tcod_light_image = libtcod.image_new(r * 2 + 1, r * 2 + 1)
        self.reset_map()

    def prepare_fov(self, light_walls=False):
        """Calculate light's distribution"""
        libtcod.map_compute_fov(self.__tcod_light_map,
                                self.radius + 1, self.radius + 1, self.radius,
                                light_walls, libtcod.FOV_BASIC)

    def reset_map(self, pos=None):
        """Reset light map.
        If pos is a list of Positions, only reset those areas"""
        if not self.light_enabled:
            libtcod.image_clear(self.__tcod_light_image, libtcod.black)
            libtcod.image_set_key_color(self.__tcod_light_image, libtcod.black)
            return
        assert not self.pos is None and not self.map is None, "resetting LightSource that is not placed on map"

        # [re-]calculating FOV of light within its map
        if pos is None:
            libtcod.map_clear(self.__tcod_light_map, False, False)
            cov = {}
            for o in self.map.find_all_within_r(self, Transparent, self.radius):
                # if there's something here already and it blocks light, light is blocked at pos
                if cov.get(o.pos, True):
                    cov[o.pos] = not o.blocks_light()

            for (p, is_transparent) in cov.items():
                # we're using the walkable bit to show that there is a tile that could be lit
                libtcod.map_set_properties(self.__tcod_light_map,
                                           self.radius + p.x - self.pos.x,
                                           self.radius + p.y - self.pos.y,
                                           is_transparent, True)

        else:
            if not isinstance(pos, list):
                pos = [pos]
            skip_calc = True
            for p in pos:
                if self.pos.distance_to(p) > self.radius:
                    # pos isn't covered by this light; do nothing
                    pass

                else:
                    skip_calc      = False
                    is_transparent = True
                    for o in self.map.find_all_at_pos(p):
                        if isinstance(o, Transparent) and o.blocks_light():
                            is_transparent = False
                            break
                    libtcod.map_set_properties(self.__tcod_light_map,
                                               self.radius + p.x - self.pos.x,
                                               self.radius + p.y - self.pos.y,
                                               is_transparent, True)

            if skip_calc:
                # all pos were outside of light radius!
                return

        self.prepare_fov(False) # TODO: calculate both True and False; use True only if light in LOS of player

        # use FOV data to create an image of light intensity, masked by opaque tiles
        # can optimise based on pos P: only need to recalculate area X
        #   ---        ---XX            ---        --XXX
        #  /   \      /   XX           /   \      /  XXX     do this by splitting into quarters
        # |    P|    |    PX          |     |    |   XXX     and working out which to recalculate
        # |  L  |    |  L  |          |  LP |    |  LPXX     based on P-L
        # |     |    |     |          |     |    |   XXX
        #  \   /      \   /            \   /      \  XXX
        #   ---        ---              ---        --XXX
        libtcod.image_clear(self.__tcod_light_image, libtcod.black)
        libtcod.image_set_key_color(self.__tcod_light_image, libtcod.black)
        r   = self.radius
        rd2 = r / 2
        i1  = self.raw_light_colour * self.intensity
        for x in range(r * 2 + 1):
            for y in range(r * 2 + 1):
                #print("(%d,%d)"%(x,y))
                if libtcod.map_is_in_fov(self.__tcod_light_map, x, y):
                    d = hypot(r - x, r - y)
                    if d > rd2:
                        libtcod.image_put_pixel(self.__tcod_light_image,
                                                x, y,
                                                i1 * (1.0 - (d - rd2) / rd2))
                        #print("  %s %s"%(d,i1*(1.0-(d-rd2)/rd2)))
                    else:
                        libtcod.image_put_pixel(self.__tcod_light_image,
                                                x, y,
                                                i1)
                        #print("  %s %s"%(d,i1))

    def blit_to(self, tcod_console, ox=0, oy=0, sx=-1, sy=-1):
        """Copy lighting information to libtcod console"""
        libtcod.image_blit_rect(self.__tcod_light_image, tcod_console,
                                self.pos.x + ox - self.radius,
                                self.pos.y + oy - self.radius,
                                #self.radius*2+1-ox, self.radius*2+1-oy,
                                sx, sy,
                                libtcod.BKGND_ADD)

    def lights(self, pos, test_los=True):
        """Does this light light pos?
        If test_los is False; don't bother checking line of sight"""
        if not self.light_enabled:
            return False
        if self.pos.distance_to(pos) > self.radius:
            return False
        if not test_los:
            return True

        #print("does %s light pos %s?"%(self,pos))
        #print("%d < %d" %(self.pos.distance_to(pos),self.radius))
        #print("%d,%d"%(1+self.radius+pos.x-self.pos.x,1+self.radius+pos.y-self.pos.y))

        return libtcod.map_is_in_fov(self.__tcod_light_map,
                                     self.radius + pos.x - self.pos.x,
                                     self.radius + pos.y - self.pos.y)

    def close(self):
        """Clean up lighting assets prior to deleting object"""
        libtcod.map_delete(self.__tcod_light_map)
        libtcod.image_delete(self.__tcod_light_image)
        self.light_enabled = False

    def __del__(self):
        """del light"""
        self.close()


class FlatLightSource(LightSource):
    """Even lighting covering square area"""
    def __init__(self, size, intensity=1.0, light_colour=Mappable.LIGHT_H_CLAMP):
        self._size              = size
        self.intensity          = intensity
        self.raw_light_colour   = light_colour
        self.light_enabled      = True
        self.__tcod_light_map   = libtcod.map_new(size.x + 2, size.y + 2)
        self.__tcod_light_image = libtcod.image_new(size.x + 2, size.y + 2)

    @property
    def radius(self):
        """Dummy radius"""
        return 0

    @radius.setter
    def radius(self, r):
        """Dummy radius"""
        pass

    @property
    def size(self):
        """Size of light, as a Position"""
        return self._size

    @size.setter
    def size(self, s):
        """Reset size of light"""
        if s == self._size:
            return
        self._size = s
        e = self.light_enabled
        self.close()
        self.light_enabled = e
        self.reset_map()

    def prepare_fov(self, light_walls=False):
        """Calculate light's distribution"""
        libtcod.map_compute_fov(self.__tcod_light_map,
                                self._size.x // 2,
                                self._size.y // 2,
                                max(self._size.x // 2, self._size.y // 2) + 1,
                                light_walls, libtcod.FOV_BASIC)

    def reset_map(self, pos=None):
        """Reset light map.
        If pos is a list of Positions, only reset those areas"""
        if self.light_enabled:
            assert not self.pos is None and not self.map is None, "resetting LightSource that is not placed on map"
            libtcod.image_clear(self.__tcod_light_image, self.raw_light_colour * self.intensity)
            libtcod.image_set_key_color(self.__tcod_light_image, libtcod.black)
        else:
            libtcod.image_clear(self.__tcod_light_image, libtcod.black)
            libtcod.image_set_key_color(self.__tcod_light_image, libtcod.black)

    def blit_to(self, tcod_console, ox=0, oy=0, sx=-1, sy=-1):
        """Copy lighting information to libtcod console"""
        libtcod.image_blit_rect(self.__tcod_light_image, tcod_console,
                                self.pos.x + ox - 1,
                                self.pos.y + oy - 1,
                                sx, sy,
                                libtcod.BKGND_ADD)

    def lights(self, pos, test_los=True):
        """Does this light light pos?
        If test_los is False; don't bother checking line of sight"""
        return self.light_enabled and pos >= self.pos - Position(1, 1) and pos <= self.pos + self._size + Position(1, 1)

    def close(self):
        libtcod.map_delete(self.__tcod_light_map)
        libtcod.image_delete(self.__tcod_light_image)

    def __del__(self):
        self.close()


class TurnTaker:
    """Mixin that provides a method call to take_turn() every turn"""
    turn_takers = []

    def __init__(self, initiative, start=True):
        """Lowest initiative goes first"""
        self.initiative = initiative
        if start:
            TurnTaker.add_turntaker(self)

    def take_turn(self):
        """Instance takes a turn."""
        raise NotImplementedError

    @staticmethod
    def take_all_turns():
        """All instances take a turn"""
        for tref in TurnTaker.turn_takers:
            t = tref()
            if t is None:
                TurnTaker.turn_takers.remove(tref)
            else:
                t.take_turn()

    @staticmethod
    def clear_all():
        """Clear all turn takers from list"""
        for tref in TurnTaker.turn_takers:
            t = tref()
            if not t is None:
                del t
        TurnTaker.turn_takers = []

    def refresh_turntaker(self):
        """Re-add turn taker to list if missing"""
        if not weakref.ref(self) in TurnTaker.turn_takers:
            TurnTaker.add_turntaker(self)

    @staticmethod
    def add_turntaker(t):
        """Add a turn taker to the list that take a turn each round"""
        # might be a faster way to do this
        TurnTaker.turn_takers.append(weakref.ref(t))
        TurnTaker.turn_takers.sort(key=lambda x: x() is None and 100000 or x().initiative)

    @staticmethod
    def clear_turntaker(t, count=1):
        """Clear count references of turn taker from the list"""
        r = weakref.ref(t)
        for x in range(count):
            if r in TurnTaker.turn_takers:
                TurnTaker.turn_takers.remove(r)


class Traversable:
    """Mixin allowing variable traveral costs for a class"""
    def __init__(self, walk_cost=0.0, may_block_movement=False):
        # 0.0 => can't traverse
        # 1.0 => traverse with no penalty
        self.walk_cost = walk_cost
        # False => try_movement always True
        # True  => try_movement might return False
        self.may_block_movement = may_block_movement

    def try_leaving(self, obj):
        """Triggered on obj trying to leave this class. Return False to prevent move"""
        return True

    def try_movement(self, obj):
        """Triggered on obj trying to arrive at this class. Return False to prevent move"""
        if self.blocks_movement():
            raise InvalidMoveContinueError
        return self.walk_cost

    def blocks_movement(self, is_for_mapping=False):
        """Does this object block movement entirely?
        Set is_for_mapping when testing possible paths (rather than actual ones)"""
        return (self.walk_cost == 0.0) and (not is_for_mapping or self.may_block_movement)


class Transparent(Mappable):
    """Mixin allowing variable transparency"""
    def __init__(self, transparency=0.0):
        # NB. mixin so will not init Mappable here
        # 0.0 => completely opaque
        # 1.0 => completely transparent
        self.transparency = transparency

    def blocks_light(self):
        """Does this object block light altogether?"""
        return self.transparency == 0.0

    @property
    def light_level(self):
        if not self.blocks_light():
            return self.map.light_level(self.pos)

        else:
            # copy light value from next cell towards player
            v = self.map.player.pos - self.pos
            # converting v to a unit vector needs to favour diagonals to get better looking lighting
            #m = max(abs(v.x),abs(v.y))
            #v.x /= m; v.y /= m
            v.x = v.x > 0 and 1 or v.x < 0 and -1 or 0
            v.y = v.y > 0 and 1 or v.y < 0 and -1 or 0
            return self.map.light_level(self.pos + v)

    @property
    def light_colour(self):
        if not self.blocks_light():
            return self.map.light_colour(self.pos)

        else:
            # copy light value from next cell towards player
            v = self.map.player.pos - self.pos
            # see comment above
            #m = max(abs(v.x),abs(v.y))
            #v.x //= m; v.y //= m
            v.x = v.x > 0 and 1 or v.x < 0 and -1 or 0
            v.y = v.y > 0 and 1 or v.y < 0 and -1 or 0
            return self.map.light_colour(self.pos + v)


class StatusEffect:
    """things that have passive status (such as being blind, stunned, able to see through walls, ...)"""
    # buffs
    X_RAY_VISION     = 100
    FAST             = 101
    INFRAVISION      = 102
    NIGHT_VISION     = 103
    HIDDEN_IN_SHADOW = 104

    # debuffs
    BLIND        = 200
    DEAF         = 201

    def __init__(self):
        self.current_effects = []

    def add_effect(self, status):
        """Adds status as a status effect"""
        if status in self.current_effects:
            return False
        else:
            self.current_effects.append(status)
            return True

    def remove_effect(self, status):
        """Removes status as a status effect"""
        if not status in self.current_effects:
            return False
        else:
            self.current_effects.remove(status)
            return True

    def has_effect(self, status):
        """Does this object have status effect?"""
        return status in self.current_effects


class CountUp:
    """things that count up (e.g. multi-turn stairs traversal)."""
    def __init__(self, count_to, c=0):
        assert c <= count_to, "Setting count up limit of %d to less than initial value of %d" % (count_to, c)
        self.count_to = count_to
        self.count    = c

    def inc(self, i=1):
        """Increment count by i. Returns true if already full, or if full as a result of incrementing"""
        if self.full():
            return True
        self.count += i
        if self.count > self.count_to:
            self.count = self.count_to
        return self.full()

    def dec(self, i=1):
        """Decrement count by i. Returns true if zero, or reached zero through decrementing"""
        if i > self.count:
            self.count = 0
        else:
            self.count -= i
        return self.count == 0

    def reset(self, c=0):
        """Reset count to c. Defaults to zero.
        NB. This does no bounds checking!"""
        self.count = c

    def full(self):
        """Has counter counted up to limit?"""
        return self.count == self.count_to


class HasInventory:
    """Mixin for objects with inventory"""
    def __init__(self, inv_size, fixed_slots=()):
        """Normal inventory and inventory slots (e.g. head, feet) are managed separately"""
        self.items = [None for i in range(inv_size)]
        self.slot_keys  = fixed_slots
        self.slot_items = {}
        for s in fixed_slots:
            self.slot_items[s] = None


class Carryable:
    """Mixin for carryable objects"""
    pass


class Activator:
    """Mixin for objects that can activate things"""
    pass


class Activatable:
    """Mixin for objects that can be activated"""
    def __init__(self, owner=None):
        assert isinstance(owner, Activator) or owner is None, "%s can't activate %s" % (owner, self)
        self.owner = owner
        self.can_be_remote_controlled = False

    def activate(self, activator=None):
        """Activate object. If activator is set, object is activated by them and not their owner (set by constructor).
        Return False to indicate that activation failed"""
        if activator is None:
            assert isinstance(self.owner, Activator), "%s can't be activated by %s" % (self, self.owner)
        else:
            assert isinstance(activator, Activator), "%s can't be activated by %s" % (self, activator)

        return True


class Alertable(Mappable):
    """Mixin for objects that can be alerted to things"""
    PRI_LOW  = 0
    PRI_MED  = 1
    PRI_HIGH = 2
    ALERTABLES = weakref.WeakSet()

    def __init__(self, listen_radius=10):
        self.listen_radius    = listen_radius
        self.investigate_list = {Alertable.PRI_LOW: [], Alertable.PRI_MED: [], Alertable.PRI_HIGH: []}
        Alertable.ALERTABLES.add(self)

    def alert(self, to_pos, priority=None):
        """Alert object to given position with optional priority (see PRI_* attributes)"""
        if to_pos.distance_to(self.pos) > self.listen_radius:
            return False

        if priority is None:
            priority = Alertable.PRI_MED

        #print("%s alerted to %s, pri %d"%(self, to_pos, priority))
        self.investigate_list[priority].append(to_pos)

        return True

    def clear_alert(self, pos, clear_others=True):
        """Clear pos from alert list so that object no longer interested."""
        r = False
        for (pri, il) in self.investigate_list.items():
            if pos in il:
                il.remove(pos)
                r = True
                if clear_others and pri != Alertable.PRI_HIGH:
                    # clear from other priorities too
                    for a in Alertable.ALERTABLES:
                        if not a is self and \
                                (pos in a.investigate_list[Alertable.PRI_LOW] or pos in a.investigate_list[Alertable.PRI_MED]):
                            a.clear_alert(pos, clear_others=False)

        return r

    def investigate_next(self):
        """Find the next position to investigate, weighted by priority"""
        # TODO: weight priority and self.pos
        for pri in (Alertable.PRI_HIGH, Alertable.PRI_MED, Alertable.PRI_LOW):
            if len(self.investigate_list[pri]) > 0:
                return self.investigate_list[pri].pop(0)
        return None


# TODO: use this for symmetry between player and monsters with same capabilities
class CanSee:
    """Mixin for objects that can see"""
    def __init__(self, radius=0):
        self.seeing_radius = radius

    def reset_fov(self):
        """Reset object's field of vision"""
        raise NotImplementedError


class Shouter(Mappable):
    """Mixin for things that can alert others to something (e.g. alarms)"""
    def __init__(self, audible_radius=10):
        # NB. mixin: doesn't init Mappable directly
        self.audible_radius = audible_radius

    def shout(self, at_thing=None, priority=None):
        """Shout out, alerting all alertables to at_pos, or Mappable.pos if omitted.
        Set priority to increase importance of shout."""
        if at_thing is None:
            at_thing = self

        # alert things within your audible radius, NOT the target's
        for a in self.map.find_all_within_r(self, Alertable, self.audible_radius):
            # don't alert yourself [TODO: this is probably right]
            # ... or the thing you're alerting about
            if not (a is self or a is at_thing):
                a.alert(at_thing.pos, priority)


class Talker(Shouter):
    """Mixin for objects that talk out loud"""
    currently_talking = weakref.WeakSet()

    def __init__(self):
        self.__phrases = {}
        self.is_talking = False
        self.__chat = Message(None, "", True)
        self.__chat.is_visible = False
        self.__chat.timeout = 2.0

    def add_phrases(self, key, phrases, probability=0.05, is_shouting=False):
        """Associate list of phrases with a key (e.g. a monster AI state).
        probability gives chance of a phrase being used.
        If isinstance(self, Shouter) and is_shouting set, triggering one of these phrases will call self.shout()"""
        if not key in self.__phrases.keys():
            self.__phrases[key] = {}
        self.__phrases[key]['probability'] = probability
        self.__phrases[key]['is_shouting'] = is_shouting
        self.__phrases[key]['phrases']     = phrases
        return self

    def stop_talk(self):
        """Stop any talking activity immediately."""
        self.__chat.is_visible = False
        self.is_talking = False
        if self in self.currently_talking:
            self.currently_talking.remove(self)

    def talk(self, key=None):
        """Talk out loud, using a randomly chosen phrase based on key."""
        if self.is_talking:
            self.stop_talk()
        if not key in self.__phrases.keys() or len(self.__phrases[key]['phrases']) == 0:
            return False
        if libtcod.random_get_float(None, 0.0, 1.0) < self.__phrases[key]['probability']:
            #assert key in self.__phrases.keys(), "Talker %s has no vocab for key %s"%(self,key)
            self.__chat.pos = self.pos - (0, 1)
            self.__chat.text = self.__phrases[key]['phrases'][
                libtcod.random_get_int(None, 0, len(self.__phrases[key]['phrases']) - 1)
                ]
            self.is_talking = True
            self.__chat.is_visible = True
            self.currently_talking.add(self)
            if self.__phrases[key]['is_shouting']:
                self.shout()
            return True
        return False

    @staticmethod
    def stop_all_talk():
        """Clear list of objects currently talking."""
        # NB: this can chuck a runtime error due to a bug in Python 3.2
        # see http://bugs.python.org/issue14159
        #for t in Talker.currently_talking:
        #    t.stop_talk()
        while(len(Talker.currently_talking) > 0):
            Talker.currently_talking.pop().stop_talk()
