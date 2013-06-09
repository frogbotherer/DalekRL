#!/usr/bin/env python3

import libtcodpy as libtcod

class Tanglable:

    def __init__(self,tangle_turns=5):
        self.tangle_turns = tangle_turns
        self.tangled_with = None
        self.recently_tangled = False

    def tangle(self,other):
        if isinstance(other,Tangle):
            other.add(self)
            
        elif isinstance(other,Tanglable):
            t = other.tangled_with
            if other.tangled_with is None:
                t = Tangle()
            t.add(self)
            t.add(other)

        else:
            assert False, "%s can't tangle with %s" % (self,other)

    def is_tangled(self):
        return not self.tangled_with is None and self.tangled_with.tangle_counter > 0


from monsters import Monster
from interfaces import Talker

class Tangle(Monster):

    def __init__(self):
        self.__dogpile = []
        self.tangle_counter = 0
        Monster.__init__(self,None,'T',libtcod.red)

    def add(self,monster):
        if not monster in self.__dogpile:
            if self.pos is None:
                self.pos = monster.pos
                monster.map.add(self)
            self.__dogpile.append(monster)
            # create reference to tangle
            monster.tangled_with = self
            # get rid of monster chat if applicable
            if isinstance(monster,Talker) and monster.is_talking:
                monster.stop_talk() # this clears chat and sets is_talking to False
            # hide monster
            monster.is_visible = False
            # increment tangle counter
            self.tangle_counter += monster.tangle_turns

    def take_turn(self):
        if self.tangle_counter == 0:
            return

        self.tangle_counter -= 1
        if self.tangle_counter == 0:
            # restore monsters in dogpile
            for o in self.__dogpile:
                o.tangled_with = None
                o.is_visible = True
                o.recently_tangled = True

            # remove tangle from map
            self.map.remove(self)


