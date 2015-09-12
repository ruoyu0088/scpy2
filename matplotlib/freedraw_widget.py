# -*- coding: utf-8 -*-
from traits.api import Event, HasTraits, Bool
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg
import matplotlib.patches as mpatches
import matplotlib.image as mimage
import matplotlib.transforms as mtrans
import numpy as np
from pyface.timer.api import Timer


class ImageMaskDrawer(HasTraits):
    mask_updated = Event
    drawed = Event
    is_dirty = Bool(False)

    def __init__(self, ax, img=None, mask_shape=None, canmove=True, size=None):
        self.canmove = canmove
        self.ax = ax
        if size is None:
            size = 10

        self.bbox = mtrans.Bbox(np.array([[0, 0], [10, 10]]))
        bbox = mtrans.TransformedBbox(self.bbox, ax.transData)
        self.mask_img = mimage.BboxImage(bbox, animated=True, alpha=0.6, zorder=1000)
        self.ax.add_artist(self.mask_img)

        self.create_mask(img, mask_shape)

        self.canvas = ax.figure.canvas
        self.event_ids = [
            self.canvas.mpl_connect('motion_notify_event', self.on_move),
            self.canvas.mpl_connect('draw_event', self.on_draw),
            self.canvas.mpl_connect('button_press_event', self.on_press),
            self.canvas.mpl_connect('button_release_event', self.on_release),
            self.canvas.mpl_connect('scroll_event', self.on_scroll),
        ]
        self.circle = mpatches.Circle((0, 0), size, facecolor="red",
                                      alpha=0.5, animated=True)
        self.ax.add_patch(self.circle)

        self.mask_circle = mpatches.Circle((0, 0), 10, facecolor="white",
                                           lw=0)
        self.mask_line = plt.Line2D((0, 0), (0, 0), lw=18,
                                    solid_capstyle="round",
                                    color="white")
        self.background = None
        self.last_pos = None

        self.timer = Timer(40, self.check_dirty)

    def remove(self):
        self.mask_img.remove()
        self.circle.remove()
        for event_id in self.event_ids:
            self.canvas.mpl_disconnect(event_id)

    def check_dirty(self):
        if self.is_dirty:
            self._update()
            self.is_dirty = False

    def create_mask(self, img=None, mask_shape=None):
        if mask_shape is None:
            self.height, self.width = img.shape[:2]
        else:
            self.height, self.width = mask_shape
        self.renderer = RendererAgg(self.width, self.height, 90)
        buf = self.renderer.buffer_rgba()
        arr = np.frombuffer(buf, np.uint8)
        self.array = arr.reshape(self.height, self.width, 4)
        self.mask_img.set_data(self.array)
        self.bbox.set_points(np.array([[0, 0], [self.width, self.height]]))

    def clear_mask(self):
        self.array[:, :, :-1] = 255
        self.array[:, :, -1] = 0

    def get_mask_array(self):
        return self.array[:, :, -1].copy()

    def get_mask_offset(self):
        box = self.mask_img.bbox._bbox
        return box.x0, box.y0

    def on_scroll(self, event):
        radius = self.circle.get_radius()
        radius += event.step
        radius = max(3, min(30, radius))
        self.circle.set_radius(radius)
        self.mask_circle.set_radius(radius)
        self.mask_line.set_linewidth(radius * 2 - 2)
        self._update()

    def transform_pos(self, x, y):
        box = self.mask_img.bbox._bbox
        return x - box.x0, y - box.y0

    def on_press(self, event):
        buttons = (1, 3) if self.canmove else (1, )
        if event.button in buttons and event.inaxes is self.ax:
            self.mask_img.set_visible(True)
            self.img_pos = self.mask_img.bbox._bbox.get_points()
            self.last_pos = self.transform_pos(event.xdata, event.ydata)
            self.last_pos2 = event.xdata, event.ydata
            self.mask_circle.center = self.last_pos
            if event.button == 1:
                self.mask_circle.draw(self.renderer)
                self.mask_updated = True
            self.mask_img.set_array(self.array)
            self.is_dirty = True

    def on_release(self, event):
        self.last_pos = None
        if event.button == 1 and event.inaxes is self.ax:
            self.drawed = True

    def on_draw(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.mask_img.set_array(self.array)
        self.ax.draw_artist(self.mask_img)
        if self.circle.get_visible():
            self.ax.draw_artist(self.circle)
        self.canvas.blit(self.ax.bbox)

    def on_move(self, event):
        self.is_dirty = True

        if event.inaxes != self.ax:
            self.circle.set_visible(False)
            return

        self.circle.set_visible(True)
        self.circle.center = event.xdata, event.ydata
        if event.button == 1 and self.last_pos is not None:
            pos = self.transform_pos(event.xdata, event.ydata)
            self.mask_line.set_data((self.last_pos[0], pos[0]),
                                    (self.last_pos[1], pos[1]))
            self.mask_line.draw(self.renderer)
            self.last_pos = pos
            self.mask_updated = True
        if self.canmove and event.button == 3 and self.last_pos is not None:
            xdata, ydata = event.xdata, event.ydata
            dx = self.last_pos2[0] - xdata
            dy = self.last_pos2[1] - ydata
            new_pos = self.img_pos - [dx, dy]
            self.mask_img.bbox._bbox.set_points(new_pos)
            self.mask_img.bbox.invalidate()

    def _update(self):
        if self.background is not None:
            self.canvas.restore_region(self.background)

        self.mask_img.set_array(self.array)
        self.ax.draw_artist(self.mask_img)
        if self.circle.get_visible():
            self.ax.draw_artist(self.circle)
        self.canvas.blit(self.ax.bbox)

    def update(self):
        # self.mask_img.set_array(self.array)
        self._update()

    def hide_mask(self):
        self.mask_img.set_visible(False)

    def show_mask(self):
        self.mask_img.set_visible(True)


if __name__ == "__main__":
    ax = plt.subplot()
    arr = np.zeros((500, 500, 3), dtype=np.uint8)
    img = ax.imshow(arr, origin="upper")
    drawer = ImageMaskDrawer(ax, arr)
    ax.axis((0, 500, 0, 500))
    plt.show()