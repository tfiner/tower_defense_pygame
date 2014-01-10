# The A* algorithm

import math
from heapq import heappush, heappop
from geom_helpers import *

ASTAR_DEBUG = False
debug_msgs = []
def DebugMsg(msg):
    if ASTAR_DEBUG:
        global debug_msgs
        debug_msgs.append(msg)

class Graph(object):
    def GetCost(self, pt):
        '''Given a point, return the cost.'''
        pass
    
    def GetNeighbors(self, pt):
        '''Return the neighbors of a given point.'''
        pass    
       

# Default functions
def AStarH( start_pt, end_pt ):
    '''Uses distance.'''
            
    if start_pt[0] == end_pt[0]:
        D = 1.0        
    elif start_pt[1] == end_pt[1]:
        D = 1.0
    else: # diagonal line
        D = 1.41421356237

    absx = abs(start_pt[0] - end_pt[0])
    absy = abs(start_pt[1] - end_pt[1])
        
    return D * (absx + absy)
      


# A*:  F = G + H
def AStarF( from_pt, to_pt, dest_pt, AStarG ):
    # I doubled it to be safe to 64.
    # tie_breaker_h = AStarH(from_pt, to_pt)
    # return AStarG[to_pt] + tie_breaker_h
    # return AStarG[to_pt] + AStarH(from_pt, to_pt) + AStarH(to_pt, dest_pt)
    return AStarG[to_pt] + AStarH(to_pt, dest_pt)

    

def AStar( graph, start_pt, end_pt ):
    '''graph is an instance of a Graph class'''
    
    # print "AStar: %s - %s" % (start_pt, end_pt)
    
    # The key is the currently considered end_pt.
    # The value is the cost from start_pt to the key.
    AStarG = {start_pt:0}        
    open_list = []
    open_test = set()
    closed_list = set()
    closed_list.add(start_pt)
    parent = start_pt

    if True:
#    try:
        while ( parent != end_pt ):
           
           parent_cost = AStarG[parent]
           neighbors = graph.GetNeighbors(parent)
           
           # print "Neighbors " , neighbors              
           
           for n in neighbors:
               if n is not None and \
                  n not in open_test and \
                  n not in closed_list:
                   g = parent_cost + graph.GetCost( parent, n )
                   AStarG[n] = g
                   f = AStarF( parent, n, end_pt, AStarG )
                   # print "Adding neighbor %s, cost: %d" % (n,f)               
                   heappush( open_list, (f, n) )
                   open_test.add(n)
                   
           parent = heappop(open_list)[1]
           # print "Selected from open %s, cost: %d" % (parent,f)               
           
           closed_list.add(parent)
           open_test.remove(parent)
#     except IndexError:
#         print "a* caught an index err, no path"
#         return []

    msgs = []                              

    DebugMsg("X" * 80)
    DebugMsg("Walking backwards, from %s to %s " % (end_pt,start_pt))

    dead_ends = set()
    path = [end_pt]
    pt = end_pt
    min_val = None    
    while pt != start_pt:
        neighbors = graph.GetNeighbors(pt)
        DebugMsg( " ".join(["    %d,%d" % (n) for n in neighbors ]))
        # print "    %s # of neighbors: %d" % (pt, len(neighbors))
        next_pt = None
        for n in neighbors:
            # Have we already used this point?
            if n in path:
                DebugMsg("    rejecting %d,%d in path" % (n))
                continue
            elif n in dead_ends:
                DebugMsg("    rejecting %d,%d in dead ends" % (n))
                continue
            elif n not in AStarG:
                DebugMsg("    rejecting %d,%d not in AStarG" % (n))
                continue            
            elif (min_val is not None and AStarG[n] > min_val):
                DebugMsg("    rejecting %s (%f > min %f)" % (n,AStarG[n],min_val))
                continue
                       
            next_pt = n
            min_val = AStarG[n]
            DebugMsg("    new min at %s %f" % (n,min_val))

        try:
            if next_pt is None:
                DebugMsg("    dead end %d,%d" % (pt))
                dead_ends.add(pt)
                old_pt = path.pop()
                DebugMsg("    removing pt %s popped %s" % (pt,old_pt))
                if old_pt == pt:
                    pt = path.pop()
                else:
                    pt = old_pt
                    
                min_val = AStarG[pt]
                DebugMsg("    backed up to %d,%d val %f" % (pt[0],pt[1], min_val))
                continue

        except IndexError:
            for m in msgs:
                print m
            return [], {}
            # return []

        pt = next_pt
        path.append(pt)
        if Distance(start_pt,pt) <= 30:
            path.append(start_pt)
            break
        
        DebugMsg( "    next pt: %s, val %f" % (next_pt, min_val))
    
    # print "Reverse path finished."    
    path.reverse()
    return path, AStarG


