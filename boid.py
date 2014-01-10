# Boid implementation by Tim Finer for CPSC-481, Spring 2007
#
# $Id: boid.py 41 2010-02-10 06:48:01Z tim $
#

# Library imports
import copy, pygame
from euclid import Vector2, Matrix3
from random import randint, seed, random
from math import *

# Convenient Constants
MAX_ANGLE_ROTATION = pi / 30
MIN_ANGLE_ROTATION = pi / 180

BLACK = 0, 0, 0
GREEN = 0, 255, 0
WHITE = 255, 255, 255
SKY_BLUE = 0, 128, 208
BLUE = 0, 0, 255
RED = 255, 0, 0
BOID_SIZE = 20
BOID_FOV = pi/3 # 60 degrees
MAX_VELOCITY = 32.0
MIN_VELOCITY = 0.125

# Experimental random velocity.  This didn't add anything to the simulation 
# so I commented out the code for it.
MAX_RND_VELOCITY = 4.0
MIN_RND_VELOCITY = 0.0

# The Simulation state in the form of a Python Dictionary (a map in other languages).
state = {
    "velocity" : 1,
    "cluster" : False,
    "avoid" : True,
    "align" : False,
    "grid" : False,
    "debug_think" : True,
    "debug_avg" : False,
    "boids" : 20,
    "fullscreen" : False,
    "wrap" : True,
    "flee_range" : BOID_SIZE * 2,
    "rnd_velocity" : 0.5,
    "info" : True
}


# 2D Helper Routines.

def Dist( ptA, ptB ):
    '''Return the distance from ptA to ptB'''
    x = (ptB.x - ptA.x)
    y = (ptB.y - ptA.y)
    return sqrt(x ** 2 + y ** 2)
    
    
def RotateVector( vec, theta ):
    '''Rotate a vector theta radians.'''
    theta = -theta
    sin_theta = sin( theta )
    cos_theta = cos( theta )
    new_x = (vec.x * cos_theta) + (vec.y * sin_theta)
    new_y = (vec.y * cos_theta) - (vec.x * sin_theta)    
    return Vector2(new_x,new_y)
    

def RotateInterp( src, dest ):
    '''Find the shortest angle to rotate src to dest.'''
    src_angle = atan2( src.y, src.x )
    dest_angle = atan2( dest.y, dest.x )

    two_pi = 2 * pi

    # normalize from -pi to pi to 0 to 2pi
    if src_angle < 0:
        src_angle = two_pi - fabs(src_angle)

    if dest_angle < 0:
        dest_angle = two_pi - fabs(dest_angle)

    alpha = dest_angle - src_angle

    degs = [ "%f" % degrees(a) for a in [src_angle, dest_angle, alpha] ]
#    print ", ".join(degs)

    # If the rotation is < 180 degrees, then it's the shortest rotation.
    if fabs(alpha) > pi:
#        print "    pre alpha", degrees(alpha)
        alpha = -two_pi + fabs(alpha)
#        print "    post alpha", degrees(alpha)

    if False:
        alpha = min( alpha, MAX_ANGLE_ROTATION )
        alpha = max( alpha, -MAX_ANGLE_ROTATION )
        if fabs(alpha) < MIN_ANGLE_ROTATION:
            alpha = 0

    assert fabs(alpha) <= pi

    return alpha
    
def RotateInterpOld( src, dest ):
    '''Rotate from vector src to vector dest clipping the amount of 
    rotation to MAX_ANGLE_ROTATION <= angle <= MAX_ANGLE_ROTATION.'''
    
    dest_angle = atan2( dest.y, dest.x )
    src_angle = atan2( src.y, src.x )
   
    alpha1 = dest_angle - src_angle
    alpha2 = AngleDiff( src, dest )

    alpha = min( alpha1, alpha2 )
    if alpha > pi:
        alpha = pi - alpha
        
    # print "a1 %f  a2 %f" % (alpha1, alpha2)
    
    alpha = min( alpha, MAX_ANGLE_ROTATION )
    alpha = max( alpha, -MAX_ANGLE_ROTATION )
    if fabs(alpha) < MIN_ANGLE_ROTATION:
        alpha = 0

    return alpha

def cosTheta( v1, v2 ):
    '''Returns the angle between two vectors in radians.'''
    
    ret = 0.0
    ptot2 = v1.magnitude_squared() * v2.magnitude_squared()
    if ptot2 <= 0.0:
        ret = 0.0
    else:
        ret = v1.dot(v2) / sqrt(ptot2)
        if ret > 1.0: 
            ret =  1.0
        elif ret < -1.0:
            ret = -1.0
    return ret


def AngleDiff( v1, v2 ):
    return atan2(v2.y,v2.x) - atan2(v1.y,v1.x)

    
def AngleDiffOld( v1, v2 ):
    '''A front end for cosTheta that matches another method used before.'''
    return acos( cosTheta(v1, v2) ) 
    
    
'''
    FowlerAngle returns a value from 0-8, this is used to display the prerotated
    sprite image.  I took the original C code from 
    http://local.wasp.uwa.edu.au/~pbourke/geometry/fowler/
    and ported it to Python.  Below is the original comment:
    
    This function is due to Rob Fowler.  Given dy and dx between 2 points
    A and B, we calculate a number in [0.0, 8.0) which is a monotonic
    function of the direction from A to B. 
    
    (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0) correspond to
    (  0,  45,  90, 135, 180, 225, 270, 315, 360) degrees, measured
    counter-clockwise from the positive x axis.
'''
def FowlerAngle(dy,dx):    
    adx = 0.0
    ady = 0.0    # Absolute Values of Dx and Dy

    # Compute the absolute values.
    if dx < 0.0:
        adx = -dx
    else:
        adx = dx

    if dy < 0.0:
        ady = -dy
    else:
        ady = dy

    code = 0     # Angular Region Classification Code        
    if adx < ady:
        code = 1
    else:
        code = 0        
    
    if dx < 0.0: 
        code += 2
    
    if dy < 0.0:  
        code += 4

    ret_val = -1.0
    if code == 0:
        if dx==0:
            ret_val = 0.0
        else:
            ret_val = ady/adx                         # [  0, 45]
    elif code == 1: ret_val = (2.0 - (adx/ady))       #  ( 45, 90] 
    elif code == 3: ret_val = (2.0 + (adx/ady))       # ( 90,135) 
    elif code == 2: ret_val = (4.0 - (ady/adx))       # [135,180] 
    elif code == 6: ret_val = (4.0 + (ady/adx))       # (180,225] 
    elif code == 7: ret_val = (6.0 - (adx/ady))       # (225,270) 
    elif code == 5: ret_val = (6.0 + (adx/ady))       # [270,315) 
    elif code == 4: ret_val = (8.0 - (ady/adx))       # [315,360)
    
    assert( ret_val >= 0 and ret_val <= 8 )
    return ret_val


# Given a list of boids, return their average heading                    
def AvgHead( boids ):
    assert( len(boids) )
    heading = Vector2(0,0)
    first = True
    
    for b in boids:    
        if first:
            first = False
            heading.x = b.heading.x
            heading.y = b.heading.y
        else:
            heading.x += b.heading.x
            heading.y += b.heading.y
    
    heading /= len(boids)
    heading.normalize()
    return heading

# Given a list of boids, return their average position.
def AvgPos( boids ):    
    assert( len(boids) )
    position = None
    first = True
    for b in boids:    
        if first:
            first = False
            position = copy.copy(b.position)
        else:
            position.x += b.position.x
            position.y += b.position.y
    
    position /= len(boids)
    return position
    
# Draw a cross hair for the average position in black, and
# the average heading in red.
def DrawAvg( screen, avg_pos, avg_head ):
    pygame.draw.line( screen, GREEN, \
        (avg_pos.x-10, avg_pos.y), \
        (avg_pos.x+10, avg_pos.y) )
        
    pygame.draw.line( screen, GREEN, \
        (avg_pos.x, avg_pos.y-10), \
        (avg_pos.x, avg_pos.y+10) )
        
    pygame.draw.line( screen, RED, \
        (avg_pos.x, avg_pos.y), \
        (avg_pos.x+avg_head.x*20, avg_pos.y+avg_head.y*20) )
    
    
    
class Boid(object):
    '''Tim Finer's Boid class, contains the 3 rules for steering behavoir.
    Boids move by multiplying their header + their velocity and adding the
    resultant vector to it's position.'''
    
    def __init__( self, position, heading ):
        '''Copy position and header, set up next heading.'''
        self.position = copy.copy(position)
        self.heading = copy.copy(heading)
        self.heading.normalize()
        self.next_heading = copy.copy( self.heading )
        self.next_alpha = 0
        #~ self.velocity = state["velocity"]
        
    def __repr__(self):
        '''This function returns a string with the state of the boid in human readable terms.'''
        return "pos: %s   head: %s" % (self.position, self.heading)

    # Rule 1.  Separation: Avoid crowding with others.
    def AvoidCrowding( self, others ):
        '''Input a list of other boids, see if they are within range, and if they are
        add the desired rotation to next turn's rotation.'''
        
        # A list of flee vectors, this is saved for graphical debugging use only.
        self.fleevs = []
        flee = None       
        for b in others:
            if b == self:
                continue
                
            # Find the vector away from the boid in question.
            delta_head = b.position - self.position          
              
            # Is this boid worth considering?
            # If so, then add the direction away from it to the flee vector.
            dist = Dist( self.position, b.position )
            if dist < state["flee_range"]:
                self.fleevs.append( delta_head )
                if flee is None: 
                    flee = -delta_head
                else:
                    flee -= delta_head
            
        # If there is a flee vector, find out how much rotation is needed to flee
        # and save that angle in the next rotation variable.
        if flee is not None:
            flee.normalize()
            self.next_alpha += RotateInterp( self.heading, flee )
                
    # Rule 2.  Alignment: Steer towards others' average heading. 
    def AlignHeading( self, new_heading ):
        '''The new heading is given, find the angle needed to accomplish that and 
        add it to the next rotation variable.'''
        
        delta_angle = AngleDiff( self.heading, new_heading )
        
        # If the boid is close enough, don't bother adjusting.
        if delta_angle > (BOID_FOV/2):      
            self.next_alpha += RotateInterp( self.heading, new_heading )            
        
    # Rule 3. Cohesion: Steer towards average position.
    def Cluster( self, avg_pos ):
        '''Average position is given, find the angle needed to steer towards it and 
        add that to the next rotation.'''
        
        dist_to_avg = Dist( self.position, avg_pos )
        if dist_to_avg > (state["flee_range"] * 1.25):
            new_heading = avg_pos - self.position
            new_heading.normalize()
            self.next_alpha += RotateInterp( self.heading, new_heading )

    # Move the Boid by adding the velocity * heading to its current position.
    def Move( self, bounds ):
        '''Uses velocity, heading and position to find a new position.  Also uses
        bounds to wrap around or reset itself randomly.'''
        
        # If we have a pending rotation, then do it and zero it out.
        if fabs(self.next_alpha) > MIN_ANGLE_ROTATION:
            # print "move, alpha %f" % self.next_alpha
            self.heading = RotateVector( self.heading, self.next_alpha )            
            self.heading.normalize()
            self.next_alpha = 0

        # Random velocity experiment - ignore these lines.
        # seed()
        # velocity = state["velocity"] * (state["rnd_velocity"] * random())
        
        # Move the boid.
        self.position += self.heading * state["velocity"]
        
        # The default state is to wrap the boids around the screen edges.
        # The initial mode just made 
        xrange = bounds[0]
        yrange = bounds[1]
        margin = BOID_SIZE
        if state["wrap"]:
            if self.position.x < -margin:
                self.position.x = xrange
            elif self.position.x > (xrange+margin):
                self.position.x = -margin
            if self.position.y < -margin:
                self.position.y = yrange
            elif self.position.y > (yrange+margin):
                self.position.y = -margin        
        else:
            if self.position.x < -margin or \
                self.position.x > (xrange+margin) or \
                self.position.y < -margin or \
                self.position.y > (yrange+margin):
                    self.position = Vector2(randint(0, xrange), randint(0, yrange) )
                    self.heading = Vector2(randint(-xrange, xrange),randint(-yrange,yrange))
                    self.heading.normalize()
                    self.next_alpha = 0
                        
    # This is the function where all of the rules are applied.
    def Think( self, others, avg_pos, avg_head ):        
        self.next_alpha = 0
        
        # Experimental random velocity - please ignore this.
#        self.velocity += state["rnd_velocity"] * (random()-.5)
#        self.velocity = min(self.velocity, MAX_VELOCITY)
#        self.velocity = max(self.velocity, MIN_VELOCITY)
        
        if state["align"] and avg_head is not None:
            self.AlignHeading( avg_head )
            
        if state["cluster"] and avg_pos is not None:
            self.Cluster( avg_pos )
            
        if state["avoid"]:
            self.AvoidCrowding( others )

    # Debug drawing.
    def Draw( self, surface ):
        if state["debug_think"]:        
            end = self.position + (self.heading * BOID_SIZE)
            pygame.draw.line( surface, GREEN, 
                (self.position.x, self.position.y), 
                (end.x, end.y) )

            pygame.draw.circle( surface, (255,0,0), 
                (int(self.position.x), int(self.position.y)), 
                int(state["flee_range"]/2), int(1) )
                
            pygame.draw.circle( surface, (255,0,0), 
                (int(self.position.x), int(self.position.y)), 
                int(state["flee_range"]*1.25/2), int(1) )                
            
            try:
                for f in self.fleevs:
                    f.normalize()
                    end = self.position + (f * state["flee_range"])
                    pygame.draw.line( surface, GREEN, 
                        (self.position.x, self.position.y), 
                        (end.x, end.y) )            
            except AttributeError:
                pass
                    
        if False:
            next_heading = RotateVector( self.heading, self.next_alpha )
            next_heading.normalize()
            end = self.position + (next_heading * 40)            
            pygame.draw.line( surface, (255,0,0), 
                (self.position.x, self.position.y), 
                (end.x, end.y) )
            
    # Return a boid with random initial position and heading.
    @staticmethod
    def Random(xrange,yrange):
        seed()
        return Boid( Vector2(randint(0, xrange),randint(0,yrange)),
            Vector2(randint(-xrange, xrange),randint(-yrange,yrange)) )
        
        
if __name__ == '__main__':
    pass
    
