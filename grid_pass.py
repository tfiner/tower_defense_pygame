import pygame


class GridPass(object):
    '''Keeps track of whether or not a grid cell is 'passable'.'''

    def __init__(self, extents, cell_size):
        self.extents = extents
        self.cell_size = cell_size        
        self.Clear( True )
        self.constants = {}

    def Clear(self, value):
        '''Clears all non constants.'''
        self.cells = {}
        for y in xrange(self.extents[0][1], self.extents[1][1], self.cell_size[1]):
            for x in xrange(self.extents[0][0], self.extents[1][0], self.cell_size[0]):
                self.cells[(x,y)] = value

    def GetNeighbors(self,pt):
        offsets = [
                      (0,  1),  
            (-1,  0),          (1,  0),
                      (0, -1)
        ]

        cells = []
        for off in offsets:
            x = pt[0] + off[0] * self.cell_size[0]
            y = pt[1] + off[1] * self.cell_size[1]

            within_grid = \
                x >= self.extents[0][0] and \
                x < self.extents[1][0] and \
                y >= self.extents[0][1] and \
                y < self.extents[1][1]

            if not within_grid:
                continue

            if (x,y) in self.constants and not self.constants[(x,y)]:
                continue

            cells.append( (x,y) )

        return cells
        
    def FloodFill(self, seed):
        '''Flood fills a point from seed.'''

        self.Clear( False )
        
        # GetNeighbors already filters on value.
        queue = [seed]
        visited = set()
        while len(queue):
            pt = queue.pop()
            self.cells[pt] = True
            visited.add(pt)
            neighbors = self.GetNeighbors(pt)
            for n in neighbors:
                if n not in visited:
                    queue.append( n )

    def AddConstant(self, pt, value):
        '''Set a value that is not subject to flood filling.'''
        self.constants[pt] = value

    def DelConstant(self, pt):
        '''Set a value that is not subject to flood filling.'''
        del self.constants[pt]

    def GetValue(self, pt):
        try:
            if pt in self.constants:
                return self.constants[pt]
            return self.cells[ pt ]
        except KeyError:
            return False

    def Draw(self, surf):
        # Draw passables in green
        for y in xrange(self.extents[0][1], self.extents[1][1], self.cell_size[1]):
            for x in xrange(self.extents[0][0], self.extents[1][0], self.cell_size[0]):
                if self.cells[(x,y)]:
                    r = pygame.Rect( (x,y), self.cell_size)
                    surf.fill((0,255,0), r)
        
