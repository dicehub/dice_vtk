# External modules
# ================
from vtk import vtkPlaneSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty


class Plane(SimpleGeometry):
    def __init__(self, name='Plane', **kwargs):
        super().__init__(name=name,
            source=vtkPlaneSource, **kwargs)

    @GeometryProperty
    def center(self):
        return self.source.GetCenter()

    @center.setter
    def center(self, value):
        self.source.SetCenter(value)

    @GeometryProperty
    def origin(self):
        return self.source.GetOrigin()

    @origin.setter
    def origin(self, value):
        self.source.SetOrigin(value)

    @GeometryProperty
    def point1(self):
        return self.source.GetPoint1()

    @point1.setter
    def point1(self, value):
        self.source.SetPoint1(value)

    @GeometryProperty
    def point2(self):
        return self.source.GetPoint2()

    @point2.setter
    def point2(self, value):
        self.source.SetPoint2(value)

    @GeometryProperty
    def x_resolution(self):
        return self.source.GetXResolution()

    @x_resolution.setter
    def x_resolution(self, value):
        self.source.SetXResolution(value)

    @GeometryProperty
    def y_resolution(self):
        return self.source.GetYResolution()

    @y_resolution.setter
    def y_resolution(self, value):
        self.source.SetYResolution(value)

    @GeometryProperty
    def normal(self):
        return self.source.GetNormal()

    @normal.setter
    def normal(self, value):
        self.source.SetNormal(value)
