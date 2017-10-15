# External modules
# ================
from vtk import vtkPlatonicSolidSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class PlatonicSolid(SimpleGeometry):
    def __init__(self, name='PlatonicSolid', **kwargs):
        super().__init__(name=name,
            source=vtkPlatonicSolidSource, **kwargs)

