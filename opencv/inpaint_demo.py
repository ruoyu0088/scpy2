# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import (HasTraits, Float, Instance,
                        Enum, List, Range, Bool, Button, Event, on_trait_change)
from traitsui.api import View, VGroup, Item, HGroup
from scpy2.matplotlib.freedraw_widget import ImageMaskDrawer
from .demobase import ImageProcessDemo


class InPaintDemo(ImageProcessDemo):
    YAXIS_DIRECTION = "up"
    TITLE = u"Inpaint Demo"
    DEFAULT_IMAGE = "stuff.jpg"

    mask_artist = Instance(ImageMaskDrawer)
    r = Range(2.0, 20.0, 10.0)  # inpaint的半径参数
    method = Enum("INPAINT_NS", "INPAINT_TELEA")  # inpaint的算法
    show_mask = Bool(False)  # 是否显示选区
    clear_mask = Button(u"清除选区")
    apply = Button(u"保存结果")

    def control_panel(self):
        return VGroup(
            Item("r", label=u"inpaint半径"),
            Item("method", label=u"inpaint算法"),
            Item("show_mask", label=u"显示选区"),
            Item("clear_mask", show_label=False),
            Item("apply", show_label=False),
        )

    def __init__(self, **kw):
        super(InPaintDemo, self).__init__(**kw)
        self.connect_dirty("r, method")

    def init_draw(self):
        self.mask_artist = ImageMaskDrawer(self.axe, self.img,
                                           canmove=False, size=15)
        self.mask_artist.on_trait_change(self.draw, "drawed")

    def draw(self):
        if self.mask_artist is None:
            self.draw_image(self.img)
            return
        mask = self.mask_artist.get_mask_array()
        if self.img.shape[:2] == mask.shape:
            img2 = cv2.inpaint(self.img, mask, self.r, getattr(cv2, self.method))
            self.img2 = img2
            self.show_mask = False
            self.mask_artist.hide_mask()
            self.draw_image(img2)
        else:
            self.draw_image(self.img)

    def _img_changed(self):
        if self.mask_artist is not None:
            self.mask_artist.create_mask(img=self.img)

    def _show_mask_changed(self):
        if self.show_mask:
            self.mask_artist.show_mask()
        else:
            self.mask_artist.hide_mask()
        self.figure.canvas.draw()

    def _clear_mask_fired(self):
        self.mask_artist.clear_mask()
        self.draw()

    def _apply_fired(self):
        if hasattr(self, "img2"):
            self.img[:] = self.img2[:]
        self.clear_mask = True


if __name__ == '__main__':
    demo = InPaintDemo()
    demo.configure_traits()