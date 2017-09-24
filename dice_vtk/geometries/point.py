# External modules
# ================
from vtk import vtkPointSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class Point(SimpleGeometry):
    def __init__(self, name='Point', **kwargs):
        super().__init__(name=name,
            source=vtkPointSource, **kwargs)

    @GeometryProperty
    def number_of_points(self):
        return self.source.GetNumberOfPoints()

    @number_of_points.setter
    def number_of_points(self, value):
        self.source.SetNumberOfPoints(value)

    @GeometryProperty
    def radius(self):
        return self.source.GetRadius()

    @radius.setter
    def radius(self, value):
        self.source.SetRadius(value)
