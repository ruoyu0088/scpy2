# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import Enum
from traitsui.api import VGroup, Item
from scpy2.matplotlib.freedraw_widget import ImageMaskDrawer
from .demobase import ImageProcessDemo

MARKER_COLORS = np.array([
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 255),
]
, dtype=np.uint8)


class WatershedDemo(ImageProcessDemo):
    TITLE = u"Watershed Demo"
    DEFAULT_IMAGE = u"fruits.jpg"
    YAXIS_DIRECTION = "up"

    current_label = Enum(range(1, 10))

    def __init__(self, **kw):
        super(WatershedDemo, self).__init__(**kw)
        self.figure.canvas_events = [
            ("button_press_event", self.on_button_pressed)
        ]
        self.result_artist = self.axe.imshow(np.zeros((10, 10, 3), np.uint8), alpha=0.3)
        self.mask_artist = None
        self.markers = None

    def control_panel(self):
        return VGroup(
            Item("current_label", label=u"当前标签")
        )

    def on_button_pressed(self, event):
        if event.inaxes is self.axe and event.button == 3:
            if self.current_label < 9:
                self.current_label += 1
            else:
                self.current_label = 1

    def init_draw(self):
        h, w = self.img.shape[:2]
        if self.mask_artist is not None:
            self.mask_artist.remove()
        self.mask_artist = ImageMaskDrawer(self.axe, mask_shape=(h, w),
                                           canmove=False, size=10)
        self.mask_artist.on_trait_change(self.update_markers, "drawed")
        self.markers = np.zeros((h, w), dtype=np.int32)
        self.result = np.zeros((h, w), dtype=np.int32)

    def update_markers(self):
        mask = self.mask_artist.get_mask_array().astype(bool)
        y, x = np.where(mask)
        self.markers[y, x] = self.current_label
        self.mask_artist.clear_mask()
        self.draw()

    def draw(self):
        if self.markers is not None:
            if self.img.shape[:2] != self.markers.shape:
                self.init_draw()

            self.result[:] = self.markers
            cv2.watershed(self.img, self.result)
            img = MARKER_COLORS[self.result]
            self.draw_image(img, self.result_artist, draw=False)
            self.draw_image(self.img)


if __name__ == '__main__':
    demo = WatershedDemo()
    demo.configure_traits()
