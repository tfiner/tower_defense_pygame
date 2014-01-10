# Contains "global" data.  This module was created to prevent
# module circular dependencies.

import image_cache
import grid_finder
import path_cache
import grid_cost
import grid_pass

print "data"

the_base = None
screen_size = 640,480
cell_size = None
extents = None

start_pt = (540,40)
end_pt = (80,340)

sprites = []
creeps = []
non_interact_sprites = []
towers = []

pathCache = None

gridCost = None
gridPass = None

towerFinder = None
creepFinder = None

selected = None

def IsCoordInRange(pt):
    return pt[0] > extents[0][0] and \
           pt[0] < extents[1][0] and \
           pt[1] > extents[0][1] and \
           pt[1] < extents[1][1]

def GetGridCoordRound(pt):
    pt_round = pt[0] + cell_size[0]/2, pt[1] + cell_size[1]/2
    return GetGridCoord( pt_round )

def GetGridCoord(pt):
    X,Y = cell_size[0], cell_size[1]
    return int(pt[0]/X) * X, int(pt[1]/Y) * Y


def SetExtents(new_extents, new_cell_size):
    print "setting extents", new_extents

    global extents, cell_size, pathCache, towerFinder, gridCost, gridPass
    global creepFinder, pathCache

    cell_size = new_cell_size
    extents = new_extents
    
    pathCache = path_cache.PathCache(cell_size)

    gridCost = grid_cost.GridCost( extents, cell_size )
    gridPass = grid_pass.GridPass( extents, cell_size )

    towerFinder = grid_finder.GridFinder( cell_size[0], exclusive=True )
    creepFinder = grid_finder.GridFinder( cell_size[0] * 4 )


def Init():
    print "data.Init()"
    SetExtents( ((20,20),(640-80,460)), (20,20))
    image_cache.ImageCache.SetImageFile( "base.png", (60,60) )
    image_cache.ImageCache.SetImageFile( "tank1.png", (20,20) )
    image_cache.ImageCache.SetImageFile( "turretsv2.png", (40,40) )
    image_cache.ImageCache.SetImageFile( "bullet1.png", (10,10) )
    image_cache.ImageCache.SetImageFile( "explosion_small.png", (20,20) )
    image_cache.ImageCache.SetImageFile( "explosion_large.png", (20,20) )

