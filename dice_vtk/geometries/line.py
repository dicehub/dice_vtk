# External modules
# ================
from vtk import vtkLineSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class Line(SimpleGeometry):
    def __init__(self, name='Line', **kwargs):
        super().__init__(name=name,
            source=vtkLineSource, **kwargs)

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
    def resolution(self):
        return self.source.GetResolution()

    @resolution.setter
    def resolution(self, value):
        self.source.SetResolution(value)