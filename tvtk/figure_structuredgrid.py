# -*- coding: utf-8 -*-
from mayavi import mlab
from tvtk.api import tvtk
import numpy as np
   
def plot_cell(cell):
    p = tvtk.PolyData()
    p.points = cell.points
    poly = []
    ids = list(cell.point_ids)
    for i in xrange(cell.number_of_faces):
        poly.append([ids.index(x) for x in cell.get_face(i).point_ids])
    p.polys = poly
    mlab.pipeline.surface(p, opacity = 0.3)

def make_points_array(x, y, z):
    return np.c_[x.ravel(), y.ravel(), z.ravel()]
    
if __name__ == "__main__": 
    z, y, x = np.mgrid[:3.0, :5.0, :4.0]
    x *= (4-z)/3 
    y *= (4-z)/3 
    s1 = tvtk.StructuredGrid()
    s1.points = make_points_array(x, y, z) 
    s1.dimensions = x.shape[::-1] 
    s1.point_data.scalars = np.arange(0, s1.number_of_points)
    s1.point_data.scalars.name = 'scalars'
    
    r, theta, z2 = np.mgrid[2:3:3j, -np.pi/2:np.pi/2:6j, 0:4:7j]
    x2 = np.cos(theta)*r
    y2 = np.sin(theta)*r

    s2 = tvtk.StructuredGrid(dimensions=x2.shape[::-1])
    s2.points = make_points_array(x2, y2, z2)
    s2.point_data.scalars = np.arange(0, s2.number_of_points)
    s2.point_data.scalars.name = 'scalars'

    mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
    mlab.clf()
    mlab.pipeline.surface(mlab.pipeline.extract_edges(s1), color=(0, 0, 0))
    mlab.pipeline.glyph(s1, mode='sphere', scale_factor=0.4, scale_mode='none')
    plot_cell(s1.get_cell(2))
    mlab.text(0.01, 0.9, "get_cell(2)", width=0.25)
    mlab.orientation_axes( )

    mlab.figure(2, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
    mlab.clf()
    mlab.pipeline.surface(mlab.pipeline.extract_edges(s2), color=(0, 0, 0))
    mlab.axes()
    mlab.pipeline.glyph(s2, mode='sphere', scale_factor=0.2, scale_mode='none')
    plot_cell(s2.get_cell(3))
    mlab.text(0.01, 0.9, "get_cell(3)", width=0.25)
    mlab.show()