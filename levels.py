import pygame
import datetime as dt
import sprite
import data

class LevelBase(object):
    def __init__(self):
        self.cell_size = (20,20)
        self.next_wave = None
        self.update = 0
        self.wave = 0
        self.next_wave = None
        self.last_update = None
        data.extents = ((20,20),(640-80,460))

    def Draw(self, surf):
        surf.blit(self.image, (0,0), None, 0)

        if data.selected:
            t = data.selected
            pygame.draw.circle(surf, (255,0,0), 
                               (t.pos[0]+10,t.pos[1]+10), t.range, 3)


    def Update(self):
        self.update += 1
        now = dt.datetime.now()
        if self.wave is None:
            return

        if self.next_wave is None:
            self.next_wave = now + \
                dt.timedelta(seconds=self.times[self.wave])

        if self.last_update is None:
            self.last_update = now

        delta = now - self.last_update
        if delta.seconds >= 1:
            next_time = self.next_wave - now
            print "seconds until next wave: %d" % next_time.seconds
            self.last_update = now

        if now > self.next_wave:
            self.NextWave()

    def IsFinished(self):
        return self.wave >= len(self.times)

    def NextWave(self):
        pass

class Level1(LevelBase):
    def __init__(self):
        super(Level1,self).__init__()
        self.image = pygame.image.load("level_snow.png")
        data.start_pt = (540,40)
        data.end_pt = (80,340)
        self.times = [ 10,10 ]

        the_base = sprite.Sprite("base.png", range(7), 15, (80,340))
        data.sprites.append( the_base )


    def NextWave(self):
        if self.wave is None:
            return

        self.wave += 1
        self.next_wave = None
        if self.wave == 1:
            print "wave1"

        elif self.wave == 2:
            print "wave2"
            self.wave = None

