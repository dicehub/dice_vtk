# External modules
# ================
from vtk import vtkSuperquadricSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry

class Superquadric(SimpleGeometry):
    def __init__(self, name='Superquadric', **kwargs):
        super().__init__(name=name, 
            source=vtkSuperquadricSource, **kwargs)