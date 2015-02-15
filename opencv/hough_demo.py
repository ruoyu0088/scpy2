# -*- coding: utf-8 -*-
import cv2
import numpy as np
from traits.api import Range, Bool
from traitsui.api import Item, Group, VGroup, HGroup
from .demobase import ImageProcessDemo
from matplotlib.collections import LineCollection, EllipseCollection
from matplotlib import patches

class HoughDemo(ImageProcessDemo):
    TITLE = u"Hough Demo"
    DEFAULT_IMAGE = "stuff.jpg"
    SETTINGS = ["th2", "show_canny", "rho", "theta", "hough_th",
                "minlen", "maxgap", "dp", "mindist", "param2",
                "min_radius", "max_radius", "blur_sigma",
                "linewidth", "alpha", "check_line", "check_circle"]

    check_line = Bool(True)
    check_circle = Bool(True)

    #Gaussian blur parameters
    blur_sigma = Range(0.1, 5.0, 2.0)
    show_blur = Bool(False)

    # Canny parameters
    th2 = Range(0.0, 255.0, 200.0)
    show_canny = Bool(False)

    # HoughLine parameters
    rho = Range(1.0, 10.0, 1.0)
    theta = Range(0.1, 5.0, 1.0)
    hough_th = Range(1, 100, 40)
    minlen = Range(0, 100, 10)
    maxgap = Range(0, 20, 10)

    # HoughtCircle parameters

    dp = Range(1.0, 5.0, 1.9)
    mindist = Range(1.0, 100.0, 50.0)
    param2 = Range(5, 100, 50)
    min_radius = Range(5, 100, 20)
    max_radius = Range(10, 100, 70)

    # draw parameters
    linewidth = Range(1.0, 3.0, 1.0)
    alpha = Range(0.0, 1.0, 0.6)

    def control_panel(self):
        return VGroup(
            Group(
                Item("blur_sigma", label=u"标准方差"),
                Item("show_blur", label=u"显示结果"),
                label=u"高斯模糊参数"
            ),
            Group(
                Item("th2", label=u"阈值2"),
                Item("show_canny", label=u"显示结果"),
                label=u"边缘检测参数"
            ),
            Group(
                Item("rho", label=u"偏移分辨率(像素)"),
                Item("theta", label=u"角度分辨率(角度)"),
                Item("hough_th", label=u"阈值"),
                Item("minlen", label=u"最小长度"),
                Item("maxgap", label=u"最大空隙"),
                label=u"直线检测"
            ),
            Group(
                Item("dp", label=u"分辨率(像素)"),
                Item("mindist", label=u"圆心最小距离(像素)"),
                Item("param2", label=u"圆心检查阈值"),
                Item("min_radius", label=u"最小半径"),
                Item("max_radius", label=u"最大半径"),
                label=u"圆检测"
            ),
            Group(
                Item("linewidth", label=u"线宽"),
                Item("alpha", label=u"alpha"),
                HGroup(
                    Item("check_line", label=u"直线"),
                    Item("check_circle", label=u"圆"),
                ),
                label=u"绘图参数"
            )
        )

    def __init__(self, **kwargs):
        super(HoughDemo, self).__init__(**kwargs)
        self.connect_dirty("th2, show_canny, show_blur, rho, theta, hough_th,"
                            "min_radius, max_radius, blur_sigma,"
                           "minlen, maxgap, dp, mindist, param2, "
                           "linewidth, alpha, check_line, check_circle")
        self.lines = LineCollection([], linewidths=2, alpha=0.6)
        self.axe.add_collection(self.lines)

        self.circles = EllipseCollection(
            [], [], [],
            units="xy",
            facecolors="none",
            edgecolors="red",
            linewidths=2,
            alpha=0.6,
            transOffset=self.axe.transData)

        self.axe.add_collection(self.circles)

    def _img_changed(self):
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

    def draw(self):
        img_smooth = cv2.GaussianBlur(self.img_gray, (0, 0), self.blur_sigma, self.blur_sigma)
        img_edge = cv2.Canny(img_smooth, self.th2 * 0.5, self.th2)

        if self.show_blur and self.show_canny:
            show_img = cv2.cvtColor(np.maximum(img_smooth, img_edge), cv2.COLOR_BAYER_BG2BGR)
        elif self.show_blur:
            show_img = cv2.cvtColor(img_smooth, cv2.COLOR_BAYER_BG2BGR)
        elif self.show_canny:
            show_img = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2BGR)
        else:
            show_img = self.img

        if self.check_line:
            theta = self.theta / 180.0 * np.pi
            lines = cv2.HoughLinesP(img_edge,
                                    self.rho, theta, self.hough_th,
                                    minLineLength=self.minlen,
                                    maxLineGap=self.maxgap)

            if lines is not None:
                lines = lines[0]
                lines.shape = -1, 2, 2
                self.lines.set_segments(lines)
                self.lines.set_visible(True)
            else:
                self.lines.set_visible(False)
        else:
            self.lines.set_visible(False)

        if self.check_circle:
            circles = cv2.HoughCircles(img_smooth, 3,
                                       self.dp, self.mindist,
                                       param1=self.th2,
                                       param2=self.param2,
                                       minRadius=self.min_radius,
                                       maxRadius=self.max_radius)

            if circles is not None:
                circles = circles[0]
                self.circles._heights = self.circles._widths = circles[:, 2]
                self.circles.set_offsets(circles[:, :2])
                self.circles._angles = np.zeros(len(circles))
                self.circles._transOffset = self.axe.transData
                self.circles.set_visible(True)
            else:
                self.circles.set_visible(False)
        else:
            self.circles.set_visible(False)

        self.lines.set_linewidths(self.linewidth)
        self.circles.set_linewidths(self.linewidth)
        self.lines.set_alpha(self.alpha)
        self.circles.set_alpha(self.alpha)

        self.draw_image(show_img)


if __name__ == '__main__':
    demo = HoughDemo()
    demo.configure_traits()