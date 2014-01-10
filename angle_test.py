#!/usr/bin/env python
from geom_helpers import sprite_angle

def sprite_angle_test():
    test = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]
    for t in test:
        print sprite_angle(t[0], t[1])
        
        
if __name__ == '__main__':    
    sprite_angle_test()
