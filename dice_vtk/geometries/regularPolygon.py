# External modules
# ================
from vtk import vtkRegularPolygonSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class RegularPolygon(SimpleGeometry):
    def __init__(self, name='RegularPolygon', **kwargs):
        super().__init__(name=name,
            source=vtkRegularPolygonSource, **kwargs)

    @GeometryProperty
    def radius(self):
        return self.source.GetRadius()

    @radius.setter
    def radius(self, value):
        self.source.SetRadius(value)

    @GeometryProperty
    def number_of_sides(self):
        return self.source.GetNumberOfSides()

    @number_of_sides.setter
    def number_of_sides(self, value):
        self.source.SetNumberOfSides(value)
