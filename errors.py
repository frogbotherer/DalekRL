#!/usr/bin/env python3


class DalekError(Exception):
    pass

class GameOverError(DalekError):
    pass

class LevelWinError(DalekError):
    pass

class InvalidMoveError(DalekError):
    pass

class TodoError(DalekError):
    pass
