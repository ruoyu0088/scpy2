import numpy as np
from mayavi import mlab
from scpy2.tvtk import fix_mayavi_bugs
fix_mayavi_bugs()

x, y, z = np.ogrid[-2:2:40j, -2:2:40j, -2:0:40j]
s = 2/np.sqrt((x-1)**2 + y**2 + z**2) + 1/np.sqrt((x+1)**2 + y**2 + z**2)

surface = mlab.contour3d(s, contours=4, transparent=True)
surface.contour.maximum_contour = 15
surface.contour.number_of_contours = 10
surface.actor.property.opacity = 0.4
mlab.figure()

mlab.pipeline.volume(mlab.pipeline.scalar_field(s))
mlab.figure()

field = mlab.pipeline.scalar_field(s)
mlab.pipeline.volume(field, vmin=1.5, vmax=10)
cut = mlab.pipeline.scalar_cut_plane(field.children[0], plane_orientation="y_axes")
cut.enable_contours = True
cut.contour.number_of_contours = 40
mlab.gcf().scene.background = (0.8, 0.8, 0.8)
mlab.show()
