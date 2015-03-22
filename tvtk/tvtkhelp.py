# -*- coding: utf-8 -*-


def make_outline(input_obj):
    from tvtk.api import tvtk
    from tvtk.common import configure_input
    outline = tvtk.StructuredGridOutlineFilter()
    configure_input(outline, input_obj)
    outline_mapper = tvtk.PolyDataMapper(input_connection = outline.output_port)
    outline_actor = tvtk.Actor(mapper = outline_mapper)
    outline_actor.property.color = 0.3, 0.3, 0.3
    return outline_actor


def depth_peeling(scene):
    rw = scene.render_window
    renderer = scene.renderer
    rw.alpha_bit_planes = 1
    rw.multi_samples = 0
    renderer.use_depth_peeling = 1
    renderer.maximum_number_of_peels = 100
    renderer.occlusion_ratio = 0.1


def vtk_scene_to_array(scene, close=True):
    import numpy as np
    from tvtk.api import tvtk

    w2if = tvtk.WindowToImageFilter(read_front_buffer=True)
    w2if.magnification = scene.magnification
    scene._lift()
    w2if.input = scene._renwin
    w2if.update()
    imgdata = w2if.output
    w, h, _ = imgdata.dimensions
    #print w, h
    #print imgdata.point_data
    #print imgdata.point_data.scalars
    #print imgdata.point_data.scalars.to_array()
    arr = imgdata.point_data.scalars.to_array()
    arr.shape = h, w, -1
    arr = arr[::-1].copy()
    mask = np.all(arr == arr[0, 0], -1)
    x0, x1 = np.where(~np.all(mask, axis=0))[0][[0, -1]]
    y0, y1 = np.where(~np.all(mask, axis=1))[0][[0, -1]]
    if close:
        scene.close()
    return arr[y0:y1 + 1, x0:x1 + 1, :].copy()


def vtk_convexhull(ch, radius=0.02):
    from tvtk.api import tvtk

    poly = tvtk.PolyData()
    poly.points = ch.points
    poly.polys = ch.simplices

    sphere = tvtk.SphereSource(radius=radius)
    points3d = tvtk.Glyph3D()
    points3d.set_source_connection(sphere.output_port)
    points3d.set_input_data(poly)

    m1 = tvtk.PolyDataMapper()
    m1.set_input_data(poly)
    a1 = tvtk.Actor(mapper=m1)
    a1.property.opacity = 0.3

    m2 = tvtk.PolyDataMapper()
    m2.set_input_data(poly)
    a2 = tvtk.Actor(mapper=m2)
    a2.property.representation = "wireframe"
    a2.property.line_width = 2.0
    a2.property.color = (1.0, 0, 0)

    m3 = tvtk.PolyDataMapper(input_connection=points3d.output_port)
    a3 = tvtk.Actor(mapper=m3)
    a3.property.color = (0.0, 1.0, 0.0)
    return [a1, a2, a3]


def vtk_scene(actors, size=(800, 600), azimuth=None, elevation=None, viewangle=None):
    from tvtk.pyface.tvtk_scene import TVTKScene

    scene = TVTKScene(off_screen_rendering=False)
    scene._renwin.size = size
    scene.add_actors(actors)
    if azimuth is not None:
        scene.camera.azimuth(azimuth)
    if elevation is not None:
        scene.camera.elevation(elevation)
    if viewangle is not None:
        scene.camera.view_angle = viewangle
    depth_peeling(scene)
    return scene


def ivtk_scene(actors):
    from .tvtk_brower_patch import patch_pipeline_browser
    from tvtk.tools import ivtk

    patch_pipeline_browser()
    window = ivtk.IVTKWithCrustAndBrowser(size=(800, 600))
    window.open()
    depth_peeling(window.scene)
    window.scene.add_actors(actors)
    window.scene.background = 1, 1, 1
    # fix problem when run in IPython
    dialog = window.control.centralWidget().widget(0).widget(0)
    from pyface.qt import QtCore

    dialog.setWindowFlags(QtCore.Qt.WindowFlags(0x00000000))
    dialog.show()

    return window


def event_loop():
    from pyface.api import GUI
    gui = GUI()
    gui.start_event_loop()
