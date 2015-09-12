# -*- coding: utf-8 -*-
import cv2
import numpy as np
from numpy import fft
from traits.api import Instance, Button, List, Bool, Event, Range, TraitError
from traitsui.api import Item, VGroup
from scpy2.matplotlib.freedraw_widget import ImageMaskDrawer
from .demobase import ImageProcessDemo


FFT_SIZE = 512


def normalize_gray_image(img):
    vmin, vmax = img.min(), img.max()
    return ((img - vmin) / (vmax - vmin) * 255).astype(np.uint8)


class FFT2DDemo(ImageProcessDemo):
    YAXIS_DIRECTION = "up"
    TITLE = "FFT2D Demo"
    DEFAULT_IMAGE = "lena.jpg"

    mask_artist = Instance(ImageMaskDrawer)
    reset = Button(u"Reset")

    def __init__(self, **kw):
        super(FFT2DDemo, self).__init__(**kw)
        self.mask_artist = None
        self.figure.canvas_events = [
            ("button_press_event", self.on_button_pressed)
        ]

    def control_panel(self):
        return VGroup(
            "reset",
            show_labels=False,
        )

    def init_draw(self):
        self.mask_artist = ImageMaskDrawer(self.axe, mask_shape=(512, 512),
                                           canmove=False, size=15)
        self.connect_dirty("mask_artist.mask_updated")

    def on_button_pressed(self, event):
        if event.inaxes is self.axe:
            if event.button == 3:
                self._reset_fired()

    def _reset_fired(self):
        self.mask_artist.clear_mask()
        self.mask_artist.update()
        self.draw()

    def _img_changed(self):
        img = cv2.resize(self.img, (FFT_SIZE, FFT_SIZE))
        w, h = img.shape[:2]

        self.img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[:FFT_SIZE, :FFT_SIZE].copy()
        self.img_freq = fft.fft2(self.img_gray)
        self.img_mag = fft.fftshift(np.log10(np.abs(self.img_freq)))
        self.img_show = np.hstack((img[:FFT_SIZE, :FFT_SIZE, :], img[:FFT_SIZE, :FFT_SIZE, :]))
        self.img_show[:FFT_SIZE, FFT_SIZE:, :] = self.img_gray[:FFT_SIZE, :FFT_SIZE, None]

        img_uint8 = normalize_gray_image(self.img_mag)
        self.img_show[:FFT_SIZE, :FFT_SIZE, :] = img_uint8[:, :, None]

    def draw(self):
        if self.mask_artist is None:
            self.draw_image(self.img_show)
            return

        mask = self.mask_artist.get_mask_array().astype(np.bool)

        if np.any(mask):
            y, x = np.where(mask)
            m = (y > 0) & (x > 0)
            x, y = x[m], y[m]
            mask[FFT_SIZE - y, FFT_SIZE - x] = True
            self.mask_artist.array[:, :, -1] = mask * 255
            filtered_img = fft.ifft2(self.img_freq * fft.fftshift(mask)).real
            filtered_img = normalize_gray_image(filtered_img)
            self.img_show[:FFT_SIZE, FFT_SIZE:, :] = filtered_img[:, :, None]
        else:
            self.img_show[:FFT_SIZE, FFT_SIZE:, :] = self.img_gray[:, :, None]

        self.draw_image(self.img_show)


if __name__ == '__main__':
    demo = FFT2DDemo()
    demo.configure_traits()