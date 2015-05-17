#ecoding=utf8
###1###
from traits.api import HasTraits, Instance, Range, on_trait_change
from traitsui.api import View, Item, VGroup, HGroup, Controller
from tvtk.api import tvtk
from tvtk.pyface.scene_editor import SceneEditor
from tvtk.pyface.scene import Scene
from tvtk.pyface.scene_model import SceneModel


class TVTKSceneController(Controller):
    def position(self, info):
        super(TVTKSceneController, self).position(info)
        self.model.plot() #❸


class TubeDemoApp(HasTraits):
    radius1 = Range(0, 1.0, 0.8)
    radius2 = Range(0, 1.0, 0.4)
    scene = Instance(SceneModel, ()) #❶
    view = View(
                VGroup(
                    Item(name="scene", editor=SceneEditor(scene_class=Scene)), #❷
                    HGroup("radius1", "radius2"),
                    show_labels=False),
                resizable=True, height=500, width=500)
        
    def plot(self):
        r1, r2 = min(self.radius1, self.radius2), max(self.radius1, self.radius2)
        self.cs1 = cs1 = tvtk.CylinderSource(height=1, radius=r2, resolution=32)
        self.cs2 = cs2 = tvtk.CylinderSource(height=1.1, radius=r1, resolution=32)
        triangle1 = tvtk.TriangleFilter(input_connection=cs1.output_port)
        triangle2 = tvtk.TriangleFilter(input_connection=cs2.output_port)
        bf = tvtk.BooleanOperationPolyDataFilter()
        bf.operation = "difference"
        bf.set_input_connection(0, triangle1.output_port)
        bf.set_input_connection(1, triangle2.output_port)
        m = tvtk.PolyDataMapper(input_connection=bf.output_port, scalar_visibility=False)
        a = tvtk.Actor(mapper=m)
        a.property.color = 0.5, 0.5, 0.5
        self.scene.add_actors([a])
        self.scene.background = 1, 1, 1
        self.scene.reset_zoom()
    
    @on_trait_change("radius1, radius2") #❹
    def update_radius(self):
        self.cs1.radius = max(self.radius1, self.radius2)
        self.cs2.radius = min(self.radius1, self.radius2)
        self.scene.render_window.render()        


if __name__ == "__main__":
    app = TubeDemoApp()
    app.configure_traits(handler=TVTKSceneController(app))
###1###