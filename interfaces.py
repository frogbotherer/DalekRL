#!/usr/bin/env python3

import libtcodpy as libtcod

class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __add__(self,other):
        if isinstance(other,tuple):
            self.x += other[0]
            self.y += other[1]
        else:
            self.x += other.x
            self.y += other.y
        return self

    def __sub__(self,other):
        if isinstance(other,tuple):
            self.x -= other[0]
            self.y -= other[1]
        else:
            self.x -= other.x
            self.y -= other.y
        return self

    def __gt__(self,other):
        """Furthest from origin is largest; if tied, larger x beats larger y so that we sort left-right, top-bottom"""
        return (self.x*self.y>other.x*other.y) or (self.x>other.x)
    def __ge__(self,other):
        return (self.x*self.y>other.x*other.y) or (self.x>=other.x)

    def __repr__(self):
        return "Position(%d,%d)" % (self.x,self.y)

    def __str__(self):
        return "(%d,%d)" % (self.x,self.y)


class Drawable:
    """Can appear on the map"""

    def __init__(self,pos,symbol,colour):
        self.pos = pos
        print("1: %s"%pos)
        self.symbol = symbol
        self.colour = colour


    def move(self, delta):
        #move by the given amount
        self.pos += delta
 
    def move_to(self, pos):
        self.pos = pos

    def move_up(self):
        self.pos += (0,-1)
    def move_down(self):
        self.pos += (0,1)
    def move_left(self):
        self.pos += (-1,0)
    def move_right(self):
        self.pos += (1,0)

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(0, self.colour)
        libtcod.console_put_char(0, self.pos.x, self.pos.y, self.symbol, libtcod.BKGND_NONE)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(0, self.pos.x, self.pos.y, ' ', libtcod.BKGND_NONE)
