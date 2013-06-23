#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable, Position, Activatable, Activator, CountUp, Talker, TurnTaker, Alertable, Shouter
from errors import GameOverError, InvalidMoveError, TodoError
from ui import HBar, Message, Menu


class Monster_State:
    def __init__(self,monster):
        self.monster = monster

    def get_move(self):
        raise NotImplementedError


class Monster (Mappable, TurnTaker):
    def __init__(self,pos,symbol,colour):
        Mappable.__init__(self,pos,symbol,colour)
        TurnTaker.__init__(self,10)
        self.reset_state()

    def __str__(self):
        return "%s at %s" %(self.__class__.__name__,self.pos)

    def random(rng,pos):
        r = libtcod.random_get_float(rng,0.0,1.0)
        if r < 0.2:
            return StaticCamera(pos)
        elif r < 0.4:
            return CrateLifter(pos)
        else:
            return Dalek(pos)

    def reset_state(self):
        self.state = MS_Stationary(self)


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
            return self.destination_pos
        else:
            assert False, "Can't investigate %s from %s" % (self.destination_pos,self.monster.pos)

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

from tiles import Crate
class CrateLifter (Monster,Tanglable,Talker,Shouter):
    def __init__(self,pos=None):
        Monster.__init__(self,pos,'l',libtcod.light_red)
        Tanglable.__init__(self,7)
        Talker.__init__(self,{},0.05)
        Shouter.__init__(self,40)
        self.my_crate = None
        self.am_carrying_my_crate = False

    def take_turn(self):
        if not self.is_visible:
            return None

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
                            self.shout()

                    else:
                        # someone moved my crate
                        #  * be confused
                        self.state = MS_LostSearchTarget(self)
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

    def __choose_new_crate(self):
        all_crates = self.map.find_all(Crate,Tile)
        self.my_crate = all_crates[libtcod.random_get_int(None,0,len(all_crates)-1)]


class Dalek (Monster,Tanglable,Talker,Alertable,Shouter):
    def __init__(self,pos=None):
        Monster.__init__(self,pos,'d',libtcod.red)
        Tanglable.__init__(self,5)
        Talker.__init__(self,{
                MS_RecentlyTangled: ['** BZZZT **'],
                MS_SeekingPlayer: ['** EXTERMINATE! **','** DESTROY! **','** HALT! **'],
                MS_InvestigateSpot: ['** HUNTING **','** I WILL FIND YOU **'],
                MS_Patrolling: ['** BEEP BOOP **','** BOOP BEEP **']
                },0.05)
        Alertable.__init__(self,30)
        Shouter.__init__(self,30)


    def take_turn(self):
        # sanity checks
        assert not self.map is None, "%s can't take turn without a map" % self

        # if not visible, do nothing
        if not self.is_visible:
            return

        p = self.map.player

        # TODO: refactor as follows??
        # self.state = self.state.get_next_state()
        # self.move_to( self.state.get_move() )

        # if already on the player square(!), stop
        if self.pos == p.pos:
            self.state = MS_Stationary(self)

        # if still confused from tangling, be confused
        elif isinstance(self.state,MS_Confused) and not self.state.full():
            pass

        # otherwise chase player if visible
        elif self.map.can_see(self):
            if not isinstance(self.state,MS_SeekingPlayer):
                self.state = MS_SeekingPlayer(self)
                self.shout(self.map.player.pos)

        # otherwise: if was chasing and now lost player, home on last loc
        elif isinstance(self.state,MS_SeekingPlayer):
            self.state = MS_InvestigateSpot(self,self.state.player_last_pos)

        # otherwise if investigating
        elif isinstance(self.state,MS_InvestigateSpot):
            # ... change state if got to spot without finding player
            if self.pos == self.state.destination_pos:
                self.state = MS_LostSearchTarget(self)

        # otherwise patrol
        else:
            if not isinstance(self.state,MS_Patrolling):
                self.state = MS_Patrolling(self)
                
        # try to move
        try:
            self.move_to(self.state.get_move())
        except InvalidMoveError:
            pass

        # if on player square: lose
        if self.pos == p.pos:
            raise GameOverError("Caught!")

        # find monster
        m = self.map.find_nearest(self,Monster)

        # if on monster square: tangle
        if self.pos == m.pos and isinstance(m,Tanglable):
            self.tangle(m)
            self.state = MS_RecentlyTangled(self)

        # chatter
        self.talk(self.state.__class__)

    def alert(self,to_pos):
        # only become alerted if in a neutral state
        if isinstance(self.state,MS_Patrolling) or isinstance(self.state,MS_Stationary):
            if Alertable.alert(self,to_pos):
                self.state = MS_InvestigateSpot(self,to_pos)


class StaticCamera(Monster, Talker, CountUp, Shouter):
    def __init__(self,pos=None):
        Monster.__init__(self,pos,'c',libtcod.light_red)
        Talker.__init__(self,{
                MS_SeekingPlayer: ['** BLAAARP! BLAAARP! **','** INTRUDER ALERT! **','** WARNING! **'],
                MS_InvestigateSpot: ['beeeeeeee','bip bip bip bip'],
                MS_Stationary: ['bip','whrrrrr']
                },1)
        Shouter.__init__(self,50)
        CountUp.__init__(self,2)

    def take_turn(self):
        # sanity checks
        assert not self.map is None, "%s can't take turn without a map" % self

        # if not visible, do nothing
        if not self.is_visible:
            return

        if self.map.can_see(self):
            if self.inc():
                self.state = MS_SeekingPlayer(self)
                self.shout()

            elif not isinstance(self.state,MS_InvestigateSpot):
                self.state = MS_InvestigateSpot( self, self.map.player.pos )
        
        else: # can't see player
            if not isinstance(self.state,MS_Stationary):
                self.state = MS_Stationary(self)
                self.reset()
            # TODO: fix Talker interface so don't need to cheat
            if libtcod.random_get_int(None,1,10) > 1:
                self.stop_talk()
                return

        self.talk(self.state.__class__)

# put here for now
from items import Item, Evidence
from tiles import Tile
class Player (Mappable,Activator):
    def __init__(self,pos):
        Mappable.__init__(self,pos,'@',libtcod.white)
        self.items = [Item.random(None,self,2,1.5),Item.random(None,self,1),None]
        self.turns = 0
        self.evidence = []
        self.levels_seen = 0

    def __str__(self):
        return "Player at %s" % self.pos

    def use_item(self,slot):
        assert slot<len(self.items), "Using undefined item slot"
        if self.items[slot] is None:
            return
        assert isinstance(self.items[slot],Activatable)
        
        return self.items[slot].activate()

    def draw_ui(self,pos,max_size=80):
        for i in range(len(self.items)):
            libtcod.console_print(0, pos.x, pos.y+i, "%d."%(i+1))
            if self.items[i] is None:
                libtcod.console_print(0, pos.x+3, pos.y+i, "--- Nothing ---")
            else:
                self.items[i].draw_ui(pos+(3,i), 40)

    def pickup(self,i):
        assert isinstance(i,Item), "Can't pick up a %s"%i

        if isinstance(i,Evidence):
            self.evidence.append(i)
            self.map.remove(i)
            return

        item_index = None
        if not None in self.items:
            # prompt to drop something; drop it

            ###
            # prompt code [TODO: refactor me!]
            xu = self.map.size.x//4
            yu = self.map.size.y//4
            b = Menu( Position(xu,yu), Position(xu*2,yu*2), title="Pick up" )
            b.add('x',str(i))
            b.add_spacer()
            for idx in range(len(self.items)):
                v = self.items[idx]
                b.add('%d'%(idx+1),str(v))
            b.is_visible = True
            while 1:
                b.draw()
                libtcod.console_flush()
                k = libtcod.console_wait_for_keypress(True)
                if k and k.pressed and k.c:
                    c = chr(k.c)
                    if   c == 'x':
                        break
                    elif c == '1':
                        item_index = 0
                        break
                    elif c == '2':
                        item_index = 1
                        break
                    elif c == '3':
                        item_index = 2
                        break
                    elif c == 'j':
                        b.sel_prev()
                    elif c == 'k':
                        b.sel_next()
                    elif c == ' ':
                        if b.sel_index() != 0:
                            item_index = b.sel_index()-1
                        break
            b.is_visible = False
            del b
            if item_index is None:
                return
            self.items[item_index].drop_at(self.pos)
            self.map.add(self.items[item_index])
        else:
            item_index = self.items.index(None)
        self.items[item_index] = i
        self.map.remove(i)
        i.take_by(self)

    def move_n(self):
        self.move( (0,-1) )
    def move_s(self):
        self.move( (0,1) )
    def move_w(self):
        self.move( (-1,0) )
    def move_e(self):
        self.move( (1,0) )
    def move_ne(self):
        self.move( (1,-1) )
    def move_nw(self):
        self.move( (-1,-1) )
    def move_se(self):
        self.move( (1,1) )
    def move_sw(self):
        self.move( (-1,1) )
    def use_item1(self):
        self.use_item(0)
    def use_item2(self):
        self.use_item(1)
    def use_item3(self):
        self.use_item(2)
    def interact(self):
        i = self.map.find_at_pos(self.pos,Item)
        if not i is None:
            self.pickup(i)
        for i in self.map.find_all_at_pos(self.pos,Tile):
            if isinstance(i,Activatable):
                i.activate(self)

    def take_turn(self):
        self.turns += 1
