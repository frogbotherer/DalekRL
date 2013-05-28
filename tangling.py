#!/usr/bin/env python3

import libtcodpy as libtcod

class Tanglable:

    def __init__(self,tangle_turns=5):
        self.tangle_turns = tangle_turns
        self.tangled_with = None

    def tangle(self,other):
        if isinstance(other,Tangle):
            other.add(self)
            
        elif isinstance(other,Tanglable):
            assert other.tangled_with is None, "oops tangling is broken"
            t = Tangle()
            t.add(self)
            t.add(other)

        else:
            assert False, "%s can't tangle with %s" % (self,other)

    def is_tangled(self):
        return not self.tangled_with is None and self.tangled_with.tangle_counter > 0

    def untangle(self):
        if not self.is_tangled():
            return False
        return self.tangled_with.untangle()


from monsters import Monster

class Tangle(Monster):
    def __init__(self):
        self.__dogpile = []
        self.tangle_counter = 0
        Monster.__init__(self,None,'T',libtcod.red)

    def add(self,monster):
        if not monster in self.__dogpile:
            if self.pos is None:
                self.pos = monster.pos
                print("%s %s"%(self.pos,self))
                monster.map.add(self)
            self.__dogpile.append(monster)
            # create reference to tangle
            monster.tangled_with = self
            # hide monster
            monster.is_visible = False
            # find largest turn count of monsters in pile
            # ... and multiply by size of pile
            self.tangle_counter = len(self.__dogpile) * max(map(lambda o: o.tangle_turns, self.__dogpile))

    def untangle(self):
        self.tangle_counter -= 1
        if self.tangle_counter == 0:
            # restore monsters in dogpile
            for o in self.__dogpile:
                o.is_visible = True
                o.tangled_with = None
                # TODO: tell monsters not to immediately tangle again
            # remove tangle from map
            self.map.remove(self)
            return False
        return True


