import math

def DistCompare( a, b ):
    '''
        Return the distance from ptA to ptB, w/out sqrt.
        Use this when comparing pts against one another, but not 
        to find the distance between points.
    '''
    x = b[0] - a[0]
    y = b[1] - a[1]
    return x ** 2 + y ** 2

def Distance( a, b ):
    x = b[0] - a[0]
    y = b[1] - a[1]
    return math.sqrt(x ** 2 + y ** 2)
    
TWO_PI = 2.0 * math.pi
SPRITE_ANGLE_ROTATION = TWO_PI / 8.0
SPRITE_ANGLE_OFFSET = SPRITE_ANGLE_ROTATION / 2.0
SPRITE_ANGLES = [] # stored as a list of tuples of (min angle, max angle, sprite idx)

# The specials
SPRITE_ANGLES.append((0, SPRITE_ANGLE_OFFSET, 0))
SPRITE_ANGLES.append((TWO_PI - SPRITE_ANGLE_OFFSET, TWO_PI, 0))

i = 1
a = SPRITE_ANGLE_ROTATION
while a < TWO_PI:
    SPRITE_ANGLES.append((a-SPRITE_ANGLE_OFFSET, a+SPRITE_ANGLE_OFFSET, i))
    a += SPRITE_ANGLE_ROTATION
    i += 1
    
# print SPRITE_ANGLES

def sprite_angle( dx, dy ):
    angle = math.atan2(dy,dx)
    if angle < 0:
        angle += TWO_PI
    
    sa = None
    for a in SPRITE_ANGLES:
        if angle >= a[0] and angle < a[1]:
            sa = a[2]
            break
            
    return sa    
