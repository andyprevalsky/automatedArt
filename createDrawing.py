# pylint: disable=E1101
import cairo
import math
import numpy


class Drawing():
    """ creates a context at 0, 0 with specified width and height """
    def __init__(self, WIDTH, HEIGHT):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        self.brushWidth = 1
        self.ctx = cairo.Context(self.surface)
        self.ctx.rectangle(0, 0, 200, 200)
        self.ctx.set_source_rgb(255, 255, 255)
        self.ctx.fill() 
        self.ctx.set_line_width(self.brushWidth)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.move_to(0, 0)
        return

    def drawArc(self, x, y, radius, startAngle, endAngle):
        """ start x, start y, radius, startAngle in radians, endAngle in radians """ 
        self.ctx.new_sub_path()
        self.ctx.arc(x, y, radius, startAngle, endAngle)
        self.ctx.stroke()
        return

    def setBrush(self, r, g, b, a, width = 1):
        """ sets brush to color of specified variables, width can be specified to change brush size """
        self.ctx.set_source_rgba(r, g, b, a)
        return

    def output(self, outputFile):
        """ writes surface to png with corresponding output file """
        self.surface.write_to_png(outputFile)
        return


def normSample(mean, std, samples) :
    """ sample from normal distribution with params, mean, standard deviation
        and number of samples """
    return numpy.random.normal(mean, std, samples)

canvas = Drawing(200, 200)
canvas.drawArc(100, 100, 10, math.pi/2, math.pi)
canvas.drawArc(100, 100, 15, math.pi/2, math.pi)
canvas.drawArc(100, 100, 20, math.pi/2, math.pi)
for i in range(50):
    x = normSample(100, 30, 1)
    y = normSample(100, 30, 1)
    radius = normSample(10, 60, 1)
    

canvas.output("test.png")
