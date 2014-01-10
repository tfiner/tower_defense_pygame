#!/Usr/bin/env python
#

import copy

from pygame.locals import *
import pygame

import pygame.mixer, pygame.time


class Toolbar(object):
    def __init__(self, screen, filename, pt ):
        self.pt = pt
        self.img = pygame.image.load(filename)
        self.img = self.img.convert_alpha(screen)
        self.children = []

    def AddChild(self, child):
        self.children.append(child)

    def Update(self):
        for c in self.children:
            c.Update()

    def Draw(self, surf):
        surf.blit( self.img, self.pt, None, 0 )
        for c in self.children:
            c.Draw(surf, self.pt)

    def Mouse(self, evt):
        # For mouse down events, forward only to children
        # that the mouse is over.
        if evt.type == pygame.MOUSEBUTTONDOWN:
            for c in self.children:
                # Only fwd mouse msgs for children that the mouse is within it's rect.
                r = c.GetRelativeRect().move(self.pt[0], self.pt[1])
                if r.collidepoint( evt.pos ):
                    c.Mouse(evt)

        else: # Forward all other mouse events.
            for c in self.children:
                c.Mouse(evt)
                
    def Key(self, evt):
        for c in self.children:
            c.Key(evt)
        
class Button(object):
    STATE_GHOST = 0
    STATE_READY = 1
    STATE_CLICK = 2
    
    EVT_BTN = USEREVENT+1
    # Since pygame appears to have a limited set of "user" event numbers,
    # these are the "action" field in an EVT_BTN dictionary.
    QUERY = 0
    CLICK = 1

    def __init__(self, screen, filename, rel_pt, abs_pt, snd_click):
        self.state = Button.STATE_GHOST

        self.img = pygame.image.load(filename)
        self.img = self.img.convert_alpha(screen)
        self.rel_pt = rel_pt
        self.abs_pt = abs_pt[0] + rel_pt[0], abs_pt[1] + rel_pt[1]

        self.width = self.img.get_width()
        self.height = self.img.get_height() / 3
        self.rect = pygame.Rect( self.rel_pt, (self.width, self.height) )
        self.img_states = []
        self.snd_click = snd_click

        for y in xrange( 0, self.img.get_height(), self.height ):
            r = pygame.Rect( (0,y), (self.width, self.height) )
            self.img_states.append( self.img.subsurface(r) )

        self.tick = 0
        self.next_update = 0
        self.SendEvt(Button.QUERY)

    def HandleEvents(self, evt):
        if evt.type == Button.EVT_BTN:
            print "Got a custom event %s for %s" % (evt, self)
            if evt.action == Button.SET_STATE:
                self.state = evt.state

    def GetRelativeRect(self):
        return self.rect

    def Draw(self, surf, pt):
        pt = self.rel_pt[0] + pt[0], self.rel_pt[1] + pt[1]
        surf.blit( self.img_states[self.state], pt, None, 0 )

    def Update(self):
        self.tick += 1
        send_query = False
        pressed = pygame.mouse.get_pressed()

        if self.next_update and self.tick > self.next_update:
            self.next_update = 0
            send_query = True

        # Don't auto update while in a click.
        elif 0 == (self.tick%50) and True not in pressed:
            send_query = True

        # If the button is being held down, then don't update.
        if send_query:
#            print "sending query"
            self.SendEvt(Button.QUERY)

    def SendEvt(self, action):
        data = { 'action':action, 
                 'btn':self }
        evt = pygame.event.Event( Button.EVT_BTN, data )
#        print "posting ", evt
        pygame.event.post( evt )

    def DeferNextState(self):
        self.next_update = self.tick + 10

    def Mouse(self, evt):
        if self.state == Button.STATE_GHOST:
            return

        if evt.type == pygame.MOUSEBUTTONDOWN:
            self.state = Button.STATE_CLICK
            self.snd_click.play()
            self.SendEvt(Button.CLICK)

        elif evt.type == pygame.MOUSEBUTTONUP:
            self.DeferNextState()

        elif evt.type == pygame.MOUSEMOTION:
            # If the button was being held down, and the user moved
            # the mouse outside of the button rectangle.
            if self.state == Button.STATE_CLICK:
                r = pygame.Rect( self.abs_pt, (self.width, self.height) )
                if not r.collidepoint( evt.pos ):
                    self.DeferNextState()
                
    def Key(self, evt):
        pass



BLACK = 0,0,0

if __name__ == '__main__':
    pygame.init()
    
    game_extents = screen_size = 640,480
    
    fullscreen = False
    screen = pygame.display.set_mode( screen_size  )

    btn_click = pygame.mixer.Sound("sounds/9245__burnttoys__click_clean.wav")

    toolbar = Toolbar( screen, "ui00.png", (640-80,0) )
    btn = Button(screen, "btn_sell.png", (10,65), (640-80,0), btn_click )
    btn.name = "sell"
    toolbar.AddChild( btn )

    btn = Button(screen, "btn_upgrade.png", (10,95), (640-80,0), btn_click )
    btn.name = "upgrade"
    toolbar.AddChild( btn )

    clock = pygame.time.Clock()

    keep_running = True
    while keep_running:
        clock.tick_busy_loop(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                keep_running = False

            if event.type in [MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                toolbar.Mouse( event )
                
            if event.type in [pygame.KEYUP, pygame.KEYDOWN]:
                toolbar.Key( event )
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_q:
                        keep_running = False

                    elif event.key == pygame.K_f:
                        fullscreen = not fullscreen

                    elif event.key == pygame.K_s:
                        data = { 'action':Button.SET_STATE, 'state':Button.STATE_GHOST }   
                        evt = pygame.event.Event( Button.EVT_BTN, data )
                        print "posting ", evt
                        pygame.event.post( evt )

                    if fullscreen:
                        screen = pygame.display.set_mode( screen_size, pygame.FULLSCREEN )
                    else:
                        screen = pygame.display.set_mode( screen_size  )

            elif event.type == Button.EVT_BTN:
                if event.action == Button.QUERY:
#                    print "button %s wants to know what state it should be in." % event.btn.name
                    if event.btn.name == "upgrade":
                        event.btn.state = Button.STATE_READY

                    elif event.btn.name == "sell":
                        event.btn.state = Button.STATE_GHOST

                elif event.action == Button.CLICK:
                    print "Clicked ", event.btn.name
 
        screen.fill(BLACK)

        toolbar.Update()
        toolbar.Draw(screen)
            
        pygame.display.flip()
        

