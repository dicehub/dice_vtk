# External modules
# ================
from vtk import vtkOBJReader

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class VtkOBJ(SimpleGeometry):
    def __init__(self, name='VtkOBJ', **kwargs):
        super().__init__(name=name,
            source=vtkOBJReader, **kwargs)

    @GeometryProperty
    def file_name(self):
        return self.source.GetFileName()

    @file_name.setter
    def file_name(self, value):
        self.source.SetFileName(value)
