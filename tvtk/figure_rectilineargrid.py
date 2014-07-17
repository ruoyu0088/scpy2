# -*- coding: utf-8 -*-
from mayavi import mlab
from figure_imagedata import plot_cell

if __name__ == "__main__":
    from tvtk.api import tvtk
    import numpy as np
    
    x = np.array([0,3,9,15])
    y = np.array([0,1,5])
    z = np.array([0,2,3])
    r = tvtk.RectilinearGrid()
    r.x_coordinates = x 
    r.y_coordinates = y
    r.z_coordinates = z
    r.dimensions = len(x), len(y), len(z) 
    
    r.point_data.scalars = np.arange(0.0,r.number_of_points)
    r.point_data.scalars.name = 'scalars'

    mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
    mlab.clf()
    mlab.pipeline.surface(mlab.pipeline.extract_edges(r), color=(0, 0, 0))
    mlab.pipeline.glyph(r, mode='sphere', scale_factor=0.5, scale_mode='none')
    plot_cell(r.get_cell(1))
    mlab.text(0.01, 0.9, "get_cell(1)", width=0.25)
    axes = mlab.orientation_axes( )
    mlab.show()