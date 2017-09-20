# External modules
# ================
from vtk import vtkEarthSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry


class Earth(SimpleGeometry):
    """
    Creates a spherical rendering of the geographical shapes of the major
    continents of the earth. The radius defines the radius of the sphere at
    which the continents are placed. Obtains data from an embedded array of
    coordinates.
    """
    def __init__(self, name='Earth', **kwargs):
        super().__init__(name=name,
            source=vtkEarthSource, **kwargs)

