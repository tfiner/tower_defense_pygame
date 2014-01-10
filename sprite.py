import copy, random
from image_cache import *
from euclid import Vector2
from geom_helpers import *

import path_cache

import data


class Sprite(object):
    def __init__(self, filename, frames, rate_div, pos):
        self.filename = filename
        self.frames = frames
        self.frame_idx = 0
        self.pos = pos
        self.rate_div = rate_div
        self.rate_ticker = 0
        self.is_dead = False

    def Draw(self, surf):
        try:
            img = ImageCache.GetImage(self.filename, self.frames[self.frame_idx])
            surf.blit(img, self.pos, None, 0)
        except IndexError:
            print "sprite %s frames: %s doesn't have index %d" % (self, self.frames, self.frame_idx)            
            
    def Think(self):
       self.NextFrame()
       
    def NextFrame(self):
        self.rate_ticker = (self.rate_ticker + 1) % self.rate_div        
        if 0 == self.rate_ticker:
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
                       
class SpriteOneShot(Sprite):
    def __init__(self, *args, **kwargs):
        super(SpriteOneShot,self).__init__(*args, **kwargs)
    
    def Think(self):
        self.rate_ticker = (self.rate_ticker + 1) % self.rate_div        
        if 0 == self.rate_ticker:
            self.frame_idx = self.frame_idx + 1 
            self.frame_idx = min( self.frame_idx, len(self.frames) - 1) 
            if self.frame_idx == len(self.frames) - 1:
                self.is_dead = True        

def DrawCrosshair( screen, pos, color ):
    pygame.draw.line( screen, color, \
        (pos[0]-10, pos[1]), \
        (pos[0]+10, pos[1]) )
        
    pygame.draw.line( screen, color, \
        (pos[0], pos[1]-10), \
        (pos[0], pos[1]+10) )
    
class Creep(Sprite):
    snd_explosion = None

    def __init__(self, filename, frames, pos, velocity, goal_think):
        self.filename = filename
        self.frames = frames
        self.pos = pos
        self.velocity = velocity
        self.cur_velocity = copy.copy(velocity)
        self.heading = Vector2(0,1)
        self.is_dead = False
        self.frame_idx = 0
        self.life = 10      
        
        img = ImageCache.GetImage(self.filename, self.frames[0])
        self.size = (img.get_width(),img.get_height())

        data.creepFinder.Add(self, pos)

        # Lower and Higher game.theGame.GetCurLevel() goals.
        self.goal = None
        self.goal_think = goal_think
        self.think = 0

        self.local_prev_goal = None
        self.next_head = None

        if Creep.snd_explosion is None:
            Creep.snd_explosion = pygame.mixer.Sound("sounds/73005__Benboncan__Blast.wav")

    def DidCollide(self, r):
        this_rect = pygame.Rect(self.pos, self.size)
        return this_rect.colliderect(r)
        
    def Draw(self, surf):
#        r = pygame.Rect(self.pos, (20,20))
#        pygame.draw.rect(surf, (0,128,0), r, 1)
#        pos = int(self.pos[0]), int(self.pos[1])
#        pygame.draw.circle(surf, (0,128,128), pos, 2, 2)        
                
        try:
            img = ImageCache.GetImage(self.filename, self.frames[self.frame_idx])
            surf.blit(img, self.pos, None, 0)
        except IndexError:
            print "frames: %s doesn't have index %d" % (self.frames, self.frame_idx)
        except TypeError:
            print "TypeError: filename:%s  frames:%s  frame_idx: %d" % \
                (self.filename,self.frames, self.frame_idx)
    
    def FindNewGoal(self, goal_think):
        self.goal_think = self.think + goal_think
        print "signalling creep to find a new goal"

    def Move(self):
        if self.next_head is None or self.is_dead:
            return

        dx,dy = self.next_head
        self.heading = Vector2(dx,dy).normalize()

        self.frame_idx = sprite_angle(dx,dy)
        
        v = Vector2(dx,dy)
        v.normalize()
        v *= self.cur_velocity
        new_pos = ( self.pos[0] + v.x, 
                    self.pos[1] + v.y)            

        cf = data.creepFinder
        cf.Move(self, self.pos, new_pos)
        self.pos = new_pos

        blocking = cf.GetItemsByPos( new_pos )
        grid_pos = data.GetGridCoord( new_pos )

        # Use python's object id as a priority
        # Objects with a higher id yield to those with lower ids.
        velocity_delta = 1.0
        for unit in blocking:
            unit_grid_pos = data.GetGridCoord( unit.pos )
            if id(self) > id(unit) and grid_pos == unit_grid_pos:
                velocity_delta = 0.5
                break

                #return
        # Nothing in the way, accelerate.
        if velocity_delta == 1.0:
            self.cur_velocity = min( self.velocity, self.cur_velocity * 2.0 )
        else: # Slow down, something is blocking.
            self.cur_velocity = max( self.cur_velocity * 0.75, 1/8.0 )


    def ThinkNextGoal(self):
        '''Considers where the creep is supposed to be headed.'''
        
        # Is it time to look for a new goal?
        new_goal = False
        if self.goal is not None:
            d = Distance(self.pos,self.goal)
            if d < 10:
                new_goal = True

        new_goal = new_goal or (self.goal_think is not None and self.think >= self.goal_think)
        if new_goal:
            # print "creep is looking for a new goal"
            self.goal, path = data.pathCache.FindNewGoal(self.goal)
            self.goal_think = None
#            self.local_goal = self.goal
#            print "Found a new goal for %s" % (self)
        else:
            return None

        dx = self.goal[0] - self.pos[0] 
        dy = self.goal[1] - self.pos[1]

        dxr = dx + random.uniform( -7, 7 )
        dyr = dy + random.uniform( -7, 7 )
        extents = data.extents
        new_pos = self.pos[0] + dxr, self.pos[1] + dyr
        if data.IsCoordInRange(new_pos):
            dx,dy = dxr,dyr

        heading = Vector2(dx,dy)
        return heading
     

    def Think(self, goal=None):
        '''Handle death and goals.'''

        if self.is_dead:
            return

        extents = data.extents
        cell_size = data.cell_size

        if self.pos[0] < (extents[0][0]-cell_size[0]) or \
           self.pos[1] < (extents[0][1]-cell_size[0]) or \
           self.pos[0] > extents[1][0] or \
           self.pos[1] > extents[1][1]:
            self.is_dead = True
            return

        self.think += 1

        # @@ REFACTOR TILE
        if Distance(data.end_pt, self.pos) < 5:
            self.Die()
            return # no more thinking, I'm dead!
       
        new_head = self.ThinkNextGoal()
        if new_head is not None:
            self.next_head = new_head
#            angle = boid.RotateInterp( self.heading, new_head )
#            self.next_head = boid.RotateVector( self.heading, angle )
            
        
    def Damage(self,value):
        self.life -= value
        # print "%s took %d damage, has %d life" % (self, value, self.life)        
        if self.life <= 0:
            self.Die()

    def Die(self):
        self.is_dead = True
        self.life = 0
            
        # Remove self from CreepFinder
        data.creepFinder.Remove(self)
#        print "I'm dead", self
        Creep.snd_explosion.play()
        
        data.non_interact_sprites.append( SpriteOneShot("explosion_large.png", range(7), 3, self.pos)  )                       
               
    def __str__(self):
        values = [ "creep pos: %d,%d" % (self.pos[0], self.pos[1]) ]
        values.append( "health: %d" % self.life )
        values.append( "alive: %s" % (not self.is_dead) )
        if self.goal is not None:
            values.append( "goal: %d,%d" % (self.goal[0], self.goal[1]) )
        return " ".join(values)


class Squadron(object):
    '''This class defines formations of units into "squads".
    All movement for these units is encoded here.'''

    def __init__(self, units):
        self.units = units
        self.is_dead = False

    def Think(self):
        # Clean up dead units.
        for u in self.units:
            if u.is_dead:
                print "unit died", id(u)
                self.units.remove(u)
                continue

        self.is_dead = 0 == len(self.units)
        if self.is_dead:
            return

        for u in self.units:
            u.Think()

    def Move(self):
        # The move on units accepts a list of other units it will yield to.
        for idx in xrange(len(self.units)):
            self.units[idx].Move( self.units[:idx] )

        
class Bullet(Sprite):
    snd_impact = None

    def __init__(self, pos, target, velocity, damage, range):
        heading = ( target.pos[0] - pos[0], target.pos[1] - pos[1])        
        
        # 4 is an empty in the middle
        frames = [5,8,7,6,3,0,1,2,5]
        angle_idx = sprite_angle( heading[0], heading[1] )                
        angle_idx = angle_idx 
        super(Bullet,self).__init__("bullet1.png", frames, 1, pos)
        self.frame_idx = angle_idx
        
        # Find the x&y components of velocity 
        self.heading = Vector2(heading[0],heading[1])
        self.heading.normalize()
        self.heading *= velocity
        
        self.damage = damage
        self.start_pos = copy.copy(pos)
        self.range = range

        if Bullet.snd_impact is None:
            Bullet.snd_impact = pygame.mixer.Sound("sounds/74747__jordanthebamf__CERAMIC_PING_04.wav")
                
    def Think(self):       
        if self.is_dead:
            return        
        # update position        
        self.pos = (self.pos[0] + self.heading.x, 
                    self.pos[1] + self.heading.y)
        
        # Replace with world check.
        if self.pos[0] < 0 or \
           self.pos[1] < 0 or \
           self.pos[0] > 640 or \
           self.pos[1] > 480:
               self.is_dead = True
               
        # check for collision
        #  explode
        r = pygame.Rect(self.pos[0]+4, self.pos[1]+4, 3, 3)
        creeps = data.creepFinder.GetItemsByPos(self.pos)
        for c in creeps:
            if c.DidCollide(r):
                Bullet.snd_impact.play()
                data.non_interact_sprites.append( SpriteOneShot("explosion_small.png", range(7), 3, self.pos)  )
                # Create an explosion
                c.Damage(self.damage)
                self.is_dead = True
                # print "damaged creep"
                break
                      
        # check for range
        #  explode
        if not self.is_dead and Distance(self.start_pos,self.pos) > self.range:
            data.non_interact_sprites.append( SpriteOneShot("explosion_small.png", range(7), 3, self.pos)  )
            self.is_dead = True
                
        
    def Draw(self, surf):
        if self.is_dead:
            return
        super(Bullet,self).Draw(surf)
        # r = pygame.Rect(self.pos[0]+4, self.pos[1]+4, 3, 3)
        # pygame.draw.rect(surf, (255,0,0), r, 1)
        

TOWER_STATE_FIND_TARGET = 0
TOWER_STATE_SHOOT       = 1
TOWER_STATE_UPGRADE     = 2

tower_frames = {
    # key:   class name
    # By state idx, a list of 
    # [ (filename, [list of frame nums], rate), (filename, ...) ]
    'Turret1':[('turretsv2.png', range(8), 8)],
    'TestTurret':[('turretsv2.png', range(8), 8)]    
}


class Turret1(object):
    shoot_sound = None

    def __init__(self, pos):       
        self.state = TOWER_STATE_FIND_TARGET
        self.frame_idx = 0
        self.fire_ticker = 0
        self.fire_rate = 30
        self.fire_damage = 5
        self.pos = copy.copy(pos)
        self.range = 32
        self.level = 1
        
        self.fire_pos = [
            (15,5), (20,5), (25,12), (25,23), 
            (15,23), (8,23), (8,12), (12,6)
        ]

        creep_idx = data.creepFinder.GetKey(self.pos)
        
        self.offsets = [
            (-1, 1),(0, 1), (1, 1),
            (-1, 0),(0, 0), (1, 0),
            (-1,-1),(0,-1), (1,-1)
        ]
        
        self.creep_idxs = [ (creep_idx[0]+ox,creep_idx[1]+oy) for ox,oy in self.offsets ]

        data.towerFinder.Add(self, self.pos)

        if Turret1.shoot_sound is None:
            Turret1.shoot_sound = pygame.mixer.Sound("sounds/39040__wildweasel__hv_uzi.wav")
        
    def GetDamagePerSec(self):
        return self.fire_rate / 60.0 * self.fire_damage
        
    def GetFrame(self):
        return tower_frames[self.__class__.__name__][self.state]
        
    def SetFrameIdx(self, new_idx):
        frames = self.GetFrame()
        self.frame_idx = new_idx % len(frames[1])

    def CanUpgrade(self):
        return self.level < 3

    def Upgrade(self):
        self.level += 1
        if self.level <= 3:
            self.range += 16
            self.fire_damage += 1
            self.fire_rate += 10
    
    def Draw(self, surf):
        draw_pos = self.pos[0]-10, self.pos[1]-10

        # draw_pos = self.pos[0], self.pos[1]
        frames = self.GetFrame()
        img = ImageCache.GetImage(frames[0], frames[1][self.frame_idx])
        surf.blit(img, draw_pos, None, 0)
               
    def Think(self):
        targets = data.creepFinder.GetItemsByKeys(self.creep_idxs)
        if len(targets) == 0:
            return
            
        # Look for targets
        closest = None
        closest_val = None
        for t in targets:
            val = Distance(self.pos, t.pos)
            if closest is None or val < closest_val:
                closest = t
                closest_val = val
        
        dx = closest.pos[0] - self.pos[0]
        dy = closest.pos[1] - self.pos[1]
        sa = sprite_angle(dx,dy)
        new_idx = sa + 2
        self.SetFrameIdx( new_idx )

        # Fire if in range and within fire rate        
        self.fire_ticker = (self.fire_ticker + 1) % self.fire_rate        
        if 0 == self.fire_ticker:
            if closest_val < self.range:
                Turret1.shoot_sound.play()
                pos = ( self.pos[0] + self.fire_pos[self.frame_idx][0] - 10, 
                        self.pos[1] + self.fire_pos[self.frame_idx][1] - 10)
                b = Bullet(pos, closest, velocity=1.5, damage=1, range=self.range)
                data.sprites.append(b)
                
    def NextFrame(self):
        pass
        #if self.state == TOWER_STATE_FIND_TARGET:
            # pass # Frame set by Think()
        # elif self.state == TOWER_STATE_SHOOT:

class NullObject(object):
    def __init__(self, pos):
        self.pos = pos
            
class TestTurret(Turret1):
    def __init__(self,*args,**kwargs):
        super(TestTurret,self).__init__(*args,**kwargs)
        self.range = 32

    def Draw(self,surf):        
        # r = pygame.Rect(self.pos[0]-10,self.pos[1]-10, 40, 40)
        pygame.draw.rect(screen, (0,128,128), r, 1)
        super(TestTurret,self).Draw(surf)
        
        # pygame.draw.line(, color, start_pos, end_pos, width=1)

    def Think(self):
        global sprites

        # Fire if in range and within fire rate        
        self.fire_ticker = (self.fire_ticker + 1) % self.fire_rate        
        if 0 == self.fire_ticker:
            target = pygame.mouse.get_pos()
            
            dx = target[0] - (self.pos[0] - 10)
            dy = target[1] - (self.pos[1] - 10)
            sa = sprite_angle(dx,dy)
            new_idx = sa + 2
            self.SetFrameIdx( new_idx )

            pos = ( self.pos[0] + self.fire_pos[self.frame_idx][0] - 10, 
                    self.pos[1] + self.fire_pos[self.frame_idx][1] - 10)
            b = Bullet(pos, NullObject(target), velocity=1.5, damage=1, range=self.range)
            data.sprites.append(b)

