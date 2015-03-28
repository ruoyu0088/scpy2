# -*- coding: utf-8 -*-
"""
演示TraitsUI的各种编辑器
"""

import os
from datetime import time
from traits.api import *
from traitsui.api import *


class Employee(HasTraits):
    name = Unicode(label=u"姓名") 
    department = Unicode(label=u"部门")
    salary = Int(label=u"薪水")
    bonus = Int(label=u"奖金")
    view = View("name", "department", "salary", "bonus") 


###1###
class EditorDemoItem(HasTraits):
    code = Code()
    view = View(
        Group(
            Item("item", style="simple", label="simple", width=-300), #❶
            "_",  #❷
            Item("item", style="custom", label="custom"),
            "_",
            Item("item", style="text", label="text"),
            "_",
            Item("item", style="readonly", label="readonly"),
        ),
    )
###1###

###2###
class EditorDemo(HasTraits):
    codes = List(Str)
    selected_item = Instance(EditorDemoItem)  
    selected_code = Str #❶
    view = View(
        HSplit(
            Item("codes", style="custom", show_label=False,
                editor=ListStrEditor(editable=False, selected="selected_code")), #❶
            Item("selected_item", style="custom", show_label=False),
        ),
        resizable=True,
        width = 800,
        height = 400,
        title=u"各种编辑器演示"
    )

    def _selected_code_changed(self):
        item = EditorDemoItem(code=self.selected_code)
        item.add_trait("item", eval(self.selected_code)) #❷
        self.selected_item = item
###2###

###3###
employee = Employee()
demo_list = [u"低通", u"高通", u"带通", u"带阻"]

trait_defines ="""
    Array(dtype="int32", shape=(3,3)) #{1}
    Bool(True)
    Button("Click me")
    List(editor=CheckListEditor(values=demo_list))
    Code("print 'hello world'")
    Color("red")
    RGBColor("red")
    Trait(*demo_list)
    Directory(os.getcwd())
    Enum(*demo_list)
    File()
    Font()
    HTML('<b><font color="red" size="40">hello world</font></b>')
    List(Str, demo_list)
    Range(1, 10, 5)
    List(editor=SetEditor(values=demo_list))
    List(demo_list, editor=ListStrEditor())
    Str("hello")
    Password("hello")
    Str("Hello", editor=TitleEditor())
    Tuple(Color("red"), Range(1,4), Str("hello"))
    Instance(EditorDemoItem, employee)    
    Instance(EditorDemoItem, employee, editor=ValueEditor())
    Instance(time, time(), editor=TimeEditor())
"""
demo = EditorDemo()
demo.codes = [s.split("#")[0].strip() for s in trait_defines.split("\n") if s.strip()!=""]
demo.configure_traits()
###3###