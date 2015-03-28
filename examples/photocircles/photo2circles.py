# -*- coding: utf-8 -*-
import numpy as np
import cv2
from cv2 import cv


def circle(cx, cy, radius, shape):
    dr = 1.0 / float(radius)
    r, c = np.ogrid[-1:1:dr, -1:1:dr]
    rr, cc = np.where(r**2 + c**2 < 1)
    rr = rr + cy - int(radius)
    cc = cc + cx - int(radius)
    mask = (rr >= 0) & (rr < shape[0]) & (cc >= 0) & (cc < shape[1])
    return cc[mask], rr[mask]


def photo2circles(img, th1=50, th2=200, counts=(2000, 1200)):
    if isinstance(img, basestring):
        img = cv2.imread(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    edges = cv2.Canny(img, th1, th2)

    edges2 = ~edges
    h, w = img.shape[:2]
    circles = []

    for i in range(counts[0]):
        if i == counts[1]:
            edges2[edges == 255] = 255
        dist = cv2.distanceTransform(edges2, cv.CV_DIST_L2, 3)
        idx = np.argmax(dist)
        cy, cx = np.unravel_index(idx, dist.shape)
        radius = dist[cy, cx]
        x, y = circle(cx, cy, int(radius), (h, w))
        edges2[y, x] = 0
        color = img[y, x].mean(0).astype(np.uint8)
        circles.append([cx, cy, radius] + color.tolist())

    circles = np.array(circles)
    return circles


def main():
    from os import path
    from glob import glob
    FOLDER = path.dirname(__file__)

    for fn in glob(path.join(FOLDER, "*.jpg")):
        csv_fn = fn.replace(".jpg", ".csv")
        if path.exists(csv_fn):
            continue
        print fn
        circles = photo2circles(fn)
        np.savetxt(fn.replace(".jpg", ".csv"), circles, fmt="%g", delimiter=",")


if __name__ == '__main__':
    main()


