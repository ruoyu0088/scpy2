from tvtk.tvtkhelp import vtk_convexhull, vtk_scene, ivtk_scene, vtk_scene_to_array
from common import GraphvizDataFrame, GraphvizMatplotlib, GraphvizMPLTransform


def info():
    import sys, platform, re
    from os import path

    print "Welcome to Scpy2"
    print "Python:", platform.python_version()
    print "executable:", path.abspath(sys.executable)

    try:
        patterns = r"numpy.*|scipy.*|sympy.*|pandas.*|opencv.*|ets.*|cython.*|matplotlib.*"
        from winpython import wppm
        dist = wppm.Distribution(sys.prefix)
        for package in dist.get_installed_packages():
            if re.match(patterns, package.name, flags=re.IGNORECASE):
                print "{:20s}: {}".format(package.name, package.version)
    except ImportError:
        pass