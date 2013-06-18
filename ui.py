#!/usr/bin/env python3

import weakref

import libtcodpy as libtcod

class UI:
    ui_elements = []
    def __init__(self):
        UI.ui_elements.append(weakref.ref(self))
        self.is_visible = False
        self.timeout = 0.0

    def draw_all(timeout):
        for eref in UI.ui_elements:
            e = eref()
            if e is None:
                UI.ui_elements.remove(eref)
            else:
                if e.is_visible:
                    if e.timeout==0.0 or e.timeout>timeout:
                        e.draw()

    def clear_all():
        for eref in UI.ui_elements:
            e = eref()
            if e is not None:
                e.is_visible = False
                del e
        UI.ui_elements = []

class Message(UI):
    def __init__(self, pos, text, centred=False):
        UI.__init__(self)
        self.pos = pos
        self.text = text
        self.centred = centred

    def draw(self):
        x = self.pos.x
        if self.centred:
            x -= len(self.text)//2
        libtcod.console_print(0, x, self.pos.y, self.text) #, libtcod.white, libtcod.BKGND_NONE)


class Bar(UI):
    def __init__(self, pos, size, fgcolours, bgcolour, show_numerator=True, show_denominator=False, text=None, text_align=str.center):
        UI.__init__(self)
        self.pos = pos
        self.size = size
        if not isinstance(fgcolours,list):
            fgcolours = [fgcolours]
        self.fgcolours = fgcolours
        self.bgcolour = bgcolour

        self.show_numerator = show_numerator
        self.show_denominator = show_denominator
        self.text = text
        self.text_align = text_align

        self.value = 0
        self.max_value = 0

        self.percentiles = [1.0]

    def draw(self):
        raise NotImplementedError


class HBar(Bar):
    
    def draw(self):
        assert len(self.percentiles)==len(self.fgcolours), "HBar not configured correctly"

        # calculate text
        s = ""
        if self.show_numerator:
            if self.show_denominator:
                s = "%d/%d"%(self.value,self.max_value)
            else:
                s = "%d"%(self.value)
        if self.text is not None:
            s = "%s %s"%(self.text,s)
        s = self.text_align(s,self.size)

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


class Box(UI):
#    NW_CORNER = '\u250c'
#    NE_CORNER = '\u2510'
#    SW_CORNER = '\u2514'
#    SE_CORNER = '\u2518'
#    VERT_EDGE = '\u2502'
    HORI_EDGE = chr(libtcod.CHAR_HLINE)
    NW_CORNER = chr(libtcod.CHAR_NW)
    NE_CORNER = chr(libtcod.CHAR_NE)
    SW_CORNER = chr(libtcod.CHAR_SW)
    SE_CORNER = chr(libtcod.CHAR_SE)
    VERT_EDGE = chr(libtcod.CHAR_VLINE)
    T_LEFT    = chr(libtcod.CHAR_TEEE)
    T_RIGHT   = chr(libtcod.CHAR_TEEW)

    def __init__(self, pos, size, colour=libtcod.white, title=""):
        UI.__init__(self)
        self.pos = pos
        self.size = size
        self.colour = colour
        self.title = title


    def draw(self):
        libtcod.console_print(0, self.pos.x, self.pos.y, "%s%s%s"%(self.NW_CORNER,self.HORI_EDGE*(self.size.x-2),self.NE_CORNER))
        if self.title == "":
            for y in range(self.pos.y+1,self.pos.y+self.size.y):
                libtcod.console_print(0, self.pos.x, y, "%s%s%s"%(self.VERT_EDGE," "*(self.size.x-2),self.VERT_EDGE))
        else:
            # title
            libtcod.console_print(0, self.pos.x, self.pos.y+1, "%s%s%s"%(self.VERT_EDGE,self.title.center(self.size.x-2),self.VERT_EDGE))
            libtcod.console_print(0, self.pos.x, self.pos.y+2, "%s%s%s"%(self.T_LEFT,self.HORI_EDGE*(self.size.x-2),self.T_RIGHT))
            for y in range(self.pos.y+3,self.pos.y+self.size.y):
                libtcod.console_print(0, self.pos.x, y, "%s%s%s"%(self.VERT_EDGE," "*(self.size.x-2),self.VERT_EDGE))
        libtcod.console_print(0, self.pos.x, self.pos.y+self.size.y, "%s%s%s"%(self.SW_CORNER,self.HORI_EDGE*(self.size.x-2),self.SE_CORNER))



class MenuItem:
    def __init__(self, hotkey, text, fgcolour=libtcod.white, bgcolour=libtcod.black, is_selected=False):
        self.hotkey = hotkey
        self.text = text
        self.fgcolour = fgcolour
        self.bgcolour = bgcolour
        self.is_selected = is_selected

    def draw_at(self, pos):
        x = "( )"
        if self.is_selected:
            x = "(X)"
        libtcod.console_print(0, pos.x, pos.y, " %s. %s %s"%(self.hotkey,self.text,x))


class MenuItemSpacer(MenuItem):
    def __init__(self):
        pass
    def draw_at(self,pos):
        pass


class Menu(Box):
    def __init__(self, pos, size, colour=libtcod.white, title=""):
        Box.__init__(self, pos, size, colour, title)
        self.__items = []

    def add(self, hotkey, text, fgcolour=libtcod.white, bgcolour=libtcod.black):
        self.__items.append( MenuItem(hotkey,text,fgcolour,bgcolour,len(self.__items)==0) )

    def add_spacer(self):
        self.__items.append( MenuItemSpacer() )

    def draw(self):
        Box.draw(self)
        dh = (self.size.y-4) // (len(self.__items)+1)
        h = dh + 2
        for i in self.__items:
            i.draw_at( self.pos+(2,h) )
            h += dh

    def sel_index(self):
        for i in range(len(self.__items)):
            if self.__items[i].is_selected:
                return i
        assert False, "No item selected in menu!"

    def sel_next(self):
        i = self.sel_index()
        if i == len(self.__items)-1:
            return False
        self.__items[i].is_selected = False
        self.__items[i+1].is_selected = True
        if isinstance(self.__items[i+1],MenuItemSpacer):
            return self.sel_next()
        return True

    def sel_prev(self):
        i = self.sel_index()
        if i == 0:
            return False
        self.__items[i].is_selected = False
        self.__items[i-1].is_selected = True
        if isinstance(self.__items[i-1],MenuItemSpacer):
            return self.sel_prev()
        return True

