import pygame

class TileCache(object):
    current_tile = 0
    
    tiles = []

    @staticmethod
    def GetTile(num):
        if TileCache.tiles[num][1] is None:
            img = pygame.image.load(TileCache.tiles[num][0])
            img = img.convert_alpha(screen)
            TileCache.tiles[num][1] = img
        return TileCache.tiles[num]

    @staticmethod
    def NextTile():
        TileCache.current_tile += 1
        if TileCache.current_tile == len(TileCache.tiles):
            TileCache.current_tile = 0            


    @staticmethod
    def PrevTile():
        TileCache.current_tile -= 1
        if TileCache.current_tile < 0:
            TileCache.current_tile = len(TileCache.tiles) - 1            


    @staticmethod
    def GetCurrentTile():
        return TileCache.GetTile(TileCache.current_tile)

    @staticmethod
    def SetTileFile(filename, size):
        print "finding tiles in %s" % filename        
        img = pygame.image.load(filename)
        color_key = img.get_at((0, 0))
        # print "\tcolor key: ", color_key

        for y in xrange(1,img.get_height(), size):
            for x in xrange(0,img.get_width(), size):
                if color_key != img.get_at((x, y)):
                    r = pygame.Rect(x,y, size, size)
                    # print "r: ", r
                    s = img.subsurface(r)
                    TileCache.tiles.append( (filename, s, 0) )
