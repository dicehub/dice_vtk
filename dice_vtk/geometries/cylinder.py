# Standard Python modules
# =======================

# External modules
# ================
from vtk import vtkCylinderSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class Cylinder(SimpleGeometry):
    """
    Creates a polygonal cylinder centered at Center; The axis of the cylinder
    is aligned along the global y-axis. The height and radius of the cylinder
    can be specified, as well as the number of sides. It is also possible to
    control whether the cylinder is open-ended or capped.
    """
    def __init__(self, name='Cylinder', **kwargs):
        super().__init__(name=name,
                source=vtkCylinderSource, **kwargs)

    @GeometryProperty
    def radius(self):
        return self.source.GetRadius()

    @radius.setter
    def radius(self, value):
        self.source.SetRadius(value)

    @GeometryProperty
    def height(self):
        return self.source.GetHeight()

    @height.setter
    def height(self, value):
        self.source.SetHeight(value)

    @GeometryProperty
    def resolution(self):
        return self.source.GetResolution()

    @resolution.setter
    def resolution(self, value):
        self.source.SetResolution(value)

