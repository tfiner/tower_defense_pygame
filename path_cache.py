#!/usr/bin/env python
#

import sys, math
from pygame.locals import *
import pygame
from copy import copy

from geom_helpers import *
from astar import AStar

import navi_graph
import data

def Simplify(path):
    '''Simplifies paths passed to it by minimizing the angle difference between path cells.'''

    ANGLE_EPSILON = 0.392699082 # ~ 22.5 degrees

    if len(path) <= 2:
        return path

    new_path = []
    angle = None

    for i in xrange(1,len(path)):
        p0 = path[i-1]
        p1 = path[i] 
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        if angle is None:
            angle = math.atan2(dy,dx)
            new_path.append(p0)
            new_path.append(p1)
            continue

        new_angle = math.atan2(dy,dx)
        if abs(new_angle - angle) > ANGLE_EPSILON:
            new_path.append(p1)
            angle = new_angle

    new_path.append( path[-1]  )

    return new_path 


# 8 neighbors for rectangular grids.
# xl,yu     x,yu    xr,yu
# xl, y     x, y    xr, y
# xl,yd     x,yd    xr,yd
#offsets = [
#    (-1,  1), (0,  1),  (1,  1),
#    (-1,  0),           (1,  0),
#    (-1, -1), (0, -1),  (1, -1),
#]

GRID_NEIGHBORS = [
              (0,  1),
    (-1,  0),           (1,  0),
              (0, -1),
]
        
def GetNeighborsDiagonal( eval_func ):       
    '''Eval func takes an offset (one of the GRID_NEIGHBORS), and returns True or False.'''
    # if 0 or 1 are False, add neighbor (-1, 1)
    # if 0 or 2 are False, add neighbor ( 1, 1)
    # if 1 or 3 are False, add neighbor (-1,-1)
    # if 2 or 3 are False, add neighbor ( 1,-1)
    diag_rules = {
        (0,1):(-1, 1), 
        (0,2):( 1, 1),
        (1,3):(-1,-1),
        (2,3):( 1,-1) 
    }

    neighbors = []
    for neighbors,off in diag_rules.items():
        if not eval_func(GRID_NEIGHBORS[neighbors[0]]) or \
           not eval_func(GRID_NEIGHBORS[neighbors[1]]):
            neighbors.append(off)


def unique(seq, idfun=None):  
    # order preserving 
    if idfun is None: 
        def idfun(x): return x 

    seen = {} 
    result = [] 
    for item in seq: 
        marker = idfun(item) 
        if marker in seen: 
            continue 
        seen[marker] = 1
        result.append(item) 
    return result


class PathCache(object):
    '''The path cache holds a hierarchy of paths and goals.'''
    
    def __init__(self, grid_size):      
        self.ClearCache()
        # b  ->    white
        self.colors = [ (c,c,255) for c in xrange(0,256) ]
        self.astar_vals = {}
        self.astar_max = self.astar_min = 0
        self.dead_ends = set()
        self.grid_size = grid_size
        self.creep_paths = []
     
        
    def ClearCache(self):
        self.creep_paths = []             
        
    def SetAStarMinMax(self):
        self.astar_min = None
        self.astar_max = None
        for cost in self.astar_vals.itervalues():
            if self.astar_min is None or cost < self.astar_min:
                self.astar_min = cost
            if self.astar_max is None or cost > self.astar_max:
                self.astar_max = cost
            

    def FindNewGoal(self, old_goal):
        '''Returns a new goal point, given the old goal
        If the old goal can't be found, the nearest point is returned.'''

        assert len(self.creep_paths)
        assert len(self.creep_paths[0])
        
        if old_goal is None:
            return self.creep_paths[0][0], self.creep_paths[0]

        closest = self.creep_paths[0][-1]
        closest_dist = Distance(self.creep_paths[0][-1], old_goal)
        new_goal = None

        src_path = None
        for p in self.creep_paths:
            for idx in xrange(len(p)-1):
                if p[idx] == old_goal:
                    new_goal = p[idx+1]
                    src_path = p
                    # print "found old goal %s, returning new goal %s (%d total goals)" % \
                    #    (old_goal, new_goal, len(p))
                    break
                dist = Distance(p[idx], old_goal)
                if dist < closest_dist:
                    closest_dist = dist
                    closest = p[idx]
                    src_path = p

        # print "new goal, closest %s at %f" % (closest, closest_dist)
        # Adjacent.                
        if new_goal is None and closest_dist < 20:
            new_goal = closest

        if new_goal is None:
            graph = navi_graph.navi_graph
            print "A*: %s to %s" % (old_goal, closest)
            new_path, vals = AStar( graph, old_goal, data.end_pt )
            if new_path is None or len(new_path) < 2:
                print new_path
                return data.end_pt

            # Filter out duplicate entries.
            new_path = unique( new_path )  

            print "new path: ", new_path
            assert len(new_path) >= 2
            src_path = new_path

            new_goal = new_path[1]

            self.creep_paths.append(new_path)
            print "Used A* to find new goal (%d total goals)" % \
                 len(new_path)

            data.gridCost.AddCostPath( new_path, 500)

        if new_goal is None:
            new_goal = closest
            print "found closest %s, returning new goal %s (%d total goals)" % \
                (closest, new_goal, len(self.creep_paths[0]))

        return new_goal, src_path

    def ResetPath(self, start, end):
        self.creep_paths = []
        self.GetPath(start,end)
        
    def GetPath(self, p0, p1):
        '''Returns the path and the path index for the given pt.
        Returns an empty path, None if no path could be found.'''
        
        start = data.GetGridCoord( p0 )
        end = data.GetGridCoord( p1 )
        print "looking for %s -> %s" % (start, end)
        
        found_path = []
        found_idx = None
        for path in self.creep_paths:
#            print "   path %s:%s" % (path[0],path[-1])
            if path[0] == start and path[-1] == end:
                found_path = path
                found_idx = 0
                break
            else:
                for pt_idx in xrange(len(path)):
                    if path[pt_idx] == start:
                        found_idx = pt_idx+1
                        found_path = path
                        break
                    
        if len(found_path) == 0:
#            print "a* calc miss, recalc %s -> %s" % (start, end)
            graph = navi_graph.navi_graph
            try:
                found_path, self.astar_vals = AStar( graph, start, end )
                self.SetAStarMinMax()
                if len(found_path):
 #                   print "   new path %s:%s" % (found_path[0],found_path[-1])
                    found_idx = 0
                    self.creep_paths.append(found_path)

                
            except ValueError:
                pass
        else:
#            print "a* calc cache hit %s -> %s" % (start, end)
            pass

        # print "returned %d dead ends" % len(self.dead_ends)                        
        return found_path, found_idx

    
    def Draw(self, surf):
        delta = 0
        if self.astar_min != self.astar_max:
            delta = self.astar_max - self.astar_min

            for pt,cost in self.astar_vals.iteritems():
                idx = int(((cost - self.astar_min) * 255) / delta);
                if idx > 255:
                    print "idx: %d  cost %f, [%f-%f]" % (idx, cost, self.astar_min, self.astar_max)
                    assert False
                r = pygame.Rect( pt, (20, 20) )
                surf.fill(self.colors[idx], r)
                
        if len(self.creep_paths):
            for p in self.creep_paths[0]:
                color = (128,0,0)
                if delta != 0 and p in self.astar_vals:
                    cost = self.astar_vals[p]
                    idx = int(((cost - self.astar_min) * 255) / delta);
                    color = self.colors[idx]

                r = pygame.Rect( (p), (20, 20) )
                surf.fill(color, r)
                pygame.draw.rect(surf, (0,0,0), r, 3)
                
            for pi in xrange(1,len(self.creep_paths)):
                for p in self.creep_paths[pi]:
                    r = pygame.Rect( p, (20, 20) )
                    pygame.draw.rect(surf, (128,128,0), r, 1)            

    def __str__(self):
        str = "%d paths:\n" % len(self.creep_paths)
        for p in self.creep_paths:
            str += "%s\n" % p
        return str

if __name__ == '__main__':
    mg = MultiLevelGrid( (640,480), (20,20), False)
    mg.InitLevel(8)
    mg.InitLevel(4)

    for s,m in mg.levels:
        print s
