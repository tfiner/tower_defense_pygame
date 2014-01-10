def IsSameSide( pt_test, pt_ref, line_ref ):
    vec_ref0 = Vector3(line_ref[1][0] - line_ref[0][0], line_ref[1][1] - line_ref[0][1], 0)
    vec_ref1 = Vector3(pt_ref[0] - line_ref[0][0], pt_ref[1] - line_ref[0][1], 0)
    vec_test = Vector3(pt_test[0] - line_ref[0][0], pt_test[1] - line_ref[0][1], 0)
    
    cp_ref = vec_ref0.cross(vec_ref1).normalized()
    cp_test = vec_ref0.cross(vec_test).normalized()
    dot = cp_ref.dot(cp_test) 
  
    if False:  
        print "pt_test: %s, pt_ref: %s, line_ref: %s" % (pt_test, pt_ref, line_ref)
        print "%s X %s = %s" % (vec_ref0, vec_ref1, cp_ref)
        print "%s X %s = %s" % (vec_ref1, vec_test, cp_test)
        print "dot = %f" % dot
    
    return dot >= 0.0

def IsPtInsidePoly(points, pt):
    inside = True
    for i in range(2, len(points)):
        if not IsSameSide( pt, points[i-2], (points[i-1],points[i]) ):
            inside = False
            break
            
    return inside

    

class HexTile(Drawable):
    def __init__(self, hex_grid, pt, pass_cost):
        self.hex_grid = hex_grid
        self.origin = self.hex_grid.GetHexOrigin(pt)        
        self.pass_cost = pass_cost        


class SolidHexColor(HexTile):
    def __init__(self, hex_grid, pt, color):
        self.color = color
        self.points = hex_grid.GetHexFromScreen(pt)        
        super(SolidHexColor,self).__init__(hex_grid, pt, 1000)
        
    def Draw(self, surf):
        pygame.draw.polygon(surf, self.color, self.points)        

class BitmapHex(HexTile):
    def __init__(self, hex_grid, pt, tile_num):
        self.tile_num = tile_num        
        tile = TileCache.GetTile(self.tile_num)        
        super(BitmapHex,self).__init__(hex_grid, pt, tile[2])                   
        
    def Draw(self, surf):
        tile = TileCache.GetTile(self.tile_num)
        surf.blit(tile[1], self.origin, None, 0)
                        
    

class NullHex(HexTile):
    pass_cost = 1000
    
    @staticmethod
    def __str__():
        return "NullHex: cost=%d" % NullHex.pass_cost
    
       
        # Look for enemies
        # Pick one (if visible)
        # Fire (if able)
        pass   


class HexGrid(Layer, Graph):
    def __init__(self, size, color):
        self.size = size
        self.surf_size = None
        self.color = color
        self.mouse_pos = None
        self.mouse_x = -1
        self.mouse_y = -1
        self.children = {}
        super(HexGrid,self).__init__()
        
    def Mouse(self, pos):
        try:        
            self.mouse_pos = pos
                
            self.mouse_x = (4 * pos[0]) / (3 * self.W)
            self.mouse_y = pos[1] / self.H
        except AttributeError:
            pass
        
    def Draw(self, surf):
        surf_size = surf.get_size()
        if surf_size != self.surf_size:
            self.surf_size = surf_size
            self.CalcOffsets()                
      
        for y in range(0, self.numy):
            pos = [0,y * self.H]
            down1 = False
            for x in xrange(0, self.numx):
                if (x,y) in self.children:
                    self.children[(x,y)].Draw(surf)

                if False:
                    if down1:
                        pos[1] += self.H2
                    else:
                        pos[1] -= self.H2
        
                    points = [ (pt[0]+pos[0], pt[1]+pos[1]) for pt in self.points ]
                    
                    width = 1
                    color = self.color
    
                    pygame.draw.lines(surf, color, True, points, width)
                    pygame.draw.circle(surf, (255,0,0), self.mouse_pos, 8, 4)                    
    
                    pos[0] += 3 * self.X                    
                    down1 = not down1
                
        if self.draw_mouse and self.mouse_pos is not None:
            mouse_hex = self.GetHexFromScreen(self.mouse_pos)
            width = 5
            color = 255,0,0
            pygame.draw.lines(surf, color, True, mouse_hex, width)
        

    def GetHexFromScreen(self, pt):
        origin = self.GetHexOrigin( pt )       
        points = [ (pt[0]+origin[0], pt[1]+origin[1]) for pt in self.points ]
        return points

    def GetHexCellCoord(self, pt):
        x,y = pt
        xhex   = (4*x)/(3*self.W)
        down1 = (xhex % 2) == 1
               
        if not down1:
            y -= self.H2

        yhex   = y/self.H
        return xhex,yhex

    def HexToScreen(self, hex_coord):
        x = (hex_coord[0] * self.W * 3) / 4
        y =  hex_coord[1] * self.H        
        
        down1 = (hex_coord[0] % 2) == 1
               
        if not down1:
            y += self.H2

        return x,y
            
    def GetHexOrigin(self, pt):
        x,y = pt
        xhex   = (4*x)/(3*self.W)
        down1 = (xhex % 2) == 1
               
        if not down1:
            y -= self.H2

        yhex   = y/self.H
        origin = [(xhex*3*self.W)/4, yhex*self.H]
        
        if not down1:
            origin[1] += self.H2        
        
        return origin 

    def SetHexCoordChild(self, hex_coord, child):
        self.children[hex_coord] = child
        assert (x,y) in self.children                

    def SetChild(self, pt):        
        child = BitmapHex(self, pt, TileCache.current_tile)                
        x,y = self.GetHexCellCoord(pt)
        self.children[(x,y)] = child
        assert (x,y) in self.children                

        if DEBUG:
            print "HexTile set %d,%d" % (x,y)                
            neighbors = self.GetNeighbors((x,y))
            directions = ['N', 'NE', 'SE', 'S', 'SW', 'NW' ]
            for n in range(len(neighbors)):
                msg = "%2s: " % directions[n]
                if neighbors[n] is None:
                    msg += "None"
                else:
                    msg += "%d %d" % neighbors[n] 
                print msg

    def GetChild(self, hex_coord):
        if hex_coord not in self.children:
            return NullHex
        return self.children[hex_coord]


    def CalcOffsets(self):                
        self.W = self.size[0]
        self.H = self.size[1]
        
        self.numx = (4 * self.surf_size[0]) / (3 * self.W)
        self.numy = self.surf_size[1] / self.H + 1
        
        W2 = self.W / 2
        self.H2 = self.H / 2
        self.X = self.size[0] / 4        
        
        self.points = []
        self.points.append( (0,         self.H2) ) 
        self.points.append( (self.X,    self.H) ) 
        self.points.append( (3*self.X,  self.H) ) 
        self.points.append( (self.W,    self.H2) ) 
        self.points.append( (3*self.X,  0) ) 
        self.points.append( (self.X,    0) )  



    def GetNeighbors(self, hex_coord):
        # Neighbors are returned in a list of 6 members, starting with North and winding clockwise to end at NW.
        # Neighbors that don't exist are None.
        neighbors = [ None for i in range(6) ]
        #                N      NE      SE      S      SW      NW
        odd_offs  = [  (0,-1), (1,-1), (1,0),  (0,1), (-1,0), (-1,-1) ]
        even_offs = [  (0,-1), (1, 0), (1,1),  (0,1), (-1,1), (-1, 0) ]
        
        offs = even_offs
        if (hex_coord[0] % 2) == 1:
            offs = odd_offs
        
        for i in range(len(offs)):
            neighbor = hex_coord[0] + offs[i][0], hex_coord[1] + offs[i][1]
            if neighbor in self.children:
                neighbors[i] = neighbor
                
        return neighbors

