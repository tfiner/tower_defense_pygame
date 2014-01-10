import itertools

class GridException(Exception):
    def __init__(self,what):
        super(GridException,self).__init__(what)


class GridFinder(object):
    '''Divided up into a virtual grid, each move by a creep updates this.'''
    def __init__(self, grid_size, exclusive=False):
        self.grid_size = grid_size
        self.items = {}
        self.exclusive = exclusive

    def GetKey(self, pos):
        x = pos[0] + self.grid_size/2
        y = pos[1] + self.grid_size/2
        return (int(x/self.grid_size), int(y/self.grid_size))

    def Move(self, creep, from_pos, to_pos):
        fkey = self.GetKey(from_pos)
        tkey = self.GetKey(to_pos)
        if fkey == tkey:
            return
        
        self.Remove(creep, from_pos)        
        self.Add(creep, to_pos)
          
    def Add(self, creep, pos=None):
        # print "adding %s at %s to grid[%s]" % (creep, pos, key)
        if pos is None:
            pos = creep.pos
                
        key = self.GetKey(pos)
        if self.exclusive:
            if key in self.items:
                raise GridException("")
            else:
                self.items[key]= creep
        else:
            self.items.setdefault(key,[]).append(creep)
                   
    def Remove(self, creep, pos=None):
        if pos is None:
            pos = creep.pos
        
        # print "removing %s from grid[%s]" % (pos, key) 
        key = self.GetKey(pos)
        if self.exclusive:
            del self.items[key]
        else:
            for c in self.items[key]:
                if c == creep:
                    self.items[key].remove(c)
                    break

    def GetItemsByKeys(self, keys):
        '''Return all items that match keys.'''

        #print "looking in keys: ", keys

        items = []
        if self.exclusive:
            items = [ self.items[key] for key in keys if key in self.items ]
        else:
            chained = []
            for k in keys:
                if k in self.items:
                    chained = itertools.chain( chained, self.items[k] )
                
            items = [ c for c in chained ] 

        return items

    def GetItemsByPos(self, pos):
        key = self.GetKey(pos)

        items = None
        if self.exclusive:
            pass
        else:
            items = []

        if key in self.items:
            items = self.items[key]
        
        return items
              
    def GetItemsByPosNeighbors(self, pos):
        # @@ RANGE
               
        # 8 neighbors for rectangular grids.
        # xl,yu     x,yu    xr,yu
        # xl, y     x, y    xr, y
        # xl,yd     x,yd    xr,yd
        cells = [
            (-1,  1), (0,  1),  (1,  1),
            (-1,  0), (0,  0),  (1,  0),
            (-1, -1), (0, -1),  (1, -1),
        ]

        key = self.GetKey( pos )
        cells = [ (c[0] + key[0], c[1] + key[1]) for c in cells ]
        items = self.GetItemsByKeys(cells)
        # if len(items):
        #    print "%s: %s" % (c, items)
               
        return items        

