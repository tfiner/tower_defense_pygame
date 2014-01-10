from pygame.locals import *
import pygame
from grid_finder import GridFinder
import level

import grid_cost
import grid_pass


class Layer(object):
    def __init__(self):
        self.draw_mouse = False
    
    def Draw(self, surf):
        pass

    def SetDrawMouse(self, flag):
        self.draw_mouse = flag 

class RectLayer(Layer):
    def __init__(self, extents, tile_size):
        super(RectLayer,self).__init__()
        self.extents = extents
        self.tile_size = tile_size
        self.tiles = {}
        self.mouse_pos = (0,0)

    def Draw(self, surf):
        for k,v in self.tiles.items():
            x = k[0] * self.tile_size[0] 
            y = k[1] * self.tile_size[1] 
            v.Draw(surf, (x,y))

        if self.draw_mouse:
            x0 = (self.mouse_pos[0] / self.tile_size[0]) * self.tile_size[0] 
            y0 = (self.mouse_pos[1] / self.tile_size[1]) * self.tile_size[1]
            r = pygame.Rect(x0, y0, self.tile_size[0], self.tile_size[1])

            if False:
                tile = TileCache.GetCurrentTile()
                surf.blit(tile[1], (x0,y0), None, 0)
            
            pygame.draw.rect(surf, (255,0,0), r, 2)

    def Mouse(self, pos):
        self.mouse_pos = pos
        
    def SetChild(self, pt):        
        tile = RectTile(TileCache.current_tile)        
        x = int(pt[0] / self.tile_size[0])
        y = int(pt[1] / self.tile_size[1])
        self.tiles[(x,y)] = tile
        assert (x,y) in self.tiles

    def Fill(self, surf):
        tile = RectTile(TileCache.current_tile)
        tiles_x = surf.get_width() / self.tile_size[0]
        tiles_y = surf.get_height() / self.tile_size[1]
        for y in xrange(0, tiles_y):
            for x in xrange(0, tiles_x):
                if not (x,y) in self.tiles:
                    self.tiles[(x,y)] = tile
                    
    def Clear(self, surf):        
        self.tiles = {}

    def GetCost(self, from_pt, to_pt):
        cost = 1.0 # Horizontal or vertical movement cost.
        
        # Make diagonal cost more.                
        if from_pt[0] != to_pt[0] and \
            from_pt[1] != to_pt[1]:
            cost = 1.41421356237

        # Movement + terrain cost.
        return cost + grid_cost.grid_cost.GetCost( to_pt )

    def IsTowerPresent(self, pos):
        global towerFinder
        tower = towerFinder.GetItemsByPos( pos )
        return tower is not None
    
    def AppendNeighbors(self, x, y, neighbors, towers, offsets):
        for xo,yo in offsets:
            xt = x + (xo * self.tile_size[0])
            yt = y + (yo * self.tile_size[1])

            # The start point might be outside of the playing field
            # and needs this conditional to be considered for pathing.
            if (xt,yt) == game.theGame.GetCurLevel().start_pt:
                neighbors.append( (xt,yt) )
            
            # 1. Range check
            if xt < 0 or xt >= self.extents[0] or \
               yt < 0 or yt >= self.extents[1]:
                continue

            # Passability check.
            if grid_pass.grid_pass.GetValue( (xt,yt) ):
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

     

