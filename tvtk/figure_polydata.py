# -*- coding: utf-8 -*-
from mayavi import mlab
   
if __name__ == "__main__":  

    from tvtk.api import tvtk
    import numpy as np

    p1 = tvtk.PolyData()
    p1.points = [(1,1,0),(1,-1,0),(-1,-1,0),(-1,1,0),(0,0,2)] 
    faces = [ 
        4,0,1,2,3,
        3,4,0,1,
        3,4,1,2,
        3,4,2,3,
        3,4,3,0
        ]
    cells = tvtk.CellArray() 
    cells.set_cells(5, faces) 
    p1.polys = cells
    p1.point_data.scalars = np.linspace(0.0, 1.0, len(p1.points))
    
    N = 10
    a, b = np.mgrid[0:np.pi:N*1j, 0:np.pi:N*1j]
    x = np.sin(a)*np.cos(b)
    y = np.sin(a)*np.sin(b)
    z = np.cos(a)

    from figure_structuredgrid import make_points_array
    points = make_points_array(x, y, z) 
    faces = np.zeros(((N-1)**2, 4), np.int) 
    t1, t2 = np.mgrid[:(N-1)*N:N, :N-1]
    faces[:,0] = (t1+t2).ravel()
    faces[:,1] = faces[:,0] + 1
    faces[:,2] = faces[:,1] + N
    faces[:,3] = faces[:,0] + N

    p2 = tvtk.PolyData(points = points, polys = faces)
    p2.point_data.scalars = np.linspace(0.0, 1.0, len(p2.points))
  
    mlab.figure(1, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
    mlab.pipeline.surface(p1)
    mlab.pipeline.glyph(p1, mode='sphere', scale_factor=0.4, scale_mode='none')

    mlab.figure(2, fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))
    mlab.pipeline.surface(p2, representation='wireframe')
    mlab.pipeline.glyph(p2, mode='sphere', scale_factor=0.08, scale_mode='none')
    mlab.show()    