# pylint: disable=E1101, C0103, C0303, C0111, C0326, W0621, R0205, W0511
import time
import struct
import threading
import Quartz.CoreGraphics as CG
from pngcanvas import PNGCanvas
from pymouse import PyMouse, PyMouseEvent

class MouseHooks(PyMouseEvent):
    """ listenting to mouse hooks to capture drawings 
    on mouse click """
    def __init__(self, screenPixel):
        self.screenPixel = screenPixel
        self.captureProcess = None
        self.mouse = PyMouse()
        self.isRunning = False
        PyMouseEvent.__init__(self)
    
    def click(self, x, y, button, press):
        if button == 1 and press:
            self.captureProcess = threading.Thread(target=self.callCapture)
            self.captureProcess.start()
            self.isRunning = True
            return
        elif button == 1 and not press:
            self.isRunning = False
            if self.captureProcess is None: 
                return
            self.captureProcess.join()
            self.screenPixel.writeLineBuffer()
        elif button == 2 and press:
            self.screenPixel.undo()
        

    def callCapture(self):
        print("starting")
        while (self.isRunning):
            mouseX = self.mouse.position()[0]
            mouseY = self.mouse.position()[1]
            self.screenPixel.capture(mouseX, mouseY)
            time.sleep(1/20)


class ScreenPixel(object):
    """Captures the screen using CoreGraphics, and provides access to
    the pixel values. first param is width of each shot, and second 
    is height of each shot
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.mainMonitor = CG.CGDisplayBounds(CG.CGMainDisplayID())
        self.dataBuffer = []
        self.lineBuffer = []
        self.counter = 0
        self.captureCount = 0

    def undo(self):
        print("UNDO")
        if self.dataBuffer == []: 
            return
        del self.dataBuffer[-1]
    
    def writeLineBuffer(self):
        if self.lineBuffer == []: return
        self.dataBuffer.append(self.lineBuffer)
        self.lineBuffer = []
        self.captureCount = 0

    def capture(self, x, y):
        if (x+(self.width/2) > self.mainMonitor.size.width or 
                y+(self.height/2) > self.mainMonitor.size.height
                or x-(self.width/2) < 0 or y-(self.height/2) < 0):
            print ("Capture out of Bounds")
            return

        print("Capturing " + str(self.captureCount))
        self.captureCount += 1

        region = CG.CGRectMake(x-(self.width/2), y-(self.height/2), self.width, self.height)
        image = CG.CGWindowListCreateImage(
            region,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageDefault)

        # Intermediate step, get pixel data as CGDataProvider
        prov = CG.CGImageGetDataProvider(image)

        # Copy data out of CGDataProvider, becomes string of bytes
        self.lineBuffer.append([CG.CGDataProviderCopyData(prov), CG.CGImageGetWidth(image), CG.CGImageGetHeight(image)])

    def pixel(self, x, y, picture, width):
        """Get pixel value at given (x,y) screen coordinates

        Must call capture first.
        """

        # Pixel data is unsigned char (8bit unsigned integer),
        # and there are for (blue,green,red,alpha)
        data_format = "BBBB"

        # Calculate offset, based on
        # http://www.markj.net/iphone-uiimage-pixel-color/
        offset = 4 * ((width*int(round(y))) + int(round(x)))

        # Unpack data from string into Python'y integers
        b, g, r, a = struct.unpack_from(data_format, picture, offset=offset)

        # Return BGRA as RGBA
        return (r, g, b, a)
    
    def draw(self):
         # To verify screen-cap code is correct, save all pixels to PNG,
        # using http://the.taoofmac.com/space/projects/PNGCanvas
        print("drawing")
        totalPictures = 0
        for line in self.dataBuffer:
            for _ in line:
                totalPictures += 1

            for line in self.dataBuffer:
                for pictureItem in line:
                    with open("screenCaptures/p" + str(self.counter) + ".txt" , 'w') as f:
                        f.write("%s\n" % pictureItem[0])
                    self.counter += 1
                    print ("Done Writing " + str(self.counter) + " / " + str(totalPictures))
        self.dataBuffer = []
        return

        # for line in self.dataBuffer:
        #     for pictureItem in line:
        #         c = PNGCanvas(pictureItem[1], pictureItem[2])
        #         for x in range(pictureItem[1]):
        #             for y in range(pictureItem[2]):
        #                 c.point(x, y, color = self.pixel(x, y, picture = pictureItem[0], width = pictureItem[1]))
        #         with open("test" + str(self.counter) + ".png", "wb") as f:
        #             f.write(c.dump())
        #         self.counter += 1
        #         print ("Done Writing " + str(self.counter) + " / " + str(totalPictures))
        # self.dataBuffer = []

if __name__ == '__main__':
    sp = ScreenPixel(200, 200)
    m = MouseHooks(sp)
    def drawImages():
        input("enter a character to draw")
        sp.draw()
    t = threading.Thread(target=drawImages)
    t.start()
    m.start()
    
        
