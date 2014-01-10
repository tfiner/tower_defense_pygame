import data

class NaviGraph(object):
    def __init__(self, extents, tile_size):
        self.extents = extents
        self.tile_size = tile_size

    def GetCost(self, from_pt, to_pt):
        cost = 1.0 # Horizontal or vertical movement cost.
        
        # Make diagonal cost more.                
        if from_pt[0] != to_pt[0] and \
            from_pt[1] != to_pt[1]:
            cost = 1.41421356237

        # Movement + terrain cost.
        return cost + data.gridCost.GetCost( to_pt )
    
    def AppendNeighbors(self, x, y, neighbors, towers, offsets):
        for xo,yo in offsets:
            xt = x + (xo * self.tile_size[0])
            yt = y + (yo * self.tile_size[1])

            # The start point might be outside of the playing field
            # and needs this conditional to be considered for pathing.
            if (xt,yt) == data.start_pt:
                neighbors.append( (xt,yt) )
            
            # 1. Range check
            if xt < self.extents[0][0] or xt >= self.extents[1][0] or \
               yt < self.extents[0][1] or yt >= self.extents[1][1]:
                continue

            # Passability check.
            if data.gridPass.GetValue( (xt,yt) ):
                neighbors.append( (xt,yt) )
            else:
                # print "---- skipped ", (xt,yt)
                towers.append( True )

                   
    def GetNeighbors(self, pt):        
        x = pt[0]
        y = pt[1]               
        
        # 8 neighbors for rectangular grids.
        # xl,yu     x,yu    xr,yu
        # xl, y     x, y    xr, y
        # xl,yd     x,yd    xr,yd
        #offsets = [
        #    (-1,  1), (0,  1),  (1,  1),
        #    (-1,  0),           (1,  0),
        #    (-1, -1), (0, -1),  (1, -1),
        #]
        
        # First pass, add neighbors in the 4 cardinal directions.
        offsets = [
                      (0,  1),
            (-1,  0),           (1,  0),
                      (0, -1),
        ]
        
        # @@ SCREEN size refactor
        neighbors = []        
        towers = []       
        self.AppendNeighbors(x, y, neighbors, towers, offsets)
        
        # Second pass, after determining tower presence, add diagonals.                
        # if 0 or 1 are False, try (-1, 1)
        # if 0 or 2 are False, try ( 1, 1)
        # if 1 or 3 are False, try (-1,-1)
        # if 2 or 3 are False, try ( 1,-1)
        diag_rules = {
            (0,1):(-1, 1), 
            (0,2):( 1, 1),
            (1,3):(-1,-1),
            (2,3):( 1,-1) 
        }
        diag_offsets = []
        
        # Don't add diagonals when next to an impassable tile.
        if True not in towers:
            for diag,off in diag_rules.items():
                diag_offsets.append(off)                              
                
        self.AppendNeighbors(x, y, neighbors, towers, diag_offsets)
        return neighbors


navi_graph = NaviGraph( ((20,20),(640-80,460)), (20,20) )
