class ToolLayer(Layer):
    def __init__(self, rect):
        self.rect = rect
        self.tools = [] # RectTile's
        self.mouse_pos = None
        self.start_draw_idx = 0
        self.visible = True
        
    def Draw(self, surf):
        if not self.visible:
            return
            
        # Start at the right tile
        if False:
            x,y = self.rect.topleft
            for idx in range(self.start_draw_idx):
                y += rt.GetSurf().get_height()
            
        # Draw the current tile with a green border.    
        
            
        # Draw the visible tiles
        x,y = self.rect.topleft        
        for idx in range(self.start_draw_idx,len(self.tools)):
            rt = self.tools[idx]            
            rt.Draw(surf, (x,y))
            r = rt.GetSurf().get_rect()
            # Offset to use the tool layer's origin.
            r.topleft = (x,y)
            
            if TileCache.current_tile == idx:            
                pygame.draw.rect(surf, (0,255,0), r, 2)
                
            elif self.mouse_pos is not None:
                if r.collidepoint( self.mouse_pos ):
                    pygame.draw.rect(surf, (255,0,0), r, 2)                   
                    
            y += r.height
            if not self.rect.collidepoint( (x,y) ):
                break

        pygame.draw.rect(surf, (0,128,128), self.rect, 1)
                    
    def Mouse(self, evt):
        self.mouse_pos = evt.pos
        if event.type == pygame.MOUSEBUTTONUP:
            x,y = self.rect.topleft
            for idx in range(self.start_draw_idx,len(self.tools)):            
                r = self.tools[idx].GetSurf().get_rect()
                r.topleft = (x,y) 
                if r.collidepoint( evt.pos ):
                    TileCache.current_tile = idx
                    break
                y += r.height        

    def LoadTiles(self):
        for t in range(len(TileCache.tiles)):        
            tile = RectTile(t)        
            self.tools.append( RectTile(t) )
            
    def OnKey(self, evt):
        if  evt.key in [K_PAGEDOWN, K_PAGEUP]:
            # Count the tools visible
            x,y = self.rect.topleft
            count = 0
            for idx in range(self.start_draw_idx,len(self.tools)):            
                r = self.tools[idx].GetSurf().get_rect()
                r.topleft = (x,y) 
                if not self.rect.colliderect( r ):
                    break
                y += r.height
                count += 1

            offset = count / 2
            if evt.key == K_PAGEUP:
                offset *= -1
             
            self.start_draw_idx += offset
            self.start_draw_idx = max(0, self.start_draw_idx)
            self.start_draw_idx = min(len(self.tools)-count,self.start_draw_idx)
        if evt.key == K_h:
            self.visible = not self.visible

