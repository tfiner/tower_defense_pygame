#!/Usr/bin/env python
#

import sys, math
from euclid import Vector2, Vector3
import pickle
from pygame.locals import *
import pygame
import itertools
import copy

import sprite 
import ui
import ui_td
import game
import data

DEBUG = False

def AddTower(grid_pos):
    pos = copy.copy(grid_pos)
    if pos in [data.start_pt, data.end_pt]:
        print "***** skipping 0, tower can't be placed on start/end..."
        return

    if data.towerFinder.GetItemsByPos(pos) is not None:
        print "***** skipping 1, tower is present..."
        return

    if not data.IsCoordInRange(pos):
        print "***** skipping, outside of playing field..."
        return

    new_tower_rect = pygame.Rect(pos, data.cell_size)
    ctest = data.creepFinder.GetItemsByPos(pos)
    for c in ctest:
        if c.DidCollide(new_tower_rect):
            print "***** skipping 2, sprite is present..."    
            return

    # Grid passage test, all sprites must be able to reach the end point.
    gp = data.gridPass
    gp.AddConstant( pos, False )
    gp.FloodFill( data.end_pt )
    if not gp.GetValue(data.start_pt):
        gp.DelConstant( pos )
        gp.FloodFill( data.end_pt )
        print "***** skipping 3, start is cut off..."    
        return

    for c in data.creeps:
        if not c.is_dead:
            c_pos = data.GetGridCoordRound(c.pos)
            if not gp.GetValue(c_pos):
                gp.DelConstant( pos )
                gp.FloodFill( data.end_pt )
                print "***** skipping 4, creep is cut off..."    
                return

    new_tower = sprite.Turret1(pos)
#    print new_tower
    data.selected = new_tower
    data.towers.append(new_tower)

    gc = data.gridCost
    gc.ResetPaths()
    gc.AddCostCircle( pos, new_tower.range, new_tower.GetDamagePerSec() * 100)

    pt = data.pathCache
    pt.ClearCache()
    pt.ResetPath(data.start_pt, data.end_pt)

    # Recalc the main astar path
    print "main a*: %s -> %s" % (data.start_pt, data.end_pt)

    # Space out recalculations with a 10 frame delay between each.
    # Reversing should pick the latest sprites, they'll probably be 
    # the farthest and they should generate the longest paths.  
    # This should help caching. 
    new_goal = 0
    for c in reversed(data.creeps):
        new_goal += 10
        c.FindNewGoal(new_goal)

def UpgradeTower(tower):
    if not tower.CanUpgrade():
        return

    gc = data.gridCost
    gc.ResetPaths()
    gc.SubtractCostCircle( tower.pos, tower.range, tower.GetDamagePerSec() * 100)

    tower.Upgrade()
    gc.AddCostCircle( tower.pos, tower.range, tower.GetDamagePerSec() * 100)

    pt = data.pathCache
    pt.ClearCache()
    pt.ResetPath(data.start_pt, data.end_pt)

                               
if __name__ == '__main__':
    pygame.init()
    
    black = 0,0,0

    data.Init()
    
    # screen = pygame.display.set_mode( screen_size, pygame.FULLSCREEN )
    screen = pygame.display.set_mode( data.screen_size  )

    toolbar = ui_td.TDToolbar( screen )
      
    creep_path, path_idx = data.pathCache.GetPath(data.start_pt, data.end_pt)

    last_mouse = None
    paused = False
    
    bad_tower_pos = None
    bad_tower_dead_ends = None

    fullscreen = False

    clock = pygame.time.Clock()
    while True:

        clock.tick_busy_loop(60)
        cur_level = game.theGame.GetCurLevel()
        cur_level.Update()
        toolbar.Update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                sys.exit()
                
            if event.type == pygame.MOUSEMOTION:
                last_mouse = event                
                
            if event.type == pygame.KEYUP:    
                if event.key == pygame.K_c:
                    data.pathCache.ClearCache()
                    data.pathCache.GetPath(cur_level.start_pt, cur_level.end_pt)
                elif event.key == pygame.K_p:
                    paused = not paused
                    
            if paused:
                continue

            mouse_type = event.type in [MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP]
            grid_pos = None
            if mouse_type:
                grid_pos = data.GetGridCoord(event.pos)
                toolbar.Mouse( event )
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                tower = data.towerFinder.GetItemsByPos(grid_pos)
                if tower is not None:
                    data.selected = tower
                else:
                    AddTower( grid_pos )
            
            if event.type == pygame.KEYUP:

                if event.key == pygame.K_q:
                    sys.exit()
                
                elif event.key == pygame.K_SPACE:
                    for i in xrange(1):
                        c = sprite.Creep("tank1.png", range(8), data.start_pt, 1, 0)                        
                        data.creeps.append( c )

                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode( data.screen_size, pygame.FULLSCREEN )
                    else:
                        screen = pygame.display.set_mode( data.screen_size  )

                elif event.key == pygame.K_u:
                    if data.selected is not None:
                        UpgradeTower(data.selected)

                elif event.key == pygame.K_TAB:
                    if data.selected is None:
                        if len(data.towers):
                            data.selected = data.towers[0]
                    else:
                        for tidx in xrange(len(data.towers)):
                            if data.towers[tidx] == data.selected:
                                break
                        tidx = (tidx + 1) % len(data.towers)
                        data.selected = data.towers[tidx]


            elif event.type == ui.Button.EVT_BTN:
                if event.action == ui.Button.QUERY:
#                    print "button %s wants to know what state it should be in." % event.btn.name
                    selected = data.selected is not None
                    if event.btn.name == "upgrade":
                        if selected and data.selected.CanUpgrade():
                            event.btn.state = ui.Button.STATE_READY
                        else:
                            event.btn.state = ui.Button.STATE_GHOST

                    if event.btn.name == "sell":
                        if selected:
                            event.btn.state = ui.Button.STATE_READY
                        else:
                            event.btn.state = ui.Button.STATE_GHOST

                elif event.action == ui.Button.CLICK:
                    if event.btn.name == "upgrade" and \
                            data.selected is not None and \
                            data.selected.CanUpgrade():
                        UpgradeTower(data.selected)
 
#        screen.fill(black)       
        cur_level.Draw( screen )
        toolbar.Draw( screen )

        data.gridCost.Draw(screen)        
#        data.pathCache.Draw(screen)
#        data.gridPass.Draw(screen)

        if bad_tower_pos is not None:
            for p in bad_tower_dead_ends:
                r = pygame.Rect( p, data.cell_size )
                screen.fill((255,0,0), r)
                
            r = pygame.Rect( pos, data.cell_size )
            screen.fill((255,0,255), r)
        
        if not paused:
            for t in data.towers:
                t.Think()
                                    
            # "Think" only sprites
            for items in [data.creeps, data.sprites, data.non_interact_sprites]:
                for s in items:
                    # @@ REFACTOR, have sprite remove itself from list of sprites.
                    if s.is_dead:                
                        # print "%s reaping sprite %s" % (items, s)
                        items.remove(s)

                    s.Think()

            for creep in data.creeps:
                # @@ REFACTOR, have sprite remove itself from list of sprites.
                if creep.is_dead:
                    # print "%s reaping sprite %s" % (items, s)
                    data.creeps.remove(creep)

            # Creeps have a split between thinking and moving so that they can read
            # their neighbors current positions and headings and adjust to them.
            for s in data.creeps:
                s.Move()
                    
        for items in [data.towers, data.creeps, data.sprites, data.non_interact_sprites]:
            for s in items:
                s.Draw(screen)          
            
        pygame.display.flip()
        

