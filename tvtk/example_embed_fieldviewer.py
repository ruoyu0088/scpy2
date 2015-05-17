#ecoding=utf8
###1###
import numpy as np

from traits.api import HasTraits, Float, Int, Bool, Range, Str, Button, Instance
from traitsui.api import View, HSplit, Item, VGroup, EnumEditor, RangeEditor
from tvtk.pyface.scene_editor import SceneEditor 
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi.core.ui.mayavi_scene import MayaviScene
from scpy2.tvtk import fix_mayavi_bugs

fix_mayavi_bugs()


class FieldViewer(HasTraits):
    
    # 三个轴的取值范围
    x0, x1 = Float(-5), Float(5)
    y0, y1 = Float(-5), Float(5)
    z0, z1 = Float(-5), Float(5)
    points = Int(50) # 分割点数
    autocontour = Bool(True) # 是否自动计算等值面
    v0, v1 = Float(0.0), Float(1.0) # 等值面的取值范围
    contour = Range("v0", "v1", 0.5) # 等值面的值
    function = Str("x*x*0.5 + y*y + z*z*2.0") # 标量场函数
    function_list = [
        "x*x*0.5 + y*y + z*z*2.0",
        "x*y*0.5 + np.sin(2*x)*y +y*z*2.0",
        "x*y*z",
        "np.sin((x*x+y*y)/z)"
    ]
    plotbutton = Button(u"描画")
    scene = Instance(MlabSceneModel, ()) #❶
    
    view = View(
        HSplit(
            VGroup(
                "x0","x1","y0","y1","z0","z1",
                Item('points', label=u"点数"),
                Item('autocontour', label=u"自动等值"),
                Item('plotbutton', show_label=False),
            ),
            VGroup(
                Item('scene', 
                    editor=SceneEditor(scene_class=MayaviScene), #❷
                    resizable=True,
                    height=300,
                    width=350
                ), 
                Item('function', 
                    editor=EnumEditor(name='function_list', evaluate=lambda x:x)),
                Item('contour', 
                    editor=RangeEditor(format="%1.2f",
                        low_name="v0", high_name="v1")
                ), show_labels=False
            )
        ),
        width = 500, resizable=True, title=u"三维标量场观察器"
    )
      
    def _plotbutton_fired(self):
        self.plot()

    def plot(self):
        # 产生三维网格
        x, y, z = np.mgrid[ #❸
            self.x0:self.x1:1j*self.points, 
            self.y0:self.y1:1j*self.points, 
            self.z0:self.z1:1j*self.points]
            
        # 根据函数计算标量场的值
        scalars = eval(self.function)  #❹
        self.scene.mlab.clf() # 清空当前场景
        
        # 绘制等值平面
        g = self.scene.mlab.contour3d(x, y, z, scalars, contours=8, transparent=True) #❺
        g.contour.auto_contours = self.autocontour
        self.scene.mlab.axes(figure=self.scene.mayavi_scene) # 添加坐标轴

        # 添加一个X-Y的切面
        s = self.scene.mlab.pipeline.scalar_cut_plane(g)
        cutpoint = (self.x0+self.x1)/2, (self.y0+self.y1)/2, (self.z0+self.z1)/2
        s.implicit_plane.normal = (0,0,1) # x cut
        s.implicit_plane.origin = cutpoint
        
        self.g = g #❻
        self.scalars = scalars
        # 计算标量场的值的范围
        self.v0 = np.min(scalars)
        self.v1 = np.max(scalars)
        
    def _contour_changed(self): #❼
        if hasattr(self, "g"):
            if not self.g.contour.auto_contours:
                self.g.contour.contours = [self.contour]
                
    def _autocontour_changed(self): #❽
        if hasattr(self, "g"):
            self.g.contour.auto_contours = self.autocontour
            if not self.autocontour:
                self._contour_changed()


if __name__ == '__main__':
    app = FieldViewer()
    app.configure_traits()
###1###