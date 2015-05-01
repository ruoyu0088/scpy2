# -*- coding: utf-8 -*-
"""
显示TVTK的类的继承树以及文档，支持简单的搜索功能。
"""
import cPickle, os.path, gzip
from traits.api import (HasTraits, Instance, Any, List, Str,
    Property, Code, Int, cached_property, Bool)
from traitsui.api import (View, Item, TreeEditor, HSplit, Group, VSplit,
    TreeNodeObject, ObjectTreeNode, CodeEditor, ListStrEditor, Handler)


CACHE_FILE = "tvtk_classes.cache"

# 忽略HasTraits中定义的所有方法
ignore_names = set(dir(HasTraits))    

def get_tvtk_class_doc(cls):
    """获得cls类的文档，包括trait属性和方法的文档"""
    def append_title(title, level=0):
        c = "=+-"
        if len(doc)>0: doc.append("")
        doc.append(title)
        doc.append(c[level] * len(title))
        doc.append("")
    doc = []
    append_title(cls.__name__)
    doc.append( cls.__doc__ )

    append_title("Traits")
    
    trait_names = cls.__class_traits__.keys()
    trait_names.sort()
    
    for name in trait_names:
        if name in ignore_names: continue
        help = cls.__class_traits__[name].help
        if help:
            doc.append("%s: %s" % (name, help))
        
    append_title("Methods")
    names = dir(cls)
    names.sort()
    for name in names:
        if name.startswith("_") or name in ignore_names: continue
        func = getattr(cls, name)
        if callable(func):
            append_title(name, level=1)
            doc.append( get_func_doc(func, name) )
    return "\n".join(doc)

SubClasses = {}    
if not os.path.exists(CACHE_FILE):
    from tvtk.api import tvtk
    from tvtk.tools.tvtk_doc import get_func_doc
    # 遍历所有TVTK类，建立类之间的继承关系
    print "reading TVTK classes"
    for tmp in dir(tvtk):
        cls = getattr(tvtk, tmp)
    

    for tmp in dir(tvtk):
        cls = getattr(tvtk, tmp)
        try:
            subclass = cls.__subclasses__()
            SubClasses[tmp] = dict(
                subclass=[t.__name__ for t in subclass], 
                doc=get_tvtk_class_doc(cls))
        except:
            continue
            
    print "saving cache"
    f = gzip.GzipFile(CACHE_FILE, "wb")
    cPickle.dump(SubClasses, f)
    f.close()
    print "done"
else:
    print "reading cache"
    f = gzip.GzipFile(CACHE_FILE, "rb")
    SubClasses = cPickle.load(f)
    f.close()
    print "done"


class TVTKClass(TreeNodeObject):
    children = List()
    name = Str("node")
    doc = Code   
    unicode_doc = Property()
    Classes = {}
    
    def __init__(self, **traits):
        super(TVTKClass, self).__init__(**traits)
        TVTKClass.Classes[self.name] = self
    
    def _get_children(self):
        try:
            subclass_names = SubClasses[self.name]["subclass"]
            subclass_names.sort()
            return [TVTKClass(name=t) for t in subclass_names]
        except:
            return []
    
    def _name_changed(self):
        #self.doc = get_tvtk_class_doc(getattr(tvtk, self.name))
        self.doc = SubClasses[self.name]["doc"]
        self.children = self._get_children()
        
    def tno_get_children(self, node):
        return self.children
        
    def _get_unicode_doc(self):
        return self.doc.decode("utf8", "ignore")
        
        
class TVTKDocumentHandler(Handler):
    def close(self, info, is_ok):
        super(TVTKDocumentHandler, self).close(info, is_ok)
        # 在销毁窗口之前隐藏树控件，提高窗口的关闭速度
        info.object.show_tree = False
        return True
    
class TVTKDocument(HasTraits):
    tree_editor = Instance(TreeEditor)
    nodes = Any
    search = Str
    search_result = List(Instance(TVTKClass))
    search_result_str = Property(depends_on = "search_result")
    search_result_index = Int
    object_class = Instance(TVTKClass)
    tree_selected = Instance(TVTKClass)
    mark_lines = List(Int)
    current_line = Int
    current_document = Str
    show_tree = Bool(True)
    
    def default_traits_view(self):
        view = View(
            HSplit(
                VSplit(
                    Item("object_class", editor=self.tree_editor, show_label=False, 
                        visible_when="object.show_tree"),
                    Group(
                        Item("search", label=u"搜索"),
                        Item("search_result_str", show_label=False,
                            editor=ListStrEditor(editable=False, selected_index="search_result_index")),
                        label="Search"),
                ),
                Item("current_document", style="custom", show_label=False,
                    editor=CodeEditor(lexer="text", search="top", line = "current_line",
                        mark_lines="mark_lines", mark_color=0xff7777)),
                id = "tvtkdoc.hsplit"
            ),
            width = 700,
            height = 500,
            resizable = True,
            title = u"TVTK文档浏览器",
            id = "tvtkdoc", 
            handler = TVTKDocumentHandler(),
        )
        return view
        
    @cached_property
    def _get_search_result_str(self):
        return [obj.name for obj in self.search_result]
        
    def _search_changed(self):
        if len(self.search)<3: return
        result = []
        for cls in TVTKClass.Classes.values():
            if self.search.islower():
                if self.search in cls.unicode_doc.lower():
                    result.append(cls)
            else:
                if self.search in cls.unicode_doc:
                    result.append(cls)
                    
        result.sort(key=lambda obj:obj.name)
        self.search_result = result
        
    def _search_result_index_changed(self):
        if self.search_result_index>=0:
            self.tree_selected = self.search_result[self.search_result_index]
        
    def _object_class_default(self):
        obj = TVTKClass(name="Object")
        self.tree_selected = obj.children[0]
        return obj
       
    def _tree_editor_default(self):
        return TreeEditor(
            editable = False,
            hide_root = True,
            nodes = self.nodes,
            selected = "tree_selected"
        )
            
    def _nodes_default(self):
        nodes = [
            ObjectTreeNode(
                node_for = [TVTKClass],
                children = "children",
                label = "name",
                auto_open = True,
                copy = True,
                delete = True,
                rename = True,                
            )
        ]
        return nodes
        
    def _tree_selected_changed(self):
        self.current_document = self.tree_selected.doc
        if len(self.search) < 3:
            self.mark_lines = []
            self.current_line = 1
            return
        doc = self.tree_selected.doc
        if self.search.islower():
            doc = doc.lower()
        lines = doc.split("\n")
        result = []
        for i, line in enumerate(lines):
            if self.search in line:
                result.append(i+1)
        self.mark_lines = result
        if len(result) > 0:
            self.current_line = result[0]
        else:
            self.current_line = 1
            
d = TVTKDocument()    
d.configure_traits()