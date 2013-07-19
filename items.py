#!/usr/bin/env python3

import libtcodpy as libtcod

from functools import reduce

from interfaces import Carryable, Activatable, Activator, CountUp, Mappable, TurnTaker, StatusEffect, Shouter
from ui import UI, HBar, Message
from errors import InvalidMoveError

class Item(Carryable, Activatable, Mappable):
    # for item generation
    awesome_rank    = 2   # out of 5. 0 can't be returned by .random()
    awesome_weight  = 1.0 # 0.0 never occur; 1.0 normal; 2.0 twice normal ... choices also sorted by weight within each rank
    AWESOME_MAP     = None

    def __init__(self, owner, power, colour, symbol='!'):
        pos = None
        if not isinstance(owner, Activator):
            pos   = owner
            owner = None
        self.power = power
        Mappable.__init__(self,pos,symbol,colour)
        Activatable.__init__(self,owner)
        if pos is None:
            self.is_visible = False
        self.is_chargable = False

    def __str__(self):
        if self.owner is None:
            return "%s at %s"%(self.__class__.__name__,self.pos)
        else:
            return "%s held by %s"%(self.__class__.__name__,self.owner)

    def draw_ui(self,pos,max_width=40):
        pass

    def drop_at(self,pos):
        self.owner = None
        self.pos = pos
        self.is_visible = True

    def take_by(self,owner):
        self.owner = owner
        self.pos = None
        self.is_visible = False

    def charge(self,amount=1):
        """returns true if item is charged by more than 0"""
        return False

    @staticmethod
    def random(rng,pos,ranks=range(1,4),weight=1.0):
        """random item at pos using rng. fixing a rank will limit choice to that rank. raising weight increases probability of a good item"""
        # build cache of item ranks and weights
        if Item.AWESOME_MAP is None:
            Item.__GEN_AWESOME_MAP()

        if isinstance(ranks,int):
            ranks = [ranks]

        elif isinstance(ranks,list):
            ranks.sort()

        # calculate weighted range
        awesome_range = reduce( lambda a,b: a + b, [A[1][-1].awesome_acc_weight for A in Item.AWESOME_MAP.items() if A[0] in ranks], 0.0 )

        # roll die and weight by parameter
        # NB. weighting can push t out of bounds!
        t = awesome_range + 1.0
        while t >= awesome_range:
            t = libtcod.random_get_float(rng,0.0,awesome_range) * weight

        #print("Range = 0.0 - %f  =>  %f" % (awesome_range,t))

        # find rank that was rolled
        rank = ranks[0]
        while t > Item.AWESOME_MAP[rank][-1].awesome_acc_weight:
            t    -= Item.AWESOME_MAP[rank][-1].awesome_acc_weight
            rank += 1

        #print("Rank = %d  =>  %s   %s" %(rank,Item.AWESOME_MAP[rank],[C.awesome_acc_weight for C in Item.AWESOME_MAP[rank]]))

        # find item that was rolled
        item_idx = 0
        while t > Item.AWESOME_MAP[rank][item_idx].awesome_acc_weight:
            item_idx += 1

        # calculate item power (higher in range => more power)
        item_power = 2 * (Item.AWESOME_MAP[rank][item_idx].awesome_acc_weight-t) / Item.AWESOME_MAP[rank][item_idx].awesome_weight
        
        #print("Got %s (%d) at power %f" % (Item.AWESOME_MAP[rank][item_idx],item_idx,item_power))

        return Item.AWESOME_MAP[rank][item_idx](pos,item_power)

    def __GEN_AWESOME_MAP():
        Item.AWESOME_MAP = {}
        for i in range(1,6):
            Item.AWESOME_MAP[i] = [] # need empty entries even if no rank
        for C in (MemoryWipe,Tangler,TangleMine,HandTeleport,Cloaker,DoorRelease,LevelMap,XRaySpecs,LabCoat,EmergencyHammer,RemoteControl,AnalysisSpecs):
            Item.AWESOME_MAP[C.awesome_rank].append(C)
        for CL in Item.AWESOME_MAP.values():
            CL.sort(key=lambda x: x.awesome_weight)
            last = 0.0
            for C in CL:
                # generate a corrected cumulative weight, where high rank items are rarer
                C.awesome_acc_weight = (C.awesome_weight + last)/C.awesome_rank
                last += C.awesome_weight


class SlotItem(Item):
    awesome_rank   = 3
    awesome_weight = 1.0

    HEAD_SLOT = 'Head'
    BODY_SLOT = 'Body'
    FEET_SLOT = 'Feet'

    def __init__(self,owner,item_power,valid_slot,item_colour=libtcod.cyan,bar_colour=libtcod.dark_cyan):
        Item.__init__(self,owner,item_power,item_colour,'[')
        self.valid_slot = valid_slot


class RunDownItem(SlotItem, CountUp, TurnTaker):
    def __init__(self,owner,item_power,valid_slot,item_colour=libtcod.cyan,bar_colour=libtcod.dark_cyan):
        SlotItem.__init__(self,owner,item_power,valid_slot,item_colour,bar_colour)
        count_to = int( 50 + 100*item_power )
        CountUp.__init__(self,count_to)
        TurnTaker.__init__(self,100,False)

        self.bar = HBar(None, None, bar_colour, libtcod.dark_grey, True, False, str(self), str.ljust)
        self.bar.is_visible = False

        self.is_active = False
        self.is_chargable = True

    def take_turn(self):
        assert self.is_active, "Taking turns on inactive RunDownItem %s" % self

        # sanity: if left active and dropped, deactivate
        if not self.owner:
            self.activate()
            return False

        if self.inc():
            self.is_active = False

        return True

    def activate(self,activator=None):
        if self.is_active:
            # deactivate an active item
            self.is_active = False
            TurnTaker.clear_turntaker(self)
            return True

        elif self.full():
            # can't activate one that's run out
            return False

        else:
            self.is_active = True
            TurnTaker.add_turntaker(self)
            self.inc(4) # activation costs 4 + 1 for the first turn; discouraging flickering
            self.take_turn() # so takes effect straight away if any turn taking behaviour
            return True

    def charge(self,amount=1):
        if self.is_chargable:
            return self.dec(amount)

    # TODO: refactor these, plus the bar, into the base class
    def draw_ui(self,pos,max_width=40):
        self.bar.pos = pos
        self.bar.size = max_width
        self.bar.value = self.count_to-self.count
        self.bar.max_value = self.count_to
        self.bar.is_visible = True

    def drop_at(self,pos):
        Item.drop_at(self,pos)
        self.bar.is_visible = False

    def take_by(self,owner):
        Item.take_by(self,owner)
        self.bar.is_visible = True


class CoolDownItem(Item, CountUp, TurnTaker):
    awesome_rank   = 2
    awesome_weight = 1.0

    def __init__(self,owner,item_power,item_colour=libtcod.green,bar_colour=libtcod.dark_green):
        count_to = int( 30 - 10*item_power )
        Item.__init__(self,owner,item_power,item_colour)
        CountUp.__init__(self,count_to,count_to)
        TurnTaker.__init__(self,100,False)
        self.bar = HBar(None, None, bar_colour, libtcod.dark_grey, True, False, str(self), str.ljust)
        self.bar.is_visible = False
        self.is_chargable = True

    def take_turn(self):
        if self.inc():
            TurnTaker.clear_turntaker(self)
            return True
        return False

    def activate(self,activator=None):
        if not self.full():
            print ("%s still on cooldown, %d turns remaining"%(self,self.count_to-self.count))
            # still on cooldown
            return False
        self.reset(0) # was -1 because we immediately inc()
        TurnTaker.add_turntaker(self)
        return True

    def draw_ui(self,pos,max_width=40):
        self.bar.pos = pos
        self.bar.size = max_width
        self.bar.value = self.count
        self.bar.max_value = self.count_to
        self.bar.is_visible = True

    def drop_at(self,pos):
        Item.drop_at(self,pos)
        self.bar.is_visible = False

    def take_by(self,owner):
        Item.take_by(self,owner)
        self.bar.is_visible = True

    def charge(self,amount=1):
        if self.is_chargable:
            return not self.inc(amount)

class LimitedUsesItem(Item):
    awesome_rank   = 1
    awesome_weight = 1.0

    def __init__(self,owner,item_power=1.0,item_colour=libtcod.orange,bar_colour=libtcod.red):
        Item.__init__(self,owner,item_power,item_colour)
        uses = int(1 + 3*item_power)
        self.max_uses = uses
        self.uses = uses
        self.bar = HBar(None, None, bar_colour, libtcod.dark_grey, True, False, str(self), str.ljust)
        self.bar.is_visible = False

    def draw_ui(self,pos,max_width=40):
        self.bar.pos = pos
        self.bar.size = max_width
        self.bar.value = self.uses
        self.bar.max_value = self.max_uses
        self.bar.is_visible = True

    def activate(self,activator=None):
        if self.uses == 0:
            return False

        self.uses -= 1
        return True

    def drop_at(self,pos):
        Item.drop_at(self,pos)
        self.bar.is_visible = False

    def take_by(self,owner):
        Item.take_by(self,owner)
        self.bar.is_visible = True


class HandTeleport(CoolDownItem):
    awesome_weight = 0.5

    def __str__(self):
        return "Hand Teleport"

    def activate(self,activator=None):
        if not CoolDownItem.activate(self):
            return False

        try:
            self.owner.move_to(self.owner.map.find_random_clear())
        except InvalidMoveError:
            print("Can't teleport from %s" % self.owner.pos)
            return False
        self.owner.reset_fov()
        return True


class Cloaker(CoolDownItem):
    awesome_weight = 1.2

    def __init__(self,owner,item_power=1.0):
        CoolDownItem.__init__(self,owner,item_power,libtcod.light_blue,libtcod.dark_blue)
        self.hidden_at = None

    def __str__(self):
        return "Cloaker"

    def activate(self,activator=None):
        if not CoolDownItem.activate(self):
            return False
        self.owner.is_visible = False
        self.hidden_at = self.owner.pos
        return True
    
    def take_turn(self):

        # only run cooldown whilst effect inactive
        if self.hidden_at is None:
            CoolDownItem.take_turn(self)

        # player moved; unhide them
        elif self.hidden_at != self.owner.pos:
            self.owner.is_visible = True
            self.hidden_at = None


class RemoteTimer(LimitedUsesItem):
    pass # TODO: same as R/C but counts down from activation

class RemoteControl(LimitedUsesItem):
    awesome_weight = 1.8

    def __init__(self,owner,item_power,item_colour=libtcod.orange,bar_colour=libtcod.red):
        # only a few uses permitted!
        self.connected_to = None
        LimitedUsesItem.__init__(self,owner,item_power*0.5,item_colour=item_colour,bar_colour=bar_colour)

    def __str__(self):
        if self.connected_to is None:
            return "Remote Control"
        else:
            return "R/C for %s" % self.connected_to

    def activate(self,activator=None):
        # sanity
        if self.owner is None or self.uses == 0:
            print("sanity failed")
            return False

        # set something to activate
        if self.connected_to is None:
            activatables = [a for a in self.owner.map.find_all_at_pos(self.owner.pos) if isinstance(a,Activatable) and a.can_be_remote_controlled]
            if len(activatables)>0:
                self.connected_to = activatables[0]
                self.bar.text = str(self)
                self.bar.show_numerator = False # because it doesn't fit
                return True
            return False

        # activate the thing
        else:
            t = self.connected_to.activate(self.owner)
            if t:
                self.connected_to = None
                self.bar.text = str(self)
                self.bar.show_numerator = True
                return LimitedUsesItem.activate(self,self.owner)
            return False

from tangling import Tanglable, Tangle
from monsters import Monster

class Tangler(LimitedUsesItem):
    awesome_weight = 1.5

    def __str__(self):
        return "Tangler"

    def activate(self,activator=None):
        # TODO: make this find the nearest untangled tanglable
        m = self.owner.map.find_nearest(self.owner,Tanglable,Monster)
        if isinstance(m, Tanglable) and not m.is_tangled() and LimitedUsesItem.activate(self):
            t = Tangle()
            t.add(m)
            return True

        return False

class TangleMine(LimitedUsesItem):
    awesome_weight = 1.2

    def __str__(self):
        return "Tangle Mine"

    def activate(self,activator=None):
        if LimitedUsesItem.activate(self):
            t = Tangle(self.owner.pos)
            t.tangle_counter = 10 # stays until something collides with it
            self.owner.map.add(t)
            return True

        return False

class MemoryWipe(LimitedUsesItem):
    awesome_weight = 0.8
    def __str__(self):
        return "Memory Wipe"

    def activate(self,activator=None):
        ms = self.owner.map.find_all_within_r(self.owner, Monster, 30, False)
        if len(ms)>0 and LimitedUsesItem.activate(self):
            for m in ms:
                m.reset_state()
            return True
        return False

from tiles import Tile, Door, Window, Floor
class DoorRelease(LimitedUsesItem):
    awesome_weight = 0.7

    def __str__(self):
        return "Door Release"

    def activate(self,activator=None):
        d = self.owner.map.find_nearest(self.owner,Door,Tile)
        if not d is None and LimitedUsesItem.activate(self):
            d.to_closing()
            return True
        return False

class EmergencyHammer(LimitedUsesItem):
    awesome_weight = 0.8

    def __str__(self):
        return "Emergency Hammer"

    def activate(self,activator=None):
        for w in self.owner.map.find_all_within_r(self.owner,Window,3):
            if not w.is_smashed and LimitedUsesItem.activate(self):
                w.smash()
                return True
        return False

class LevelMap(LimitedUsesItem):
    awesome_weight = 0.4
    def __init__(self,owner,item_power,item_colour=libtcod.orange,bar_colour=libtcod.red):
        # only a few uses permitted!
        LimitedUsesItem.__init__(self,owner,item_power*0.3,item_colour=item_colour,bar_colour=bar_colour)

    def __str__(self):
        return "Map"

    def activate(self,activator=None):
        if LimitedUsesItem.activate(self):
            for t in self.owner.map.find_all(Tile):
                t.has_been_seen = True
            return True
        return False

class Evidence(Item):
    awesome_rank = 0

    def __str__(self):
        return "Evidence"

    def __init__(self,pos):
        Item.__init__(self,pos,0.0,libtcod.yellow)

class XRaySpecs(RunDownItem):
    def __init__(self,owner,item_power=1.0):
        RunDownItem.__init__(self,owner,item_power,SlotItem.HEAD_SLOT)

    def __str__(self):
        return "X-Ray Specs"

    def activate(self,activator=None):
        if not RunDownItem.activate(self):
            return False

        if self.is_active:
            self.owner.add_effect(StatusEffect.X_RAY_VISION)
            self.owner.reset_fov()

        else:
            self.owner.remove_effect(StatusEffect.X_RAY_VISION)
            self.owner.reset_fov()

        return True

class AnalysisSpecs(RunDownItem):
    SYM_W_E   = '-'
    SYM_N_S   = '|'
    SYM_NW_SE = '\\'
    SYM_NE_SW = '/'

    def __init__(self,owner,item_power=1.0):
        RunDownItem.__init__(self,owner,item_power,SlotItem.HEAD_SLOT)
        self.messages = []

    def __str__(self):
        return "Analysis Specs"

    def activate(self,activator=None):
        if self.is_active: # i.e. about to be deactivated
            self.messages = []
        return RunDownItem.activate(self,activator)

    def take_turn(self):
        self.messages = []

        if not RunDownItem.take_turn(self):
            return False

        # show the heading of each monster as a line
        ms = self.owner.map.find_all(Monster,Monster)
        for m in ms:
            if m.last_pos is None or m.last_pos == m.pos or not self.owner.map._drawing_can_see(m.pos):
                continue # nothing to do here
            v = m.pos-m.last_pos

            # calculate symbol
            s = self.SYM_NE_SW
            if v.y == 0:
                s = self.SYM_W_E
            elif v.x == 0:
                s = self.SYM_N_S
            elif v.x == v.y:
                s = self.SYM_NW_SE

            g = Message(m.pos+v, s, colour=UI.COLCTRL_GREEN)
            g.is_visible = True
            g.timeout    = 5.0
            self.messages.append(g)

        return True


class RunningShoes(RunDownItem):
    def __init__(self,owner,item_power=1.0):
        RunDownItem.__init__(self,owner,item_power*0.5,SlotItem.FEET_SLOT)

    def __str__(self):
        return "Running Shoes"

    def activate(self,activator=None):
        if not RunDownItem.activate(self):
            return False

        if self.is_active:
            TurnTaker.add_turntaker(self.owner)

        else:
            TurnTaker.clear_turntaker(self.owner)

        return True

class LabCoat(SlotItem):
    def __init__(self,owner,item_power=1.0):
        SlotItem.__init__(self,owner,0.0,SlotItem.BODY_SLOT)

    def __str__(self):
        return "Lab Coat"
