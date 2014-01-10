import copy

from pygame.locals import *
import pygame

from geom_helpers import *

class GridCost(object):
    def __init__(self, extents, cell_size):
        self.extents = extents
        self.cell_size = cell_size
        
        self.costs = {}
        for y in xrange(self.extents[0][1], self.extents[1][1], self.cell_size[1]):
            for x in xrange(self.extents[0][0], self.extents[1][0], self.cell_size[0]):
                self.costs[ (x,y) ] = 0.0
                
        self.cost_min = 0
        self.cost_max = 0
        
        self.colors = []
        # g         yellow  red
        # 0 r  r0   r1
        # 0 g  g 1  g1      g0
        # 0 b 
        for c in xrange(0,256):            
            if c < 64:
                g = (c * 255) / 64
                self.colors.append( (0,g,0) )
            elif c >= 64 and c < 128:
                r = ((c-64) * 255) / 64
                self.colors.append( (r,255,0) )
            else: # c >= 128 < 256
                g = 128 / ((c-127) * 255)
                self.colors.append( (255,g,0) )

        # Keep a copy of these around so they can be undone.
        self.paths = []
            
                
    def GetKey(self, pt):
        x,y = pt
        x = int(x / self.cell_size[0]) * self.cell_size[0]
        y = int(y / self.cell_size[1]) * self.cell_size[1]

        x = max(x,self.extents[0][0])
        x = min(x,self.extents[1][0])
        y = max(y,self.extents[0][1])
        y = min(y,self.extents[1][1])

        return (x,y)
    
    def GetCost(self, pt):        
        return self.costs[ pt ]
    
    def AddCost(self, pt, cost):
        key = self.GetKey(pt)
        self.costs[ key ] += cost
        self.SetMinMax( self.costs[ key ] )
        # print "%s : %f" % (key, self.costs[ key ])
    
    def SubtractCost(self, pt, cost):
        key = self.GetKey(pt)
        self.costs[ key ] -= cost
        self.SetMinMax( self.costs[ key ] )
        
    def SetMinMax(self, cost ):
        self.cost_min = min( self.cost_min, cost )
        self.cost_max = max( self.cost_max, cost )

        
    def Draw(self, surf):
        delta = self.cost_max - self.cost_min
        if 0 == delta:
            return        
        
        for y in xrange(self.extents[0][1], self.extents[1][1], self.cell_size[1]):
            for x in xrange(self.extents[0][0], self.extents[1][0], self.cell_size[0]):
                cost = self.costs[ (x,y) ]
                if 0 == cost:
                    continue
                # print "%s = %f" % (key,cost)                
                idx = int((255 * (cost - self.cost_min)) / delta)
                idx = min(idx,255)
                idx = max(idx,0)
                r = pygame.Rect((x,y), self.cell_size)
                surf.fill(self.colors[idx], r)
        
        
    def ApplyToCircle(self, pt, radius, cost, func):        
        '''Applies the function to the cost dictionary.'''
        # print "Applying circle at %s, radius %d" % (pt, radius)        
        radius *= 1.5

        center = copy.copy(pt)
        center = center[0] + self.cell_size[0]/2, center[1] + self.cell_size[1]/2

        x0,y0 = self.GetKey( (center[0]-radius, center[1]-radius) )
        x1,y1 = self.GetKey( (center[0]+radius+self.cell_size[0], center[1]+radius+self.cell_size[1]) )
        
        for y in xrange(y0,y1,self.cell_size[1]):
            for x in xrange(x0,x1,self.cell_size[0]):
                t = x + self.cell_size[0]/2, y + self.cell_size[1]/2
                d = Distance( t, center )
                if d < radius:
                    func( (x,y), cost )

    def ApplyToPath(self, path, cost, func):        
        '''Applies the function to the cost dictionary.'''

        for p in path:
            func( p, cost )

    def AddCostPath(self, path, cost):
        self.ApplyToPath(path, cost, self.AddCost)
        self.paths.append( (cost, copy.copy(path)) )

    def SubtractCostPath(self, path, cost):
        self.ApplyToPath(path, cost, self.SubtractCost)

    def ResetPaths(self):
        for cost,path in self.paths:
            self.ApplyToPath(path, cost, self.SubtractCost)
        self.paths = []

    def AddCostCircle(self, pt, radius, cost):
        self.ApplyToCircle(pt, radius, cost, self.AddCost)
        
    def SubtractCostCircle(self, pt, radius, cost):
        self.ApplyToCircle(pt, radius, cost, self.SubtractCost)
