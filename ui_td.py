import ui
import pygame.mixer
from pygame.locals import *

class Text(object):
    EVT_STATS = USEREVENT+2    

    def __init__(self, pt):
        self.font = pygame.font.SysFont( "Bitstream Vera Sans", 10 )
        self.pt = pt
        self.text = "0000000"

    def Draw(self, surf, pt):
        if self.surf is not None:
            surf.blit(self.surf, self.pt, None, 0)

    def Update(self):
        self.surf = self.font.render(self.text, False, (0,255,0))

    def Mouse(self, evt):
        pass

    def GetRelativeRect(self):
        return pygame.Rect(0,0,0,0)


class TDToolbar(ui.Toolbar):
    def __init__(self, screen):
        super(TDToolbar,self).__init__(screen, "ui00.png", (640-80,0))

        btn_click = pygame.mixer.Sound("sounds/9245__burnttoys__click_clean.wav")

        btn = ui.Button(screen, "btn_sell.png", (10,65), (640-80,0), btn_click )
        btn.name = "sell"
        self.AddChild( btn )

        btn = ui.Button(screen, "btn_upgrade.png", (10,95), (640-80,0), btn_click )
        btn.name = "upgrade"
        self.AddChild( btn )

        btn = ui.Button(screen, "btn-t1.png", (20,210), (640-80,0), btn_click )
        btn.name = "t1"
        self.AddChild( btn )

#        stats = Stats((640-80+15,35))
#        self.AddChild( stats )
