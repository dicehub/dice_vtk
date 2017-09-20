# External modules
# ================
from vtk import vtkTextSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class Text(SimpleGeometry):
    def __init__(self, name='Text', **kwargs):
        super().__init__(name=name,
            source=vtkTextSource, **kwargs)

    @GeometryProperty
    def text(self):
        return self.source.GetText()

    @text.setter
    def text(self, value):
        self.source.SetText(value)
