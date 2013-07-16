#!/usr/bin/env python3


class DalekError(Exception):
    pass

class GameOverError(DalekError):
    pass

class LevelWinError(DalekError):
    pass

class InvalidMoveError(DalekError):
    """stop execution and end turn (e.g. instead of moving to locker tile, interact with it)"""
    pass

class InvalidMoveContinueError(InvalidMoveError):
    """stop execution but continue turn (e.g. instead of losing a turn for bumping a wall, continue"""
    pass

class TodoError(DalekError):
    pass
