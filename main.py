import gi
import numpy as np
import itertools

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging

logger = logging.getLogger('glow')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


CHANNELS = 3
WIDTH, HEIGHT = 1920, 1080
MEAN_WINDOW_WIDTH = 120
MEAN_WINDOW_HEIGHT = 120

def get_root_window_pixels_and_dimensions():
    window = Gdk.get_default_root_window()
    x, y, w, h = window.get_geometry()
    logger.debug(f'root window {x} {y} {w} {h}')
    return Gdk.pixbuf_get_from_window(window, x, y, w, h), w, h


def pixbuf_to_numpy(pixbuf, w, h):
    arr = np.frombuffer(pixbuf.get_pixels(), dtype=np.uint8).reshape((h, w, CHANNELS))
    logger.debug(f'numpy from pixbuf shape {arr.shape}')
    # print(arr.shape, np.mean(arr, axis=tuple(range(arr.ndim-1))))
    return arr


def get_grid(monitor, w, h):
    xs = list(range(0, monitor.shape[1], w))
    ys = list(range(0, monitor.shape[0], h))
    # grid = list(itertools.product(xs, ys))
    # logger.debug(grid)
    return xs, ys


def get_means(monitor, grid):
    xs, ys = grid
    means = np.empty((len(ys), len(xs), CHANNELS), dtype=np.uint8)
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            means[i, j] = np.mean(monitor[y:y + MEAN_WINDOW_HEIGHT, x:x + MEAN_WINDOW_WIDTH, :], axis=tuple(range(monitor.ndim - 1)))
    logger.debug(f'means shape {means.shape}')
    means = means.astype(np.float) / np.iinfo(np.uint8).max
    return means


class Glow(Gtk.Window):
    def __init__(self):
        super(Glow, self).__init__()
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.add(darea)
        self.resize(460, 240)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
        self.set_title("Glow")
        self.W = 48
        self.H = 48 
        
    
    def on_draw(self, wid, cr):
        pixels, w, h = get_root_window_pixels_and_dimensions()
        pixels = pixbuf_to_numpy(pixels, w, h)
        monitors = [pixels[:, b:b + WIDTH, :] for b in range(0, pixels.shape[1], WIDTH)]
        grids = [get_grid(m, MEAN_WINDOW_WIDTH, MEAN_WINDOW_HEIGHT) for m in monitors]
        means = [get_means(m, g) for m, g in zip(monitors, grids)]
        mean = means[0]
        for i in range(mean.shape[0]):
            for j in range(mean.shape[1]):
                self._draw_rectangle(cr, j * self.W, i * self.H, mean[i, j])  


    def _draw_rectangle(self, cr, x, y, rgb):
        cr.set_source_rgb(*rgb)
        cr.set_line_width(1)
        cr.rectangle(x, y, self.W, self.H)
        cr.fill()



def main():
    app = Glow()
    Gtk.main()


if __name__ == '__main__':
    main()
