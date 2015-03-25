# -*- coding: utf-8 -*-
"""
使用Mayavi绘制多为数组下标存取的演示图像。
"""
import numpy as np
from mayavi import mlab

x, y, z = np.mgrid[:6,:7,:8]
c = np.zeros((6, 7, 8), dtype=np.int)
c.fill(1)
k = np.random.randint(2,5,size=(6, 7))

idx_i, idx_j, _ = np.ogrid[:6, :7, :8]
idx_k = k[:,:, np.newaxis] + np.arange(3)
c[idx_i, idx_j, idx_k] = np.random.randint(2,6, size=(6,7,3))

mlab.points3d(x[c>1], y[c>1], z[c>1], c[c>1], mode="cube", scale_factor=0.8, 
    scale_mode="none", transparent=True, vmin=0, vmax=8, colormap="Greys")

mlab.points3d(x[c==1], y[c==1], z[c==1], c[c==1], mode="cube", scale_factor=0.8,
    scale_mode="none", transparent=True, vmin=0, vmax=8, colormap="Greys", opacity = 0.2)
mlab.gcf().scene.background = (1,1,1)

mlab.figure()
x, y, z = np.mgrid[:6,:7,:3]
mlab.points3d(x, y, z, c[idx_i, idx_j, idx_k], mode="cube", scale_factor=0.8, 
    scale_mode="none", transparent=True, vmin=0, vmax=8, colormap="Greys", opacity = 1)
mlab.gcf().scene.background = (1,1,1)
mlab.show()