# Standard Python modules
# =======================
import weakref
from abc import ABCMeta, abstractmethod, abstractproperty

# External modules
# ================
from vtk import vtkActor
from vtk import vtkMapper
from vtk import vtkPolyDataAlgorithm
from vtk import vtkBoundingBox

# DICE modules
# ============
from dice_tools import wizard

class VisObject(metaclass=ABCMeta):

    @abstractmethod
    def attach(self, scene):
        pass

    @abstractmethod
    def detach(self, scene):
        pass

class GeometryProperty(property):

    name = "unnamed_property"

    def __init__(self, fget = None, fset = None):
        property.__init__(self, fget = self.__fget, fset = self.__fset)
        self.__getter = fget
        self.__setter = fset

    def __fget(self, obj):
        return self.__getter(obj)

    def __fset(self, obj, value):
        self.__setter(obj, value)
        wizard.w_property_changed(obj,
            name = self.name, value = value)

    def __call__(self, fget):
        return self.getter(fget)

    def getter(self, fget):
        self.__getter = fget
        return self

    def setter(self, fset):
        self.__setter = fset
        return self

class GeometryBaseMeta(ABCMeta):
    def __new__(cls, classname, bases, classDict):
        for name, attr in classDict.items():
            if isinstance(attr, GeometryProperty):
                attr.name = name
        return super().__new__(cls, classname, bases, classDict)

class GeometryBase(VisObject, metaclass=GeometryBaseMeta):
    selection = weakref.WeakSet()

    def __init__(self, name='UnnamedGeometry', **kwargs):
        super().__init__(**kwargs)
        self.__name = name
        self.__selected = False
        self.__saved_color = None

    @GeometryProperty
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @abstractmethod
    def get_bounds(self, scene):
        pass

    @abstractmethod   
    def get_sources(self):
        pass

    def get_mappers(self):
        return [v.GetMapper() for v in self.get_actors()]

    @abstractmethod   
    def get_actors(self):
        pass

    @property
    def selected(self):
        return self.__selected

    @property
    def saved_color(self):
        return self.__saved_color

    @saved_color.setter
    def saved_color(self, value):
        self.__saved_color = value

    @GeometryProperty
    def color(self):
        if self.__saved_color != None:
            return self.__saved_color
        return self.get_color()

    @color.setter
    def color(self, value):
        if self.selected:
            self.saved_color = value
        else:
            self.set_color(value)

    @abstractmethod
    def get_color(self):
        pass

    @abstractmethod
    def set_color(self, value):
        pass

    @abstractproperty
    def visible(self):
        pass

    @visible.setter
    def visible(self, value):
        pass

    @abstractproperty
    def opacity(self):
        pass

    @opacity.setter
    def opacity(self, value):
        pass

    @abstractproperty
    def representation(self):
        pass

    @representation.setter
    def representation(self, value):
        pass

    @abstractproperty
    def edge_visible(self):
        pass

    @edge_visible.setter
    def edge_visible(self, value):
        pass

    @abstractproperty
    def position(self):
        pass

    @position.setter
    def position(self, value):
        pass

    @classmethod
    def w_geometry_objects_select(cls, objects, enable, clear):
        if clear and cls.selection:
            for o in objects:
                cls.selection.discard(o)
            for o in cls.selection:
                o.set_selected(False)

        for o in objects:
            if enable:
                cls.selection.add(o)
                o.set_selected(True)
            else:
                cls.selection.discard(o)
                o.set_selected(False)

    def set_selected(self, enable):
        if enable and not self.__selected:
            color = getattr(self, 'color', None)
            if color != None:
                self.__saved_color = color
                self.set_color([0.9, 0, 0])
            self.__selected = True
            wizard.w_geometry_object_selection_state(self, True)
        elif not enable and self.__selected:
            self.__selected = False
            color = getattr(self, 'color', None)
            if color != None:
                self.set_color(self.__saved_color)
                self.__saved_color = None
            wizard.w_geometry_object_selection_state(self, False)

wizard.subscribe(GeometryBase, 'w_geometry_objects_select')
