class MultiLevelGrid(object):
    '''This class is designed to make lookups of grids faster by reducing 
    the amount of data considered.  It does this by searching the largest 
    cells first, and descending to smaller cells only when needed.

    A cell has three possible states: (CLEAR, BLOCKED, UNKNOWN)
    When querying, if a cell is unknown, it means that some of its subcells
    are CLEAR and some are BLOCKED.
    '''

    CLEAR=0
    BLOCKED=1
    UNKNOWN=2

    def __init__(self, extents, cell_size):
        self.extents = extents
        self.cell_size = copy(cell_size)
        self.default = None
        self.levels = []
        self.InitLevel(1)               

    def GetLevel(self, level):
        return self.levels[level]

    def InitLevel(self, factor):
        size = self.cell_size[0]*factor,self.cell_size[1]*factor        
        map = {}
        for y in xrange(0, self.extents[1], size[1]):
            for x in xrange(0, self.extents[0], size[0]):
                map[ (x,y) ] = MultiLevelGrid.CLEAR

        # We want the largest grid first in self.levels.
        self.levels.append( (size, map) )
        self.levels.sort()
        self.levels.reverse() 

    def Set(self, pt, value):
        # Set level 0, then propagate up.
        size0,map0 = self.levels[-1]
        cell_pt = GetGridCoord(size0, pt)
        if map0[ cell_pt ] == value:
            return

        map0[ cell_pt ] = value

        # From smallest cell to largest cells.
        for cell_size,cell_map in reversed(self.levels):
            cell_pt = GetGridCoord(cell_size, pt)
            value = cell_map[ cell_pt ]≈o                


    def Get(self, pt):
        '''Starts at the highest level, and dives down until the state is known.'''

        depth = 0

        state = MultiLevelGrid.UNKNOWN
        for cell_size,cell_map in self.levels:
            cell_pt = GetGridCoord(cell_size, pt)
            state = cell_map[cell_pt]
            if state is not MultiLevelGrid.UNKNOWN:
                break
            depth += 1

        assert state is not MultiLevelGrid.UNKNOWN
        return state, depth

    def GetNeighbors(self, pt, level, diagonals=False):
        '''Returns the neighbors of the grid at level.'''
        size, map = self.GetLevel(level)
        cell_pt = GetGridCoord(size, pt)

        neighbors = []
        for gn in GRID_NEIGHBORS:
            npt = cell_pt[0] + (gn[0] * size[0]), cell_pt[1] + (gn[1] * size[1])
            if npt[0] >= 0 and npt[0] < self.extents[0] and \
               npt[1] >= 0 and npt[1] < self.extents[1]:
                neighbors.append(npt)

    def FloodFill(self, pt, value):
        '''Fills at the lowest level, then propagates upwards.'''
