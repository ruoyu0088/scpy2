# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import Range, Bool, Instance, Array, Int, on_trait_change
from traitsui.api import Item, Group, VGroup, HGroup, ArrayEditor
from .demobase import ImageProcessDemo
from scpy2.matplotlib.polygon_widget import PolygonWidget
from matplotlib.collections import LineCollection, EllipseCollection
from matplotlib import patches

COLORS = np.array([[0, 0.0, 0.5], [1, 0, 0]])


class SURFDemo(ImageProcessDemo):
    TITLE = "SURF Demo"
    DEFAULT_IMAGE = "lena.jpg"
    SETTINGS = ["m_perspective", "hessian_threshold", "n_octaves"]
    m_perspective = Array(np.float, (3, 3))
    m_perspective2 = Array(np.float, (3, 3))

    hessian_threshold = Int(2000)
    n_octaves = Int(2)

    poly = Instance(PolygonWidget)

    def control_panel(self):
        return VGroup(
            Item("m_perspective", label=u"变换矩阵", editor=ArrayEditor(format_str="%g")),
            Item("m_perspective2", label=u"变换矩阵", editor=ArrayEditor(format_str="%g")),
            Item("hessian_threshold", label=u"hessianThreshold"),
            Item("n_octaves", label=u"nOctaves")
        )

    def __init__(self, **kwargs):
        super(SURFDemo, self).__init__(**kwargs)
        self.poly = None
        self.init_points = None
        self.lines = LineCollection([], linewidths=1, alpha=0.6, color="red")
        self.axe.add_collection(self.lines)
        self.connect_dirty("poly.changed,hessian_threshold,n_octaves")

    def init_poly(self):
        if self.poly is None:
            return
        h, w, _ = self.img_color.shape
        self.init_points = np.array([(w, 0), (2*w, 0), (2*w, h), (w, h)], np.float32)
        self.poly.set_points(self.init_points)
        self.poly.update()

    def init_draw(self):
        style = {"marker": "o"}
        self.poly = PolygonWidget(axe=self.axe, points=np.zeros((3, 2)), style=style)
        self.init_poly()

    @on_trait_change("hessian_threshold, n_octaves")
    def calc_surf1(self):
        self.surf = cv2.SURF(self.hessian_threshold, self.n_octaves)
        self.key_points1, self.features1 = self.surf.detectAndCompute(self.img_gray, None)
        self.key_positions1 = np.array([kp.pt for kp in self.key_points1])

    def _img_changed(self):
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.img_color = cv2.cvtColor(self.img_gray, cv2.COLOR_GRAY2RGB)
        self.img_show = np.concatenate([self.img_color, self.img_color], axis=1)
        self.size = self.img_color.shape[1], self.img_color.shape[0]
        self.calc_surf1()

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=100)

        self.matcher = cv2.FlannBasedMatcher(index_params, search_params)

        self.init_poly()

    def settings_loaded(self):
        src = self.init_points.copy()
        w, h = self.size
        src[:, 0] -= w
        dst = cv2.perspectiveTransform(src[None, :, :], self.m_perspective)
        dst = dst.squeeze()
        dst[:, 0] += w
        self.poly.set_points(dst)
        self.poly.update()

    def draw(self):
        if self.poly is None:
            return
        w, h = self.size
        src = self.init_points.copy()
        dst = self.poly.points.copy().astype(np.float32)
        src[:, 0] -= w
        dst[:, 0] -= w
        m = cv2.getPerspectiveTransform(src, dst)
        self.m_perspective = m
        img2 = cv2.warpPerspective(self.img_gray, m, self.size, borderValue=[255]*4)
        self.img_show[:, w:, :] = img2[:, :, None]
        key_points2, features2 = self.surf.detectAndCompute(img2, None)

        key_positions2 = np.array([kp.pt for kp in key_points2])

        match_list = self.matcher.knnMatch(self.features1, features2, k=1)
        index1 = np.array([m[0].queryIdx for m in match_list])
        index2 = np.array([m[0].trainIdx for m in match_list])

        distances = np.array([m[0].distance for m in match_list])

        n = min(50, len(distances))
        best_index = np.argsort(distances)[:n]
        matched_positions1 = self.key_positions1[index1[best_index]]
        matched_positions2 = key_positions2[index2[best_index]]

        self.m_perspective2, mask = cv2.findHomography(matched_positions1, matched_positions2, cv2.RANSAC)

        lines = np.concatenate([matched_positions1, matched_positions2], axis=1)
        lines[:, 2] += w
        line_colors = COLORS[mask.ravel()]
        self.lines.set_segments(lines.reshape(-1, 2, 2))
        self.lines.set_color(line_colors)
        self.draw_image(self.img_show)


if __name__ == '__main__':
    demo = SURFDemo()
    demo.configure_traits()