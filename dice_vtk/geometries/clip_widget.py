from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from vtk import vtkTableBasedClipDataSet
from vtk import vtkClipPolyData
from vtk import vtkExtractGeometry
from vtk import vtkActor
from vtk import vtkPolyDataMapper
from vtk import vtkImplicitPlaneRepresentation
from vtk import vtkImplicitPlaneWidget2
from vtk import vtkPlane
from vtk import vtkLODActor
import time
from vtk import vtkBoundingBox

from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty
from dice_tools import wizard
from vtk import vtkExtractDataSets


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


class ClipWidget(SimpleGeometry):

    def __init__(self, target, **kwargs):
        name = target.name + '_clip'
        super().__init__(name=name,
            lod=True, **kwargs)

        self.__target = target
        self.__instances = {}

        bounds = self.__target.get_bounds(None)
        center = [(a+b)/2.0 for a, b in zip(bounds[::2], bounds[1::2])]
        for i in range(0, 6, 2):
            ext = (bounds[i+1] - bounds[i]) * 0.1 / 2
            bounds[i] -= ext
            bounds[i+1] += ext

        self.__normal = [1, 0, 0]
        self.__inside_out = True
        self.__crinkle = False

        self.__modified = True
        self.__plane = vtkPlane()
        self.__rep_actor = vtkImplicitPlaneRepresentation()
        self.__rep_actor.SetPlaceFactor(1.1)
        self.__rep_actor.PlaceWidget(bounds)
        self.__rep_actor.SetNormal(self.__normal)
        self.__rep_actor.SetOrigin(center)
        self.__rep_actor.SetEdgeColor(0, 1, 0)
        self.__rep_actor.GetOutlineProperty().SetColor(1, 0, 1)
        self.__rep_actor.OutlineTranslationOff()
       
    def __set_clip_source(self):
        for v in self.__target.get_sources():
            if (not v.IsA("vtkPolyData") and not
                    v.IsA("vtkPolyDataAlgorithm")):
                source=vtkTableBasedClipDataSet()
                break
        else:
            source=vtkClipPolyData()
        self.__plane = vtkPlane()
        self.__rep_actor.GetPlane(self.__plane)
        source.SetClipFunction(self.__plane)
        if self.__inside_out:
            source.InsideOutOn()
        for v in self.__target.get_sources():
            if v.IsA("vtkAlgorithm"):
                source.AddInputConnection(v.GetOutputPort())
            elif v.IsA("vtkDataObject"):
                source.AddInputData(v)
        self.source = source

    def __set_crinkle_source(self):
        source=vtkExtractGeometry()
        source.SetImplicitFunction(self.__plane)
        if self.__inside_out:
            source.ExtractInsideOn()
        for v in self.__target.get_sources():
            if v.IsA("vtkAlgorithm"):
                source.AddInputConnection(v.GetOutputPort())
            elif v.IsA("vtkDataObject"):
                source.AddInputData(v)
        self.source = source

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
        self.__target.visible = True
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
        plane = vtkPlane()
        self.__rep_actor.GetPlane(plane)
        if not self.__modified:
            if (plane.GetOrigin() != self.__plane.GetOrigin()
                    or plane.GetNormal() != self.__plane.GetNormal()):
                self.__modified = True

        if self.__modified:
            self.__plane = plane
            if self.__crinkle:
                self.__set_crinkle_source()
            else:
                self.__set_clip_source()

        self.__modified = False
        self.__target.visible = False

        # self.mapper.SetInputConnection(self.__target.mapper.GetOutputPort())

        # self.mapper.SetScalarMode(self.__target.mapper.GetScalarMode())
        self.mapper.SelectColorArray(self.__target.mapper.GetArrayName())
        # self.mapper.SetScalarRange(self.__target.mapper.GetScalarRange())
        self.mapper.SetLookupTable(self.__target.mapper.GetLookupTable())

        self.visible = True

    @GeometryProperty
    def plane_normal(self):
        return self.__normal

    @plane_normal.setter
    def plane_normal(self, value):
        if self.__normal != value:
            self.__modified = True
            self.__normal = value
            self.__rep_actor.SetNormal(value)

    @GeometryProperty
    def plane_origin(self):
        return self.__rep_actor.GetOrigin()

    @plane_origin.setter
    def plane_origin(self, value):
        if tuple(self.__rep_actor.GetOrigin()) != tuple(value):
            self.__modified = True
            self.__rep_actor.SetOrigin(value)

    @GeometryProperty
    def inside_out(self):
        return self.__inside_out

    @inside_out.setter
    def inside_out(self, value):
        if self.__inside_out != value:
            self.__modified = True
            self.__inside_out = value

    @GeometryProperty
    def crinkle(self):
        return self.__crinkle

    @crinkle.setter
    def crinkle(self, value):
        if self.__crinkle != value:
            self.__modified = True
            self.__crinkle = value
