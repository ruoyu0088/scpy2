import re
from tvtk.pipeline.browser import SimpleTreeGenerator
from tvtk.api import tvtk
from tvtk.tvtk_base import TVTKBase
from tvtk.common import camel2enthought

icon_map = {'actor': 'actor.png',
            'camera': 'camera.png',
            'coordinate': 'coordinate.png',
            'filter': 'filter.png',
            'lookuptable': 'lookuptable.png',
            'mapper': 'mapper.png',
            'polydata': 'polydata.png',
            'property': 'property.png',
            'reader': 'reader.png',
            'renderer': 'renderer.png',
            'rendererwindowinteractor': 'rendererwindowinteractor.png',
            'source': 'source.png',
            'texture': 'texture.png',
            'window': 'window.png',
            'writer': 'writer.png',
            'grid': 'source.png',
            }


def get_icon(object_name):
    """Given the name of the object, this function returns an
    appropriate icon image name.  If no icon is appropriate it returns
    the empty string."""

    # Lower case the name.
    name = object_name.lower()

    for key in icon_map:
        if name.endswith(key):
            return icon_map[key]

    # No valid icon for this object.
    return ''


######################################################################
# `FullTreeGenerator` class.
######################################################################
class FullTreeGenerator(SimpleTreeGenerator):
    """This particular class picks up a lot more children in the
    pipeline and is similar to the code used in MayaVi-1.x's pipeline
    browser."""

    def __init__(self, **traits):
        super(FullTreeGenerator, self).__init__(**traits)
        self.last_transform = 0

    def get_children(self, obj):
        """Returns the child objects of a particular tvtk object in a
        dictionary, the keys are the trait names.  This is used to
        generate the tree in the browser."""

        vtk_obj = tvtk.to_vtk(obj)
        methods = self._get_methods(vtk_obj)

        kids = {}
        def _add_kid(key, x):
            if x is None:
                kids[key] = None
            else:
                if type(x) in (type([]), type(())):
                    x1 = [i for i in x if isinstance(i, TVTKBase)]
                    if x1:
                        kids[key] = x1
                elif isinstance(x, TVTKBase):
                    if hasattr(x, '__iter__'):
                        # Don't add iterable objects that contain non
                        # acceptable nodes
                        if len(list(x)) and isinstance(list(x)[0], TVTKBase):
                            kids[key] = x
                    else:
                        kids[key] = x

        for method in methods:
            attr = camel2enthought(method[0])
            if hasattr(obj, attr):
                _add_kid(attr, getattr(obj, attr))

        if hasattr(obj, 'number_of_input_ports'):
            count = obj.number_of_input_ports
            inputs = []
            for i in range(count):
                for j in range(obj.get_number_of_input_connections(i)):
                    producer = obj.get_input_connection(i, j).producer
                    if isinstance(producer, tvtk.TrivialProducer):
                        producer = obj.get_input_data_object(i, j)
                    inputs.append(producer)
            _add_kid('input', inputs)

        return kids

    def has_children(self, obj):
        """Returns true of the object has children, false if not.  This is
        very specific to tvtk objects."""
        if isinstance(obj, (tvtk.RenderWindow, tvtk.Renderer,
                            tvtk.Collection)):
            return True
        for attribute in ['number_of_input_ports', 'source', 'input_connection',
                          'get_input', 'input', 'mapper',
                          'property', 'texture', 'text_property', 'volume_property',
                          'lookup_table', 'producer_port', 'producer']:
            if hasattr(obj, attribute):
                return True
        # FIXME: This is inefficient.  We probably should cache the
        # get_children call.
        if self.get_children(obj):
            return True
        return False

    ###########################################################################
    # Non-public interface.
    ###########################################################################
    def _get_methods(self, vtk_obj):
        """Obtain the various methods from the passed object."""

        def _remove_method(name, methods, method_names):
            """Removes methods if they have a particular name."""
            try:
                idx = method_names.index(name)
            except ValueError:
                pass
            else:
                del methods[idx], method_names[idx]
            return methods, method_names

        # The following code basically gets the 'str' representation
        # of the VTK object and parses it to obtain information about
        # the object's children.  It is a hack but has worked well for
        # a *very* long time with MayaVi-1.x and before.

        # Oops, this isn't a VTK object.
        if not hasattr(vtk_obj, 'GetClassName'):
            return []

        methods = str(vtk_obj)
        methods = methods.split("\n")
        del methods[0]

        # using only the first set of indented values.
        patn = re.compile("  \S")
        for method in methods[:]:
            if patn.match(method):
                if method.find(":") == -1:
                    methods.remove(method)
                elif method[1].find("none") > -1:
                    methods.remove(method)
            else:
                methods.remove(method)

        # Props/Prop is deprecated in more recent VTK releases.
        for method in methods[:]:
            if method.strip()[:6] == "Props:":
                if hasattr(vtk_obj, "GetViewProps"):
                    methods.remove(method)
                    methods.append("ViewProps: ")
            elif method.strip()[:5] == "Prop:":
                if hasattr(vtk_obj, "GetViewProp"):
                    methods.remove(method)
                    methods.append("ViewProp: ")

        method_names = []
        for i in range(0, len(methods)):
            strng = methods[i].replace(" ", "")
            methods[i] = strng.split(":")
            method_names.append(methods[i][0])

        if re.match("vtk\w*Renderer", vtk_obj.GetClassName()):
            methods.append(["ActiveCamera", ""])

        if re.match("vtk\w*Assembly", vtk_obj.GetClassName()):
            methods.append(["Parts", ""])
            methods.append(["Volumes", ""])
            methods.append(["Actors", ""])

        if vtk_obj.IsA('vtkAbstractTransform'):
            if self.last_transform > 0:
                _remove_method('Inverse', methods, method_names)
            else:
                self.last_transform += 1
        else:
            self.last_transform = 0

        # Some of these object are removed because they arent useful in
        # the browser.  I check for Source and Input anyway so I dont need
        # them.
        for name in('Output', 'FieldData', 'CellData', 'PointData',
                    'Source', 'Input', 'ExtentTranslator',
                    'Interactor', 'Lights', 'Information', 'Executive'):
            _remove_method(name, methods, method_names)

        return methods


def patch_pipeline_browser():
    from tvtk.pipeline import browser
    browser.get_icon = get_icon
    for method in ("get_children", "has_children"):
        setattr(browser.FullTreeGenerator, method, FullTreeGenerator.__dict__[method])