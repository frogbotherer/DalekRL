#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable, Position, Activatable, Activator, CountUp, Talker, TurnTaker, Alertable, Shouter, StatusEffect, LightSource
from errors import GameOverError, InvalidMoveError, TodoError
from ui import HBar, Message, Menu

# lang imports
from functools import reduce
import re # for sub

class Monster_State:
    def __init__(self,monster):
        self.monster = monster

    def get_move(self):
        raise NotImplementedError


class AI:
    """effectively a Monster_State factory"""
    def __init__(self):
        self.reset_state()

    def get_next_state(self):
        raise NotImplementedError

    def reset_state(self):
        self.state = MS_Stationary(self)


class Monster (Mappable, TurnTaker, StatusEffect):
    # TODO: genericise item generation logic and reuse here
    generator_weight = 1.0
    # put most dangerous to right
    GENERATOR = []

    def __init__(self,pos,symbol,colour):
        Mappable.__init__(self,pos,symbol,colour)
        TurnTaker.__init__(self,10)
        StatusEffect.__init__(self)

    def __str__(self):
        return "%s at %s facing %s" %(self.__class__.__name__,self.pos,(self.pos is None or self.last_pos is None) and 'nowhere' or (self.pos-self.last_pos))

    @staticmethod
    def random(rng,pos,weight=1.0):
        if Monster.GENERATOR == []:
            Monster.__GEN_GENERATOR()
        
        max_weight = reduce( lambda a,b: a+b, [C.generator_weight for C in Monster.GENERATOR], 0.0 )
        r = max_weight + 1.0

        while r > max_weight:
            r = libtcod.random_get_float(rng,0.0,max_weight * weight)

        m_idx = 0
        while r > Monster.GENERATOR[m_idx].generator_weight:
            r -= Monster.GENERATOR[m_idx].generator_weight
            m_idx += 1

        return Monster.GENERATOR[m_idx](pos)

    @staticmethod
    def __GEN_GENERATOR():
        Monster.GENERATOR = [StaticCamera,CrateLifter,Dalek,SlowDalek,BetterDalek,LitDalek]

    @staticmethod
    def get_monster_by_name(name):
        if Monster.GENERATOR == []:
            Monster.__GEN_GENERATOR()
        for C in Monster.GENERATOR:
            if C.__name__.lower() == name.lower() or re.sub("([a-z])([A-Z])",r'\1 \2',C.__name__).lower() == name.lower():
                return C
        raise NameError(name)

from tangling import Tanglable


class MS_Confused(Monster_State,CountUp):
    def __init__(self,monster,turns=3):
        Monster_State.__init__(self,monster)
        CountUp.__init__(self,turns)

    def get_move(self):
        self.inc()

        # this will give us a random direction +/- 1 square, or no move
        d = libtcod.random_get_int(None,0,8)
        v = Position( d%3-1, d//3-1 )        
        return self.monster.pos + v

class MS_RecentlyTangled(MS_Confused):
    def __init__(self,monster):
        MS_Confused.__init__(self,monster,4)

class MS_LostSearchTarget(MS_Confused):
    def __init__(self,monster):
        MS_Confused.__init__(self,monster,2)

class MS_SeekingPlayer(Monster_State):
    def __init__(self,monster):
        Monster_State.__init__(self,monster)

    def get_move(self):
        p = self.monster.map.player
        next_move = self.monster.map.get_path(self.monster.pos,p.pos,1)
        self.player_last_pos = Position(p.pos.x,p.pos.y)

        if len(next_move):
            if not self.monster.pos.distance_to(next_move[0])<2:
                next_move = [self.monster.pos]#self.monster.map.get_path(self.monster.pos,p.pos)
                print ("BAD MOVE BY %s" % self.monster)
            assert self.monster.pos.distance_to(next_move[0])<2, "Illegal move by %s to %s"%(self.monster,next_move[0])
            return next_move[0]
        else:
            assert False, "Can't chase player!"

class MS_InvestigateSpot(Monster_State):
    def __init__(self,monster,pos):
        Monster_State.__init__(self,monster)
        self.destination_pos = pos

    def get_move(self):
        next_move = self.monster.map.get_path(self.monster.pos,self.destination_pos)

        if len(next_move):
            return next_move[0]
        elif self.monster.pos == self.destination_pos:
            if isinstance(self.monster,Alertable):
                self.monster.clear_alert(self.destination_pos)
            return self.destination_pos
        else:
            print("WARNING: Can't investigate %s from %s" % (self.destination_pos,self.monster.pos))
            #assert False, "Can't investigate %s from %s" % (self.destination_pos,self.monster.pos)
            return self.monster.pos

class MS_Patrolling(Monster_State):
    def __init__(self,monster,min_distance=10):
        Monster_State.__init__(self,monster)
        self.patrolpt1 = monster.pos
        while True:
            self.patrolpt2 = monster.map.find_random_clear()
            if self.patrolpt1.distance_to(self.patrolpt2) > min_distance:
                break

    def get_move(self):
        if self.monster.pos == self.patrolpt2:
            (self.patrolpt1,self.patrolpt2) = (self.patrolpt2,self.patrolpt1)
        next_move = self.monster.map.get_path(self.monster.pos,self.patrolpt2)

        if len(next_move):
            return next_move[0]
        else:
            assert False, "Can't patrol!"

class MS_Stationary(Monster_State):
    def get_move(self):
        return self.monster.pos


class StaticCamera(Monster, Talker, CountUp, Shouter, AI):
    generator_weight = 0.5

    def __init__(self,pos=None):
        Monster.__init__(self,pos,'c',libtcod.light_red)
        self.remains_in_place = True
        Talker.__init__(self)
        self.add_phrases( MS_SeekingPlayer, ['** BLAAARP! BLAAARP! **','** INTRUDER ALERT! **','** WARNING! **'], 0.7, True )
        self.add_phrases( MS_InvestigateSpot, ['beeeeeeee','bip bip bip bip'], 1.0 )
        self.add_phrases( MS_Stationary, ['bip','whrrrrr'], 0.2 )
        Shouter.__init__(self,50)
        CountUp.__init__(self,2)

        AI.__init__(self)

    def take_turn(self):
        # sanity checks
        assert not self.map is None, "%s can't take turn without a map" % self

        # if not visible, do nothing
        if not self.is_visible:
            #print("%s not visible. tangled? %s"%(self,self.is_tangled()))
            return

        if self.map.can_see(self):
            if self.inc():
                self.state = MS_SeekingPlayer(self)

            elif not isinstance(self.state,MS_InvestigateSpot):
                self.state = MS_InvestigateSpot( self, self.map.player.pos )
        
        else: # can't see player
            if not isinstance(self.state,MS_Stationary):
                self.state = MS_Stationary(self)
                self.reset()

        self.talk(self.state.__class__)


from tiles import Tile,Crate
class CrateLifter (Monster,Tanglable,Talker,Shouter,AI):
    generator_weight = 0.5

    def __init__(self,pos=None):
        Monster.__init__(self,pos,'l',libtcod.light_red)
        Tanglable.__init__(self,7)
        Talker.__init__(self)
        Shouter.__init__(self,40)
        AI.__init__(self)

        self.my_crate = None
        self.am_carrying_my_crate = False

        self.add_phrases('default',['doop doop','doop de doop','a boop de doop'],0.2)
        self.add_phrases('sad',['MY CRATE NOOO!','WHERE CRATE?','NULL CRATE EXCEPTION!'],0.4)
        self.add_phrases('angry',['** ILLEGAL CRATE CONTENTS **','** ERROR ** ERROR **'],1.0)
        self.add_phrases('happy',['DONK!','order fulfilled!','Return code: 0'],0.8)

    def take_turn(self):
        if not self.is_visible:
            #print("%s not visible. tangled? %s"%(self,self.is_tangled()))
            return 

        talk_state = 'default'
        if isinstance(self.state,MS_InvestigateSpot):
            if self.pos == self.state.destination_pos:
                # arrived, what were we doing?

                if not self.am_carrying_my_crate:
                    # if i'm not carrying a crate ...

                    if self.my_crate in self.map.find_all_at_pos(self.pos,Tile):
                        # ... and my crate is on this square ...

                        if self.my_crate.owner is None:
                            # ... and i can pick up my crate:

                            # * pick up crate
                            self.map.remove(self.my_crate,Tile)
                            self.am_carrying_my_crate = True
                            
                            # * choose somewhere to put it
                            self.state.destination_pos = self.map.find_random_clear()

                        else:
                            # someone is in my crate :(
                            # * tell everyone the crate is too heavy!
                            talk_state = 'angry'

                    else:
                        # someone moved my crate
                        #  * be confused
                        self.state = MS_LostSearchTarget(self)
                        talk_state = 'sad'
                        #  * choose a new one
                        self.__choose_new_crate()

                else:
                    # ... i am carrying my crate
                    if len( [c for c in self.map.find_all_at_pos(self.pos,Tile) if isinstance(c,Crate)] ) > 0:
                        # ... but i can't drop it here because there's one there already
                        # * choose somewhere else to put it
                        self.state.destination_pos = self.map.find_random_clear()

                    else:
                        # i put crate down
                        talk_state = 'happy'

                        #  * add back to map
                        self.my_crate.pos = self.pos
                        self.map.add(self.my_crate,Tile)
                        self.am_carrying_my_crate = False

                        #  * find a new crate to pick up
                        self.__choose_new_crate()

            else:
                # happily looking for [somewhere to put] my crate
                pass

        elif isinstance(self.state,MS_Confused):
            if self.state.full():
                # if i was confused and am now right, work out what to do next
                if self.am_carrying_my_crate:
                    self.state = MS_InvestigateSpot(self,self.map.find_random_clear())

                else:
                    if self.my_crate is None:
                        self.__choose_new_crate()
                    self.state = MS_InvestigateSpot(self,self.my_crate.pos)
            else:
                talk_state = 'sad'
        else:
            # any other state: find my crate
            self.__choose_new_crate()
            self.state = MS_InvestigateSpot(self,self.my_crate.pos)

        # try to move
        try:
            self.move_to(self.state.get_move())
        except InvalidMoveError:
            pass

        # if on player square: lose (let's leave it as noisy useless monster for now)
        #if self.pos == self.map.player.pos:
        #    raise GameOverError("Crate Monkey")

        # find monster
        m = self.map.find_nearest(self,Monster)

        # if on monster square: tangle
        if self.pos == m.pos and isinstance(m,Tanglable):
            self.tangle(m)
            self.state = MS_RecentlyTangled(self)

        # make noises
        self.talk(talk_state)

    def __choose_new_crate(self):
        all_crates = self.map.find_all(Crate,Tile)
        self.my_crate = all_crates[libtcod.random_get_int(None,0,len(all_crates)-1)]


class DalekAI(AI):

    def get_next_state(self):
        # if already on the player square(!), stop
        if self.pos == self.map.player.pos:
            return MS_Stationary(self)

        # if still confused from tangling, be confused
        elif isinstance(self.state,MS_Confused) and not self.state.full():
            return self.state

        # otherwise chase player if visible
        elif self.map.can_see(self,self.map.player,0.5):
            if not isinstance(self.state,MS_SeekingPlayer):
                self.shout(self.map.player,priority=Alertable.PRI_HIGH)
                return MS_SeekingPlayer(self)

        # otherwise: if was chasing and now lost player, home on last loc
        elif isinstance(self.state,MS_SeekingPlayer):
            return MS_InvestigateSpot(self,self.state.player_last_pos)

        # otherwise if investigating
        elif isinstance(self.state,MS_InvestigateSpot):
            # ... change state if got to spot without finding player
            if self.pos == self.state.destination_pos:
                return MS_LostSearchTarget(self)

        # otherwise patrol
        else:
            if isinstance(self,Alertable):
                p = self.investigate_next()
                if not p is None:
                    print("%s now investigating %s"%(self,p))
                    return MS_InvestigateSpot(self,p)
            if not isinstance(self.state,MS_Patrolling):
                print("%s has nothing to investigate now"%self)
                return MS_Patrolling(self)

        return self.state


class Dalek (Monster,Tanglable,Talker,Alertable,Shouter,DalekAI):
    generator_weight = 1.2

    def __init__(self,pos=None):
        Monster.__init__(self,pos,'d',libtcod.red)
        Tanglable.__init__(self,5)
        Talker.__init__(self)
        self.add_phrases( MS_RecentlyTangled, ['** BZZZT **'], 0.45 )
        self.add_phrases( MS_SeekingPlayer, ['** EXTERMINATE! **','** DESTROY! **','** HALT! **'], 0.2, True )
        self.add_phrases( MS_InvestigateSpot, ['** HUNTING **','** I WILL FIND YOU **'], 0.25 )
        self.add_phrases( MS_Patrolling, ['** BEEP BOOP **','** BOOP BEEP **'], 0.15 )

        Alertable.__init__(self,30)
        Shouter.__init__(self,30)
        
        DalekAI.__init__(self)


    def take_turn(self):
        # sanity checks
        assert not self.map is None, "%s can't take turn without a map" % self

        # if not visible, do nothing
        if not self.is_visible:
            #print("%s not visible. tangled? %s"%(self,self.is_tangled()))
            return

        # update state
        self.state = self.get_next_state()

        # try to move
        try:
            new_pos = self.state.get_move()

            m = self.map.find_all_at_pos(new_pos,Monster)

            ## this logic stops the monster from entering the same square as a non-tanglable
            ## it also makes sure that the player can't stand on static cameras and be
            ## untouchable
            if len(m) == 0 or len([mi for mi in m if not mi.remains_in_place]) == 0:
                self.move_to(new_pos)
            
            elif len([mi for mi in m if isinstance(mi,Tanglable)]) > 0:
                # tangle if poss
                self.move_to(new_pos)
                self.tangle([mi for mi in m if isinstance(mi,Tanglable)][0])
                self.state = MS_RecentlyTangled(self)
            
            else:
                # don't move if can't tangle with dest monster
                #print("%s can't tangle with %s" % (self,m[0]))
                pass

            #self.move_to(new_pos)
            #ms = [mi for mi in m if isinstance(mi,Tanglable)]
            #if len(ms) > 0:
            #    self.tangle(ms[0])
            #    self.state = MS_RecentlyTangled(self)

        except InvalidMoveError:
            pass

        # if on player square: lose
        if self.pos == self.map.player.pos:
            raise GameOverError("Caught!")

        # chatter
        self.talk(self.state.__class__)

    def alert(self,to_pos,priority=None):
        # only become alerted if in a neutral state
        if isinstance(self.state,MS_Patrolling) or isinstance(self.state,MS_Stationary):
            if Alertable.alert(self,to_pos,priority):
                self.state = MS_InvestigateSpot(self,to_pos)


class LitDalek(Dalek,LightSource):
    generator_weight = 0.8
    def __init__(self,pos=None):
        Dalek.__init__(self,pos)
        LightSource.__init__(self,6,1.0,libtcod.red)
        self.light_enabled = False

    def take_turn(self):
        if not self.map.is_lit(self) and not self.light_enabled:
            self.light_enabled = True
            #self.map.recalculate_lighting(statics=False)
        elif self.map.light_level(self.pos)-self.intensity > LightSource.INTENSITY_VISIBLE and self.light_enabled:
            # TODO: this doesn't work because the dalek's light lights the map bright enough to trigger
            self.light_enabled = False
            #self.map.recalculate_lighting(statics=False)
        return Dalek.take_turn(self)
            

class BetterDalek (Monster,Talker,Alertable,Shouter,DalekAI):
    generator_weight = 0.1

    def __init__(self,pos=None):
        Monster.__init__(self,pos,'b',libtcod.red)
        Talker.__init__(self)
        self.add_phrases( MS_SeekingPlayer, ['** EXTERMINATE! **','** DESTROY! **','** HALT! **'], 0.25, True )
        self.add_phrases( MS_InvestigateSpot, ['** HUNTING **','** I WILL FIND YOU **'], 0.15 )
        self.add_phrases( MS_Patrolling, ['** RRRRRRRRRR **','** BZZZZZZZZ **'], 0.15 )

        Alertable.__init__(self,30)
        Shouter.__init__(self,30)

        DalekAI.__init__(self)

    def take_turn(self):
        # sanity checks
        assert not self.map is None, "%s can't take turn without a map" % self

        # if not visible, do nothing
        if not self.is_visible:
            #print("%s not visible. tangled? %s"%(self,self.is_tangled()))
            return

        # get next state
        self.state = self.get_next_state()
                
        # try to move
        try:
            new_pos = self.state.get_move()
            ms = [m for m in self.map.find_all_at_pos(new_pos,Monster) if not m.remains_in_place]
            if new_pos != self.pos and len(ms)>0:
                # TODO: complain about path being blocked
                # attempt a different move
                #  * get a vector representing the direction we tried
                v  = new_pos - self.pos
                #  * convert to an int
                #      -1,-1   0,-1   1,-1          0    1    2
                #      -1,0    0,0    1,0           7         3
                #      -1,1    0,1    1,1           6    5    4
                #
                V_MAP = [
                    Position(-1,-1),
                    Position(0,-1),
                    Position(1,-1),
                    Position(1,0),
                    Position(1,1),
                    Position(0,1),
                    Position(-1,1),
                    Position(-1,0)
                    ]
                if not v in V_MAP:
                    raise InvalidMoveError # not sure how this happens?
                vi  = V_MAP.index(v)
                #  * get the adjacent vectors
                #  * try both of those
                if    len(self.map.find_all_at_pos(self.pos + V_MAP[vi-1],Monster)) == 0:
                    new_pos = self.pos + V_MAP[vi-1]
                elif  len(self.map.find_all_at_pos(self.pos + V_MAP[(vi+1)%8],Monster)) == 0:
                    new_pos = self.pos + V_MAP[(vi+1)%8]
                #  * ... otherwise give up
                else:
                    raise InvalidMoveError
            self.move_to(new_pos)

        except InvalidMoveError:
            pass

        # if on player square: lose
        if self.pos == self.map.player.pos:
            raise GameOverError("Caught!")

        # chatter
        self.talk(self.state.__class__)

    def alert(self,to_pos,priority=None):
        # only become alerted if in a neutral state
        if isinstance(self.state,MS_Patrolling) or isinstance(self.state,MS_Stationary):
            if Alertable.alert(self,to_pos,priority):
                self.state = MS_InvestigateSpot(self,to_pos)

class SlowDalek (BetterDalek):
    """like a BetterDalek, but moves only once every two spaces"""
    generator_weight = 0.5

    def __init__(self,pos=None):
        Monster.__init__(self,pos,'s',libtcod.red)
        Talker.__init__(self)
        self.add_phrases( MS_SeekingPlayer, ['** EXXXXX **','** TERRRRR **','** MIIII **'], 0.15, True )
        self.add_phrases( MS_InvestigateSpot, ['** BUUUU **','** AAAA **'], 0.15 )
        self.add_phrases( MS_Patrolling, ['** RRRRRRRRRR **','** BZZZZZZZZ **'], 0.15 )

        Alertable.__init__(self,30)
        Shouter.__init__(self,30)

        DalekAI.__init__(self)

        self._tick = True

    def take_turn(self):
        if self._tick:
            BetterDalek.take_turn(self)
            self._tick = False
        else:
            self._tick = True



