# External modules
# ================
from vtk import vtkTexturedSphereSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry

class TexturedSphere(SimpleGeometry):
    def __init__(self, name='TexturedSphere', **kwargs):
        super().__init__(name=name,
            source=vtkTexturedSphereSource, **kwargs)
