# -*- coding: utf-8 -*-
"""
对图像进行浮雕处理
"""
import pylab as pl
import scipy as sp
import numpy as np

t = np.arange(1e-6, 20, 0.01)
y = np.sin(t) / t

img = sp.misc.lena()
pl.imshow(img, cmap=pl.cm.gray)
img2 = img[:-2,1:-1]-img[2:,1:-1]+img[1:-1, :-2]-img[1:-1,2:]
pl.figure()
pl.imshow(img2, cmap=pl.cm.gray)
pl.show()