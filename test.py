# pylint: disable=E1101
import cairo

WIDTH = 200
HEIGHT = 200

cairo.ImageSurface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.scale(HEIGHT, WIDTH)
surface.write_to_png("test.png")