# External modules
# ================
from vtk import vtkSTLReader

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class VtkSTL(SimpleGeometry):
    def __init__(self, name='VtkSTL', **kwargs):
        super().__init__(name=name,
            source=vtkSTLReader, **kwargs)

    @GeometryProperty
    def file_name(self):
        return self.source.GetFileName()

    @file_name.setter
    def file_name(self, value):
        self.source.SetFileName(value)