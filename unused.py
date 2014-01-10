
class GridCost2(object):
    def __init__(self, extents, cell_size):
        self.extents = extents
        self.cell_size = cell_size
        self.costs = {}
        self.colors = [ (c,255,c) for c in xrange(0,256) ]
        self.min_val = self.max_val = None
        
    def Calculate(self, start, end):
        for y in xrange(0, self.extents[1], self.cell_size[1]):
            for x in xrange(0, self.extents[0], self.cell_size[0]):
                if IsTowerPresent( (x,y) ):
                    self.costs[ (x,y) ] = None
                else:
                    cost = Distance(start, (x,y)) + Distance((x,y),end)
                    self.costs[ (x,y) ] = cost
                    if self.min_val is None:
                        self.min_val = cost
                        self.max_val = cost
                    else:
                        self.min_val = min(self.min_val,cost)
                        self.max_val = max(self.max_val,cost)

    def GetKey(self, pt):
        grid_pt = int(pt[0]/self.cell_size[0]) * self.cell_size[0], \
            int(pt[1]/self.cell_size[1]) * self.cell_size[1]
        return grid_pt
        
    def GetCost(self, pt):
        grid_pt = self.Getkey(pt)
        return self.costs[ grid_pt ]
                
    def Draw(self, surf):
        if self.min_val is not None:
            delta = self.max_val - self.min_val
            for pt,cost in self.costs.iteritems():
                if cost is not None:
                    idx = int(((cost - self.min_val) * 255) / delta);
                    r = pygame.Rect( pt, (20, 20) )
                    surf.fill(self.colors[idx], r)
        
