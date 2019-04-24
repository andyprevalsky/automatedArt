# pylint: disable=E1101, C0103, C0303, C0111, C0326, W0621, R0205, W0511
import time
import struct
import Quartz.CoreGraphics as CG
import multiprocessing

class MouseHooks():
    """ listenting to mouse hooks to capture drawings 
    on mouse click """
    def __init__(self, screenPixel):
        self.screenPixel = screenPixel
        self.captureProcess = None

    def callCapture(self):
        #sleep for 25 ms, then call caputer
        self.screenPixel.capture(mouseX-100, mouseY-100)

    def onMouseRelease(self):
        if (self.captureProcess is None) return
        self.captureProcess.terminate()

    def onMouseDown(self):
        self.captureProcess = multiprocessing.Process(target=self.callCapture, args=(self,))


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

    def undo(self):
        if len(self.dataBuffer) == 0: return
        del self.dataBuffer[-1]
    
    def writeLineBuffer(self):
        self.dataBuffer.append(self.lineBuffer)
        self.lineBuffer = []

    def capture(self, x, y):
        if (x+self.width > self.mainMonitor.size.width or y+self.height > self.mainMonitor.size.height):
            print ("Capture out of Bounds")
            return
    
        region = CG.CGRectMake(x, y, self.width, self.height)
        image = CG.CGWindowListCreateImage(
            region,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageDefault)

        # Intermediate step, get pixel data as CGDataProvider
        prov = CG.CGImageGetDataProvider(image)

        # Copy data out of CGDataProvider, becomes string of bytes
        self.lineBuffer.append(CG.CGDataProviderCopyData(prov))

    def pixel(self, x, y):
        """Get pixel value at given (x,y) screen coordinates

        Must call capture first.
        """

        # Pixel data is unsigned char (8bit unsigned integer),
        # and there are for (blue,green,red,alpha)
        data_format = "BBBB"

        # Calculate offset, based on
        # http://www.markj.net/iphone-uiimage-pixel-color/
        offset = 4 * ((self.width*int(round(y))) + int(round(x)))

        # Unpack data from string into Python'y integers
        b, g, r, a = struct.unpack_from(data_format, self.dataBuffer[-1][-1], offset=offset)

        # Return BGRA as RGBA
        return (r, g, b, a)
    
    def draw(self):
         # To verify screen-cap code is correct, save all pixels to PNG,
        # using http://the.taoofmac.com/space/projects/PNGCanvas

        from pngcanvas import PNGCanvas
        c = PNGCanvas(self.width, self.height)
        for x in range(self.width):
            for y in range(self.height):
                c.point(x, y, color = self.pixel(x, y))

        with open("test.png", "wb") as f:
            f.write(c.dump())


if __name__ == '__main__':
    # Timer helper-function
    # import contextlib
 
    # @contextlib.contextmanager
    # def timer(msg):
    #     start = time.time()
    #     yield
    #     end = time.time()
    #     print ("%s: %.02fms" % (msg, (end-start)*1000))
    #       with timer("Capture"):

    # Example usage

    mainMonitor = CG.CGDisplayBounds(CG.CGMainDisplayID())
    print (mainMonitor.size.width, mainMonitor.size.height)
    sp = ScreenPixel(200, 200)
    region = CG.CGRectMake(100, 100, 200, 200)

    sp.capture(1440-200, 500)
    sp.draw()
