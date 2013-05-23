#!/usr/bin/env python3

import libtcodpy as libtcod


class Drawable:
    """Can appear on the map"""

    def __init__(self,x,y,symbol,colour):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.colour = colour


    def move(self, dx, dy):
        #move by the given amount
        self.x += dx
        self.y += dy
 
    def move_to(self, x, y):
        self.x = x
        self.y = y

    def move_up(self):
        self.y -= 1
    def move_down(self):
        self.y += 1
    def move_left(self):
        self.x -= 1
    def move_right(self):
        self.x += 1

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(0, self.colour)
        libtcod.console_put_char(0, self.x, self.y, self.symbol, libtcod.BKGND_NONE)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(0, self.x, self.y, ' ', libtcod.BKGND_NONE)
