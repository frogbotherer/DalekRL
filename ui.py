#!/usr/bin/env python3

import libtcodpy as libtcod

from interfaces import UI

class Bar(UI):
    def __init__(self, pos, size, fgcolours, bgcolour, show_numerator=True, show_denominator=False):
        UI.__init__(self)
        self.pos = pos
        self.size = size
        if not isinstance(fgcolours,list):
            fgcolours = [fgcolours]
        self.fgcolours = fgcolours
        self.bgcolour = bgcolour

        self.show_numerator = show_numerator
        self.show_denominator = show_denominator

        self.value = 0
        self.max_value = 0

        self.percentiles = [1.0]

    def draw(self):
        raise NotImplementedError


class HBar(Bar):
    
    def draw(self):
        assert len(self.percentiles)==len(self.fgcolours), "HBar not configured correctly"

        # calculate text
        s = " " * self.size
        if self.show_numerator:
            if self.show_denominator:
                s = ("%s/%s"%(self.value,self.max_value)).center(self.size)
            else:
                s = ("%s"%(self.value)).center(self.size)

        # draw bar
        fv = self.value/self.max_value
        fg_idx = 0
        for i in range(0,self.size):
            #calculate colour for this character
            f = (i+1)/self.size
            col = self.bgcolour
            if f<=fv: # part of bar fg
                while f>self.percentiles[fg_idx]:
                    fg_idx += 1
                    assert fg_idx < len(self.percentiles), "HBar not configured correctly"
                col = self.fgcolours[fg_idx]
            libtcod.console_put_char_ex(0, self.pos.x+i, self.pos.y, s[i], libtcod.white, col)
