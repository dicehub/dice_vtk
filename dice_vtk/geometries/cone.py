# Standard Python modules
# =======================

# External modules
# ================
from vtk import vtkConeSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class Cone(SimpleGeometry):
    """
    Creates a cone centered at a specified point and pointing in a specified
    direction. (By default, the center is the origin and the direction is the
    x-axis.) Depending upon the resolution of this object, different
    representations are created. If resolution=0 a line is created; if
    resolution=1, a single triangle is created; if resolution=2, two crossed
    triangles are created. For resolution > 2, a 3D cone (with resolution
    number of sides) is created. It also is possible to control whether the
    bottom of the cone is capped with a (resolution-sided) polygon, and to
    specify the height and radius of the cone.
    """
    def __init__(self, name='Cone', **kwargs):
        super().__init__(name=name,
            source=vtkConeSource, **kwargs)

    @GeometryProperty
    def height(self):
        return self.source.GetHeight()

    @height.setter
    def height(self, value):
        self.source.SetHeight(value)

    @GeometryProperty
    def radius(self):
        return self.source.GetRadius()

    @radius.setter
    def radius(self, value):
        self.source.SetRadius(value)

    @GeometryProperty
    def resolution(self):
        return self.source.GetResolution()

    @resolution.setter
    def resolution(self, value):
        self.source.SetResolution(value)

    @GeometryProperty
    def direction(self):
        return self.source.GetDirection()

    @direction.setter
    def direction(self, value):
        self.source.SetDirection(value)

    @GeometryProperty
    def capping(self):
        return self.source.GetCapping()

    @capping.setter
    def capping(self, value):
        self.source.SetCapping(value)


