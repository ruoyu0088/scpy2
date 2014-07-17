# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import Array, Property, List, Bool, Event, Range, TraitError
from traitsui.api import Item, VGroup
from .demobase import ImageProcessDemo


class RemapDemo(ImageProcessDemo):
    TITLE = "Remap Demo"
    DEFAULT_IMAGE = "lena.jpg"

    offsetx = Array
    offsety = Array
    gridx = Array
    gridy = Array
    need_redraw = Event
    need_update_map = Bool
    radius = Range(10, 50, 20)
    sigma = Range(10, 50, 30)
    history = List()
    history_len = Property(depends_on="history")

    def __init__(self, **kw):
        super(RemapDemo, self).__init__(**kw)
        self.figure.canvas_events = [
            ("button_press_event", self.on_figure_press),
            ("button_release_event", self.on_figure_release),
            ("motion_notify_event", self.on_figure_motion),
            ('scroll_event', self.on_scroll),
        ]
        self.connect_dirty("need_redraw")
        self.target_pos = self.source_pos = None

    def control_panel(self):
        return VGroup(
            "radius", "sigma", Item("history_len", style="readonly"),
        )

    def _get_history_len(self):
        return len(self.history)

    def on_scroll(self, event):
        try:
            if event.key == "shift":
                self.sigma = int(self.sigma + event.step)
            else:
                self.radius = int(self.radius + event.step)
        except TraitError:
            pass


    def on_figure_press(self, event):
        if event.inaxes is self.axe and event.button == 1:
            self.target_pos = int(event.xdata), int(event.ydata)
        elif event.button == 3:
            if self.history:
                self.img[:] = self.history.pop()[:]
                self.need_redraw = True

    def on_figure_release(self, event):
        if event.inaxes is self.axe and event.button == 1:
            self.source_pos = int(event.xdata), int(event.ydata)
            self.need_redraw = True
            self.need_update_map = True

    def on_figure_motion(self, event):
        if event.inaxes is self.axe and event.button == 1:
            self.source_pos = int(event.xdata), int(event.ydata)
            self.need_redraw = True

    def _img_changed(self):
        self.offsetx = np.zeros(self.img.shape[:2], dtype=np.float32)
        self.offsety = np.zeros(self.img.shape[:2], dtype=np.float32)
        self.gridy, self.gridx = np.mgrid[:self.img.shape[0], :self.img.shape[1]]
        self.gridx = self.gridx.astype(np.float32)
        self.gridy = self.gridy.astype(np.float32)

    def draw(self):
        self.offsetx.fill(0)
        self.offsety.fill(0)

        if self.source_pos is not None and self.target_pos is not None:
            sx, sy = self.source_pos
            tx, ty = self.target_pos
            mask = ((self.gridx - sx)**2 + (self.gridy - sy)**2) < self.radius**2
            self.offsetx[mask] = tx - sx
            self.offsety[mask] = ty - sy
            cv2.GaussianBlur(self.offsetx, (0, 0), self.sigma, self.offsetx)
            cv2.GaussianBlur(self.offsety, (0, 0), self.sigma, self.offsety)

        img2 = cv2.remap(self.img,
                         self.offsetx + self.gridx,
                         self.offsety + self.gridy, cv2.INTER_LINEAR)
        self.draw_image(img2)

        if self.need_update_map:
            self.history.append(self.img.copy())
            if len(self.history) > 10:
                del self.history[0]
            self.img[:] = img2[:]
            self.source_pos = self.target_pos = None
            self.need_update_map = False


if __name__ == '__main__':
    demo = RemapDemo()
    demo.configure_traits()