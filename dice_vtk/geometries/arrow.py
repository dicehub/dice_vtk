# Standard Python modules
# =======================

# External modules
# ================
from vtk import vtkArrowSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty

class Arrow(SimpleGeometry):
    """
    Cylinder appended to a cone to form an arrow. It was intended to be used as
    the source for a glyph. The shaft base is always at (0,0,0). The arrow tip
    is always at (1,0,0). If "Invert" is true, then the ends are flipped i.e.
    tip is at (0,0,0) while base is at (1, 0, 0). The resolution of the cone
    and shaft default to 6. The radius of the cone and shaft default to 0.03
    and 0.1. The length of the tip defaults to 0.35.
    """

    def __init__(self, name='Arrow', **kwargs):
        super().__init__(name=name, source=vtkArrowSource,
            **kwargs)

    @GeometryProperty
    def shaft_radius(self):
        return self.source.GetShaftRadius()

    @shaft_radius.setter
    def shaft_radius(self, value):
        self.source.SetShaftRadius(value)

    @GeometryProperty
    def shaft_resolution(self):
        return self.source.GetShaftResolution()

    @shaft_resolution.setter
    def shaft_resolution(self, value):
        self.source.SetShaftResolution(value)

    @GeometryProperty
    def tip_resolution(self):
        return self.source.GetTipResolution()

    @tip_resolution.setter
    def tip_resolution(self, value):
        self.source.SetTipResolution(value)

    @GeometryProperty
    def tip_length(self):
        return self.source.GetTipLength()

    @tip_length.setter
    def tip_length(self, value):
        self.source.SetTipLength(value)

    @GeometryProperty
    def tip_radius(self):
        return self.source.GetTipRadius()

    @tip_radius.setter
    def tip_radius(self, value):
        self.source.SetTipRadius(value)
