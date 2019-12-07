# pylint: disable=E1101, C0103, C0303, C0111, C0326, W0621, R0205, W0511
import time
import struct
import threading
import math
import Quartz.CoreGraphics as CG
from pngcanvas import PNGCanvas
from pynput.mouse import Listener, Button
from pynput import keyboard


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

class keyboardHooks():
    """ listenting to keyboard hooks for undoes """
    def __init__(self, screenPixel):
        self.running = True
        self.screenPixel = screenPixel
        self.commandPressed = False
    
    def on_press(self, key):
        if (self.running == False): return False
        if (key == keyboard.Key.cmd):
            self.commandPressed = True
        if (key == keyboard.KeyCode.from_char('z') and self.commandPressed): # undo buffer on cmd z
            self.screenPixel.undo()
        if (key == keyboard.KeyCode.from_char('s') and self.commandPressed): # save drawing on cmd s
            self.running = False
            m.running = False
            self.screenPixel.draw()

    def on_release(self, key):
        if (self.running == False): return False
        if (key == keyboard.Key.cmd):
            self.commandPressed = False

class MouseHooks():
    """ listenting to mouse hooks to capture drawings 
    on mouse click """
    def __init__(self, screenPixel):
        self.running = True
        self.screenPixel = screenPixel
        self.mousePressed = False
        self.currentMousePos = None
    
    # def click(self, x, y, button, press):
    #     if button == 1 and press:
    #         self.captureProcess = threading.Thread(target=self.callCapture)
    #         self.isRunning = True
    #         self.captureProcess.start()
    #         return
    #     elif button == 1 and not press:
    #         self.isRunning = False
    #         if self.captureProcess is None: 
    #             return
    #         self.captureProcess.join()
    #         self.screenPixel.writeLineBuffer()
    #     elif button == 2 and press:
    #         self.screenPixel.undo()


    def callCapture(self, x, y):
        threading.Thread(target=self.screenPixel.capture(x, y)).start()

    def on_move(self, x, y):
        if (self.running == False): return False
        self.currentMousePos = [x, y]
        if (self.mousePressed):
            self.callCapture(x,y)

    def on_click(self, x, y, button, pressed):
        if (self.running == False): return False
        self.currentMousePos = [x, y]
        self.screenPixel.previousMousePos = None
        self.mousePressed = pressed
        if button == Button.left and pressed:
            self.callCapture(x,y)
        elif button == Button.left and not pressed:
            self.screenPixel.writeLineBuffer()
        elif button == Button.right and pressed:
            self.screenPixel.undo()


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
        self.previousMousePos = None

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

        self.captureCount += 1
        print("Capturing " + str(self.captureCount))

        region = CG.CGRectMake(x-(self.width/2), y-(self.height/2), self.width, self.height)
        image = CG.CGWindowListCreateImage(
            region,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageDefault)

        # Intermediate step, get pixel data as CGDataProvider
        prov = CG.CGImageGetDataProvider(image)
        currMousePos = m.currentMousePos
        # Copy data out of CGDataProvider, becomes string of bytes
        self.lineBuffer.append([
            CG.CGDataProviderCopyData(prov), 
            CG.CGImageGetWidth(image), 
            CG.CGImageGetHeight(image),
            self.previousMousePos,
            currMousePos
        ])
        self.previousMousePos = currMousePos

    
    def getDirection(self, start, end):
        """ takes in start and end coordinates as 1-d 2 value arrays
        and return the angle between the two """
        #flip first val to atan2 because y val is reversed on screen mapping
        angle = (math.degrees(math.atan2(start[1] - end[1], end[0] - start[0])) + 360) % 360 
        return str(angle)

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
                if (self.counter % 10 != 0 and (self.counter - 1) % 10 != 0): 
                    self.counter += 1
                    continue
                if (pictureItem[3] == None): #pass over starts of lines
                    continue
                c = PNGCanvas(pictureItem[1], pictureItem[2])
                for x in range(pictureItem[1]):
                    for y in range(pictureItem[2]):
                        c.point(x, y, color = self.pixel(x, y, picture = pictureItem[0], width = pictureItem[1]))
                with open("screenCaptures/image" + str(self.counter) + ".png", "wb") as f:
                    f.write(c.dump())
                if (self.counter % 10 == 0):
                    with open("labels/" + str(self.counter) + ".txt", "wt") as f:
                        f.write(self.getDirection(pictureItem[3], pictureItem[4]))
                self.counter += 1
                print ("Done Writing " + str(self.counter) + " / " + str(totalPictures))
        self.dataBuffer = []

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

if __name__ == '__main__':
    sp = ScreenPixel(200, 200)
    m = MouseHooks(sp)
    k = keyboardHooks(sp)
    with Listener(on_move=m.on_move, on_click=m.on_click) as listener:
        with keyboard.Listener(on_press=k.on_press, on_release=k.on_release) as listener2:
            listener.join()
            listener2.join()
        
