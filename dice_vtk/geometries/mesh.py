# External modules
# ================
from vtk import vtkGeometryFilter

# DICE modules
# ============
from .simple_geometry import SimpleGeometry

class Mesh(SimpleGeometry):
    def __init__(self, name='Mesh', **kwargs):
        super().__init__(name=name,
            source=vtkGeometryFilter,
            lod=True, **kwargs)

