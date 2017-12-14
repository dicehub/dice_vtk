# Standard Python modules
# =======================

# External modules
# ================
from vtk import vtkCubeSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty


class Cube(SimpleGeometry):
    """
    Creates a cube centered at origin. The cube is represented with four-sided
    polygons. It is possible to specify the length, width, and height of the
    cube independently.
    """
    def __init__(self, name='Cube', **kwargs):
        super().__init__(name='Cube',
            source=vtkCubeSource, **kwargs)

    @GeometryProperty
    def x_length(self):
        return self.source.GetXLength()

    @x_length.setter
    def x_length(self, value):
        self.source.SetXLength(value)

    @GeometryProperty
    def y_length(self):
        return self.source.GetYLength()

    @y_length.setter
    def y_length(self, value):
        self.source.SetYLength(value)

    @GeometryProperty
    def z_length(self):
        return self.source.GetZLength()

    @z_length.setter
    def z_length(self, value):
        self.source.SetZLength(value)
