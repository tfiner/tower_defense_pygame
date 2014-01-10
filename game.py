#!/Usr/bin/env python
#


# Level factory.

import levels

class LevelIterator(object):
    def __init__(self, levels, cur_level):
        self.levels = levels
        cur_level = -1
        self.cur_level = cur_level

    def next(self):
        self.cur_level += 1
        if self.cur_level == len(self.levels):
            raise StopIteration
        return self.levels[self.cur_level]

class Game(object):
    '''A container for levels.'''

    def __init__(self):
        self.cur_level = 0
        self.levels = [ levels.Level1() ]

    def __iter__(self):
        return LevelIterator(self.levels, self.cur_level)

    def GetCurLevel(self):
        return self.levels[self.cur_level]
   
theGame = Game()

if __name__ == '__main__':
    print "main"
    g = theGame
    for level in theGame:
        while not level.IsFinished():
            level.Update()
#        print "level", level
#        print "g level", g.GetCurLevel()
