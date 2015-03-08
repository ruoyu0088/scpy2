from tvtk.api import tvtk

r1 = 0.5
r2 = 0.9

cs1 = tvtk.CylinderSource(height=1, radius=r2, resolution=32)
cs2 = tvtk.CylinderSource(height=1.1, radius=r1, resolution=32)
triangle1 = tvtk.TriangleFilter(input_connection=cs1.output_port)
triangle2 = tvtk.TriangleFilter(input_connection=cs2.output_port)
bf = tvtk.BooleanOperationPolyDataFilter()
bf.operation = "difference"
bf.set_input_connection(0, triangle1.output_port)
bf.set_input_connection(1, triangle2.output_port)
m = tvtk.PolyDataMapper(input_connection=bf.output_port, scalar_visibility=False)
a = tvtk.Actor(mapper=m)
a.property.color = 0.5, 0.5, 0.5

from scpy2.tvtk.tvtkhelp import ivtk_scene, event_loop

scene = ivtk_scene([a])
event_loop()