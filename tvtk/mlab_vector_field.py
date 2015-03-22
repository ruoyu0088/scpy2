# -*- coding: utf-8 -*-
import os
import numpy as np
from mayavi import mlab
from scpy2.tvtk import fix_mayavi_bugs

fix_mayavi_bugs()

p, r, b = (10.0, 28.0, 3.0)
x, y, z = np.mgrid[-17:20:20j, -21:28:20j, 0:48:20j]
u, v, w = p*(y-x), x*(r-z)-y, x*y-b*z

mlab.figure(size=(600, 600))

mlab.quiver3d(x, y, z, u, v, w)

mlab.figure(size=(600, 600))
vectors = mlab.quiver3d(x, y, z, u, v, w)
vectors.glyph.mask_input_points = True
vectors.glyph.mask_points.on_ratio = 20
vectors.glyph.glyph.scale_factor = 5.0

mlab.figure(size=(600, 600))
src = mlab.pipeline.vector_field(x, y, z, u, v, w)
mlab.pipeline.vector_cut_plane(src, mask_points=2, scale_factor=5)

magnitude = mlab.pipeline.extract_vector_norm(src)
surface = mlab.pipeline.iso_surface(magnitude)
surface.actor.property.opacity = 0.3
mlab.gcf().scene.background = (0.8, 0.8, 0.8)

mlab.figure(size=(600, 600))
mlab.flow(x, y, z, u, v, w)

mlab.show()
