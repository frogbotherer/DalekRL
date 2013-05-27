#!/usr/bin/env python3

import libtcodpy as libtcod
from interfaces import Mappable

class Monster (Mappable):
    def take_turn(self):
        pass


class Dalek (Monster):
    def __init__(self,pos=None):
        Monster.__init__(self,pos,'D',libtcod.red)

    def take_turn(self):
        pass

# put here for now
class Player (Mappable):
    pass
