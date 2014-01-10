import pygame

class ImageCache(object):
    images = {} # A dictionary of image name keys, followed by a list of surfaces

    # Images have alpha via PNG
    # sub images are loaded from left to right, top to bottom per size.
    @staticmethod
    def SetImageFile(filename, size):
        ImageCache.images[filename] = []
        img_list = ImageCache.images[filename] 
        img = pygame.image.load(filename)
        
        print "loading %s, %dx%d" % (filename, img.get_width(), img.get_height())
        
        for y in xrange(0, img.get_height(),size[1]):
            for x in xrange(0, img.get_width(),size[0]):
                r = pygame.Rect(x,y, size[0], size[1])
                print "\tloading rect", r
                s = img.subsurface(r)
                img_list.append( s  )

        print "%s: loaded %d" % (filename, len(img_list))
        return len(img_list)
        
    @staticmethod
    def GetImage(filename, idx):
        # print "%s %s" % (filename, idx)
        try:
            return ImageCache.images[filename][idx]
        except IndexError:
            print "%s doesn't have index %d cached" % (filename, idx)
