# Standard Python modules
# =======================

# External modules
# ================
from vtk import vtkPolyDataMapper
from vtk import vtkDataSetMapper
from vtk import vtkLookupTable

from vtk import vtkActor
from vtk import vtkQuadricLODActor
from vtk import vtkModifiedBSPTree
from vtk import vtkBoundingBox
from vtk import vtkDataSetSurfaceFilter
from vtk import vtkCompositeDataGeometryFilter

# DICE modules
# ============
from .geometry_base import GeometryBase, GeometryProperty
from dice_tools import wizard

class SimpleGeometry(GeometryBase):
    """
    Base class for DICE wrappers over VTK geometry objects.
    """
    def __init__(self, name, source=None,
            lod=False,
            color=(1.0, 1.0, 1.0),
            **kwargs):
        super().__init__(name=name, **kwargs)

        self.__filter = None
        self.__mapper = vtkPolyDataMapper()

        if lod:
            self.__actor = vtkQuadricLODActor()
        else:
            self.__actor = vtkActor()

        # self.__lt = vtkLookupTable()
        # self.__lt.SetHueRange(0.0, 0.66667)
        # self.__mapper.SetLookupTable(self.__lt)

        self.__actor.GetProperty().SetAmbient(0.2)
        self.__actor.GetProperty().SetDiffuse(0.8)
        self.__actor.GetProperty().SetSpecular(0.0)

        self.__actor.SetMapper(self.__mapper)

        self.color=color
        wizard.subscribe(self.w_scene_actor_clicked, actor=self.__actor)
        self.source = source

    def __set_source(self, source):
        if source:
            if isinstance(source, type):
                self.__source = source()
            else:
                self.__source = source

            if (self.__source.IsA("vtkPolyData") or 
                    self.__source.IsA("vtkPolyDataAlgorithm")):
                self.__filter = None
                if self.__source.IsA("vtkDataSet"):
                    self.__mapper.SetInputData(self.__source)
                elif self.__source.IsA("vtkAlgorithm"):
                    self.__mapper.SetInputConnection(self.__source.GetOutputPort())
            elif self.__source.IsA("vtkMultiBlockDataSet"):
                if not self.__filter or not self.__filter.IsA("vtkCompositeDataGeometryFilter"):
                    self.__filter = vtkCompositeDataGeometryFilter()
                self.__filter.SetInputData(self.__source)
                self.__mapper.SetInputConnection(self.__filter.GetOutputPort())
            elif self.__source.IsA("vtkMultiBlockDataSetAlgorithm"):
                if not self.__filter or not self.__filter.IsA("vtkCompositeDataGeometryFilter"):
                    self.__filter = vtkCompositeDataGeometryFilter()
                self.__filter.SetInputConnection(self.__source.GetOutputPort())
                self.__mapper.SetInputConnection(self.__filter.GetOutputPort())
            else:
                if not self.__filter or not self.__filter.IsA("vtkDataSetSurfaceFilter"):
                    self.__filter = vtkDataSetSurfaceFilter()
                if self.__source.IsA("vtkDataSet"):
                    self.__filter.SetInputData(self.__source)
                elif self.__source.IsA("vtkAlgorithm"):
                    self.__filter.SetInputConnection(self.__source.GetOutputPort())
                self.__mapper.SetInputConnection(self.__filter.GetOutputPort())
        else:
            self.__source = None
            self.__filter = None
            self.__mapper.SetInputData(None)
            self.__mapper.SetInputConnection(None)

    def w_scene_actor_clicked(self, actor, x, y, control_modifier):
        wizard.w_geometry_object_clicked(self, x, y, control_modifier)

    def get_sources(self):
        if self.__source:
            return (self.__source,)
        return ()

    def get_actors(self):
        return (self.__actor,)

    @property
    def actor(self):
        return self.__actor

    @property
    def mapper(self):
        return self.__mapper

    @GeometryProperty
    def source(self):
        return self.__source

    @source.setter
    def source(self, value):
        self.__set_source(value)

    def get_bounds(self, scene):
        bbox = vtkBoundingBox()
        bbox.AddBounds(self.actor.GetBounds())
        bounds = [0]*6
        bbox.GetBounds(bounds)
        return bounds

    def attach(self, scene):
        scene.renderer.AddActor(self.actor)

    def detach(self, scene):
        scene.renderer.RemoveActor(self.actor)

    def get_color(self):
        return self.actor.GetProperty().GetColor()

    def set_color(self, value):
        self.actor.GetProperty().SetColor(value)

    @GeometryProperty
    def visible(self):
        return self.actor.GetVisibility()

    @visible.setter
    def visible(self, value):
        self.actor.SetVisibility(value)

    @GeometryProperty
    def opacity(self):
        return self.actor.GetProperty().GetOpacity()

    @opacity.setter
    def opacity(self, value):
        self.actor.GetProperty().SetOpacity(value)

    @GeometryProperty
    def representation(self):
        return self.actor.GetProperty().GetRepresentation()

    @representation.setter
    def representation(self, value):
        self.actor.GetProperty().SetRepresentation(value)

    @GeometryProperty
    def position(self):
        return self.actor.GetPosition()

    @position.setter
    def position(self, value):
        self.actor.SetPosition(value)

    @GeometryProperty
    def edge_color(self):
        return self.actor.GetProperty().GetEdgeColor()

    @edge_color.setter
    def edge_color(self, value):
        self.actor.GetProperty().SetEdgeColor(value)

    @GeometryProperty
    def edge_visible(self):
        return self.actor.GetProperty().GetEdgeVisibility()

    @edge_visible.setter
    def edge_visible(self, value):
        self.actor.GetProperty().SetEdgeVisibility(value)

    @GeometryProperty
    def line_width(self):
        return self.actor.GetProperty().GetLineWidth()

    @line_width.setter
    def line_width(self, value):
        self.actor.GetProperty().SetLineWidth(value)

    @GeometryProperty
    def point_size(self):
        return self.actor.GetProperty().GetPointSize()

    @point_size.setter
    def point_size(self, value):
        self.actor.GetProperty().SetPointSize(value)


