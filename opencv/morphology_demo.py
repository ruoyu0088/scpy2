# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import Array, Enum, Int, Range
from traitsui.api import View, Item, VGroup
from .demobase import ImageProcessDemo

FUNCTIONS = ["dilate", "erode", "MORPH_OPEN", "MORPH_CLOSE",
             "MORPH_GRADIENT", "MORPH_TOPHAT", "MORPH_BLACKHAT"]


class MorphologyDemo(ImageProcessDemo):
    TITLE = u"Morphology Demo"
    DEFAULT_IMAGE = "squares.png"
    SETTINGS = ["structing_element", "process_type", "iter"]

    structing_element = Array(shape=(3, 3), dtype=np.uint8)
    process_type = Enum(FUNCTIONS)
    iter = Range(1, 30, 2)

    def control_panel(self):
        return VGroup(
            Item("structing_element", label=u"结构元素"),
            Item("process_type", label=u"处理类型"),
            Item("iter", label=u"迭代次数"),
        )

    def __init__(self, *args, **kwargs):
        super(MorphologyDemo, self).__init__(*args, **kwargs)
        self.structing_element = np.ones((3, 3), dtype=np.uint8)
        self.connect_dirty("structing_element,process_type,iter")

    def draw(self):
        if self.process_type.startswith("MORPH_"):
            type_id = getattr(cv2, self.process_type)
            img2 = cv2.morphologyEx(self.img, type_id,
                                    self.structing_element, iterations=self.iter)
        else:
            func = getattr(cv2, self.process_type)
            img2 = func(self.img,  self.structing_element, iterations=self.iter)

        self.draw_image(img2)


if __name__ == '__main__':
    demo = MorphologyDemo()
    demo.configure_traits()