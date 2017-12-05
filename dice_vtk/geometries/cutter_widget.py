# # External modules
# # ================
# from vtk import vtkPolyDataMapper, \
#     vtkActor, \
#     vtkPlane, \
#     vtkFeatureEdges, \
#     vtkCutter, \
#     vtkStripper, \
#     vtkPolyData

# # DICE modules
# # ============
# from .geometry_base import VisObject

# class Cutter(VisObject):

#     def __init__(self, obj, **kwargs):
#         super().__init__(**kwargs)
#         # print("-=-=-=-=-app_plugin Cutter-=-=-=-=-")

#         self.obj = obj
#         self.source = vtkCutter()
#         self.mapper = vtkPolyDataMapper()
#         self.actor = vtkActor()
#         self.plane = vtkPlane()

#         # plane.SetOrigin(1, 0.5, 0)
#         self.plane.SetNormal(1, 0.5, 0.25)

#         self.source.SetCutFunction(self.plane)
#         self.source.SetInputConnection(self.obj.source.GetOutputPort())
#         self.source.Update()

#         self.cut_strips = vtkStripper()  # Forms loops (closed polylines) from cutter
#         self.cut_strips.SetInputConnection(self.source.GetOutputPort())
#         self.cut_strips.Update()

#         self.cut_poly = vtkPolyData()  # This trick defines polygons as polyline loop
#         self.cut_poly.SetPoints((self.cut_strips.GetOutput()).GetPoints())
#         self.cut_poly.SetPolys((self.cut_strips.GetOutput()).GetLines())

#         self.mapper.SetInputData(self.cut_poly)
#         # cutter_mapper.SetInputData(FeatureEdges.GetOutput())

#         self.actor.GetProperty().SetColor(1, 0, 1)
#         self.actor.GetProperty().SetEdgeColor(0, 1, 0)
#         self.actor.GetProperty().SetLineWidth(2)
#         self.actor.GetProperty().EdgeVisibilityOn()
#         self.actor.GetProperty().SetOpacity(0.7)
#         self.actor.SetMapper(self.mapper)

#     def attach(self, scene):
#         scene.renderer.AddActor(self.actor)

#     def detach(self, scene):
#         scene.renderer.RemoveActor(self.actor)

from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from vtk import vtkCutter, \
    vtkActor, \
    vtkPolyDataMapper, \
    vtkImplicitPlaneRepresentation, \
    vtkImplicitPlaneWidget2, \
    vtkPlane, \
    vtkLODActor

from vtk import vtkBoundingBox

from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty
from dice_tools import wizard


class ClipWidgetInstance:

    def __init__(self, parent, rep_actor, scene):
        self.__parent = parent
        self.__widget = vtkImplicitPlaneWidget2()
        self.__widget.SetInteractor(scene.interactor)
        self.__widget.SetRepresentation(rep_actor)
        self.__widget.SetEnabled(0)
        self.__widget.AddObserver("StartInteractionEvent", self.start_interaction)
        self.__widget.AddObserver("EndInteractionEvent", self.end_interaction)
        self.__widget.AddObserver("InteractionEvent", self.interaction)

    def set_enabled(self, enable):
        self.__widget.SetEnabled(enable)

    def start_interaction(self, obj, ev):
        self.__parent.on_start_interaction()

    def end_interaction(self, obj, ev):
        self.__parent.on_stop_interaction()

    def interaction(self, obj, ev):
        self.__parent.on_interaction()

    def destroy(self):
        self.__widget.Off()
        self.__widget.SetEnabled(0)


class CutterWidget(SimpleGeometry):

    def __init__(self, target, **kwargs):
        name = target.name + '_slice'
        super().__init__(name=name,
            lod=True, **kwargs)

        self.__instances = {}
        self.__target = target
        self.__normal = [1, 0, 0]
        self.color = [0,0,1]

        bounds = self.__target.get_bounds(None)
        center = [(a+b)/2.0 for a, b in zip(bounds[::2], bounds[1::2])]
        for i in range(0, 6, 2):
            ext = (bounds[i+1] - bounds[i]) * 0.1 / 2
            bounds[i] -= ext
            bounds[i+1] += ext

        self.__rep_actor = vtkImplicitPlaneRepresentation()
        self.__rep_actor.SetPlaceFactor(1.1)
        self.__rep_actor.PlaceWidget(bounds)
        self.__rep_actor.SetNormal(self.__normal)
        self.__rep_actor.SetOrigin(center)
        self.__rep_actor.SetEdgeColor(0, 1, 0)
        self.__rep_actor.GetOutlineProperty().SetColor(1, 0, 1)
        self.__rep_actor.OutlineTranslationOff()

    @property
    def target(self):
        return self.__target

    def attach(self, scene):
        super().attach(scene)
        self.__instances[scene] = ClipWidgetInstance(self, self.__rep_actor, scene)

    def detach(self, scene):
        super().detach(scene)
        self.__instances[scene].destroy()
        del self.__instances[scene]

    def on_start_interaction(self):
        # self.__target.visible = True
        self.visible = False

    def on_stop_interaction(self):
        pass

    def on_interaction(self):
        self.__normal = self.__rep_actor.GetNormal()
        wizard.w_property_changed(self,
            name = "plane_normal", value = self.plane_normal)
        wizard.w_property_changed(self,
            name = "plane_origin", value = self.plane_origin)

    def set_selected(self, enable):
        super().set_selected(enable)
        for v in self.__instances.values():
            v.set_enabled(enable)

    def apply(self):
        self.__plane = vtkPlane()
        self.__rep_actor.GetPlane(self.__plane)
        source = vtkCutter()
        source.SetCutFunction(self.__plane)
        for v in self.__target.get_sources():
            if v.IsA("vtkAlgorithm"):
                source.AddInputConnection(v.GetOutputPort())
            elif v.IsA("vtkDataObject"):
                source.AddInputDataObject(v)
        self.source = source
        self.__target.visible = False
        self.mapper.SetScalarMode(self.__target.mapper.GetScalarMode())
        self.mapper.SelectColorArray(self.__target.mapper.GetArrayName())
        self.mapper.SetScalarRange(self.__target.mapper.GetScalarRange())
        self.mapper.SetLookupTable(self.__target.mapper.GetLookupTable())

        self.visible = True

    @GeometryProperty
    def plane_normal(self):
        return self.__normal

    @plane_normal.setter
    def plane_normal(self, value):
        if self.__normal != value:
            self.__normal = value
            self.__rep_actor.SetNormal(value)

    @GeometryProperty
    def plane_origin(self):
        return self.__rep_actor.GetOrigin()

    @plane_origin.setter
    def plane_origin(self, value):
        if tuple(self.__rep_actor.GetOrigin()) != tuple(value):
            self.__rep_actor.SetOrigin(value)
