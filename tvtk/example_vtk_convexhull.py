import numpy as np
from scipy import spatial
from .tvtkhelp import vtk_convexhull, ivtk_scene, event_loop, vtk_scene, vtk_scene_to_array

np.random.seed(42)
points3d = np.random.rand(40, 3)
ch3d = spatial.ConvexHull(points3d)


actors = vtk_convexhull(ch3d)
scene = vtk_scene(actors, viewangle=22)
vtk_scene_to_array(scene)

#win = ivtk_scene(actors)
#win.scene.isometric_view()
#win.scene.save_png("test.png")
#event_loop()