#!/usr/bin/env python 
# $Id
#
# Tim Finer for CPSC-481, Spring 2007
# The main program that drives the simulation.
#

# Import system libraries.
import sys, time, pygame
from pygame.locals import *

# Import the boid class and support functions.
from boid import *


# Some constants
GREY = (128,128,128)
SPRITE_OFFSET = 32
    
# The Grid class is used purely for optimization purposes.
# It spatially sorts the boids into "cells" and caches cell calculations.
class Grid(object):
    def __init__( self, width, height, cell_size ):
        '''Initialize the grid.'''
        self.width = width
        self.height = height
        self.cell_size = cell_size		
        
    def Process( self, boids, screen ):
        '''Optionally draw grid, sort, calculate average heading, position, give
        each boid the averages along with their neighbors.'''

        ycells = self.height/self.cell_size
        xcells = self.width/self.cell_size
        
        # Draw the grid.
        if state["grid"]:
            for dy in range(0,self.height,self.cell_size):
                pygame.draw.line( screen, GREY, \
                    (0, dy), (self.width, dy) )
            for dx in range(0,self.width,self.cell_size):
                pygame.draw.line( screen, GREY, \
                    (dx, 0), (dx, self.height) )                            
                                            
        # Use space sorting to efficiently retrieve boids.        
        # Put all of the boids into a 2D grid of cells.
        # Create the 2D array of cell lists
        grid_boids = []
        for row in range(ycells):            
            grid_boids.append([])                                   
            for col in range(xcells):
                grid_boids[row].append([])

        assert( len(grid_boids) == ycells )
        assert( len(grid_boids[0]) == xcells )
        
        # Determine which cell a boid belongs to and add it.
        for b in boids:
            row = int(b.position.y / self.cell_size)
            row = max( 0, min(row,ycells-1))
            
            col = int(b.position.x / self.cell_size)
            col = max( 0, min(col,xcells-1))
            
            xmin = col*self.cell_size
            xmax = xmin+self.cell_size
            # print "col:%d b.x:%d lims:%d-%d" % (col, b.position.x,xmin,xmax )
            # assert( b.position.x >= xmin and b.position.x <= xmax )

            ymin = row*self.cell_size
            ymax = ymin+self.cell_size
            # print "row:%d b.y:%d lims:%d-%d" % (row, b.position.y,ymin,ymax )
            # assert( b.position.y >= ymin and b.position.y <= ymax )
            
            # print "adding to [%d][%d]" % (row,col)
            # print "cell size %d" % (len(grid_boids[row][col]))
            grid_boids[row][col].append( b )
                
        # For each cell, create a "supercell": the cell itself plus 
        # its 8 surrounding neighbors.
        # +-+-+-+
        # | | | |
        # +-+-+-+
        # | |X| |
        # +-+-+-+
        # | | | |
        # +-+-+-+
        for row in range(1,ycells):
            for col in range(1,xcells):
                supercell = []
                avg_pos = None
                avg_head = None
                                                
                for sr in range(row-1, row+1):
                    for sc in range(col-1, col+1):
                        # Can't wrap around without adding some more smarts to the boids.
                        # They'd have to "know" about the shorcut to the other side
                        # of the screen.
                        # Instead, just skip outer cells.
                        # r = sr % ycells # wrap around
                        # c = sc % xcells # wrap around                    
                        for b in grid_boids[sr][sc]:
                            # print "  cell: %d,%d" % (sc,sr)
                            supercell.append( b )
                            
                # print "supercell(%d,%d) = %d" % (col,row, len(supercell))                            

                # Use the supercell to find average position and average heading.
                if len(supercell) > 1:
                    avg_pos = AvgPos(supercell)
                    avg_head = AvgHead(supercell)
                    if state["debug_avg"]:
                        DrawAvg( avg_pos, avg_head, screen )
                        for b in supercell:
                            pygame.draw.line( screen, BLUE, \
                                (b.position.x, b.position.y), \
                                (avg_pos.x, avg_pos.y) )                            

                # Apply those averages to boids in the cell (not the supercell).
                for cb in grid_boids[row][col]:
                    cb.Think( supercell, avg_pos, avg_head )                                                            
                    
# Given a list of boids, return their average heading                    
def AvgHead( boids ):
    assert( len(boids) )
    heading = Vector2(0,0)
    first = True
    
    for b in boids:    
        if first:
            first = False
            heading.x = b.heading.x
            heading.y = b.heading.y
        else:
            heading.x += b.heading.x
            heading.y += b.heading.y
    
    heading /= len(boids)
    heading.normalize()
    return heading

# Given a list of boids, return their average position.
def AvgPos( boids ):    
    assert( len(boids) )
    position = None
    first = True
    for b in boids:    
        if first:
            first = False
            position = copy.copy(b.position)
        else:
            position.x += b.position.x
            position.y += b.position.y
    
    position /= len(boids)
    return position
    
# Draw a cross hair for the average position in black, and
# the average heading in red.
def DrawAvg( avg_pos, avg_head, screen ):
    pygame.draw.line( screen, BLACK, \
        (avg_pos.x-10, avg_pos.y), \
        (avg_pos.x+10, avg_pos.y) )
        
    pygame.draw.line( screen, BLACK, \
        (avg_pos.x, avg_pos.y-10), \
        (avg_pos.x, avg_pos.y+10) )
        
    pygame.draw.line( screen, red, \
        (avg_pos.x, avg_pos.y), \
        (avg_pos.x+avg_head.x*20, avg_pos.y+avg_head.y*20) )
    

if __name__ == '__main__':
    # A bunch of initialization...
    pygame.init()
        
    font = pygame.font.Font( pygame.font.match_font('bitstreamverasansmono'), 32 )

    size = width,height = 1024, 768
    speed = [20, 20]
    white = 255, 255, 255
    red    = 255, 0, 0

    screen = pygame.display.set_mode(size)

    # Generate some boids with random position and heading.
    boids = [ Boid.Random(width, height) for i in range(0,20) ]
    
    # Partition the screen into squares.
    grid = Grid( width, height, 128 )

    # sprites is a 2D array of [sprite type][rotations]    
    sprites = []
    for img in [ "ferrari-0.gif", "azz.gif", "audi-a3.png", "355.gif"]:
        sprites.append( [] )
        sprites[-1].append( pygame.image.load(img) )    
        for i in range(1, 16):
            sprites[-1].append( pygame.transform.rotate(sprites[-1][0], -i*22.5) )           
        
    boid_sprite_idx = []

    # The main simulation loop.
    while 1:
        # The keyboard handler, some of the keys tweak the state of the simulation.
        for event in pygame.event.get():
            key_mods = pygame.key.get_mods()
            # print "%x" % pygame.key.get_mods()
            if event.type == pygame.QUIT: sys.exit()
            if (event.type == KEYUP):
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                    
                elif event.key == pygame.K_g:
                    state["grid"] = not state["grid"]
                    
                elif event.key in [ pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_PERIOD ]:
                    key_mods = pygame.key.get_mods()
                    if (KMOD_RSHIFT & key_mods) or (KMOD_LSHIFT & key_mods):
                        state["rnd_velocity"] += .1
                        state["rnd_velocity"] = min(state["rnd_velocity"], MAX_RND_VELOCITY)                        
                    else:
                        state["velocity"] *= 2.0
                        state["velocity"] = min(state["velocity"], MAX_VELOCITY)

                elif event.key in [ pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_COMMA ]:
                    if (KMOD_RSHIFT & key_mods) or (KMOD_LSHIFT & key_mods):
                        state["rnd_velocity"] -= .1
                        state["rnd_velocity"] = max(state["rnd_velocity"], MIN_RND_VELOCITY)                        
                    else:                    
                        state["velocity"] /= 2.0
                        state["velocity"] = max(state["velocity"], MIN_VELOCITY)
                    
                elif event.key == pygame.K_1:
                    state["align"] = not state["align"]
                    
                elif event.key == pygame.K_2:
                    state["cluster"] = not state["cluster"]

                elif event.key == pygame.K_3:
                    state["avoid"] = not state["avoid"]
                elif event.key == pygame.K_UP:
                    state["boids"] += 10
                elif event.key == pygame.K_DOWN:
                    state["boids"] -= 10
                elif event.key == pygame.K_f:
                    state["fullscreen"] = not state["fullscreen"]
                    if state["fullscreen"]:
                        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(size)                        
                elif event.key == pygame.K_w:
                    state["wrap"] = not state["wrap"]
                elif event.key == pygame.K_d:
                    state["debug_think"] = not state["debug_think"]                    
                    state["debug_avg"] = not state["debug_avg"]
                    
                elif event.key == pygame.K_RIGHT:
                    state["flee_range"] += 8
                    
                elif event.key == pygame.K_LEFT:
                    state["flee_range"] -= 8
                    state["flee_range"] = max(state["flee_range"],BOID_SIZE/2)
                    
                elif event.key == pygame.K_i:
                    state["info"] = not state["info"]
                    
        # If there are supposed to be more boids, add them.
        # If there are supposed to be less, then delete some.
        try:
            delta_boids = state["boids"] - len(boids) 
            if delta_boids > 0:
                [ boids.append( Boid.Random(width, height) ) for i in range(0,delta_boids) ]
            elif delta_boids < 0:
                boids[0:-delta_boids] = []
        except:
            pass
            
        if state["boids"] != len(boids):
            state["boids"] = len(boids)
            
        # For each boid, give it a random sprite type.
        # Sync the boid_sprite_index to the existing boids, using the 
        # same method to grow / shrink as the boid array above. 
        delta_boids = len(boids) - len(boid_sprite_idx)
        if delta_boids > 0:
            [ boid_sprite_idx.append( randint(0,len(sprites)-1) ) for i in range(0,delta_boids) ]
        elif delta_boids < 0:
            boid_sprite_idx[0:-delta_boids] = []
                
        # screen.fill( SKY_BLUE )
        screen.fill( BLACK )
        # screen.fill( WHITE )

        # Do all of the spatial sorting, math and boid thinking.
        grid.Process( boids, screen )        

        # Draw the important information in the upper left hand corner of the screen.
        if state["info"]:
            text_line = 0
            #~ for flag in ["align", "cluster", "avoid", "velocity", "boids", "flee_range", "rnd_velocity"]:
            for flag in ["align", "cluster", "avoid", "velocity", "boids", "flee_range"]:
                txt     = font.render( "%12s = %s" % (flag, state[flag]), True, GREEN )
                shadow  = font.render( "%12s = %s" % (flag, state[flag]), True, BLACK )
                screen.blit(shadow, (10+2,text_line+2))
                screen.blit(txt, (10,text_line))
                text_line += txt.get_size()[1]

        # Move the boids around, draw using their sprites.
        spr_idx = 0
        for b in boids:
            b.Move( size )
            rot_idx = int( (FowlerAngle(b.heading.y,b.heading.x)*2.0) +0.5 )
            # print ">ridx %d" % rot_idx
            rot_idx %= len(sprites[boid_sprite_idx[spr_idx]])
            # print "<ridx %d" % rot_idx
            # print "boid: %d  sidx: %d  ridx  %d" % (spr_idx, boid_sprite_idx[spr_idx], rot_idx)
            sprite = sprites[boid_sprite_idx[spr_idx]][rot_idx]
            screen.blit( sprite, (b.position.x-SPRITE_OFFSET, b.position.y-SPRITE_OFFSET))
            b.Draw( screen )
            spr_idx += 1
            
        pygame.display.flip()
#        time.sleep( .125 )
        