import gi
import numpy as np

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

window = Gdk.get_default_root_window()
x, y, w, h = window.get_geometry()
print(x, y, w, h)
screen = Gdk.pixbuf_get_from_window(window, x, y, w, h)
print(screen.get_has_alpha())

arr = np.frombuffer(screen.get_pixels(), dtype=np.uint8).reshape((h,w,3))

print(arr.shape, np.mean(arr, axis=tuple(range(arr.ndim-1))))
