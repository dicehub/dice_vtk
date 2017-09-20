# Standard Python modules
# =======================
import math

# External modules
# ================
from vtk import vtkDiskSource

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty


class Disk(SimpleGeometry):
    """
    Creates a polygonal disk with a hole in the center. The disk has zero
    height. The user can specify the inner and outer radius of the disk, and
    the radial and circumferential resolution of the polygonal representation.
    """
    def __init__(self, name='Disk', **kwargs):
        super().__init__(name=name,
            source=vtkDiskSource, **kwargs)
        self.__normal = [0, 1, 0]
        self.__update_normal()

    def __update_normal(self):
        r = math.sqrt(sum(map(lambda x: x * x, self.__normal)))
        if r == 0:
            return
        t = math.atan2(self.__normal[0], self.__normal[1])
        p = math.acos(self.__normal[2] / r)
        orientation = self.actor.GetOrientation()
        self.actor.SetOrientation(orientation[0],
                                  math.degrees(p), math.degrees(t))

    @GeometryProperty
    def normal(self):
        return self.__normal

    @normal.setter
    def normal(self, value):
        self.__normal = value
        self.__update_normal()

    @GeometryProperty
    def inner_radius(self):
        return self.source.GetInnerRadius()

    @inner_radius.setter
    def inner_radius(self, value):
        self.source.SetInnerRadius(value)

    @GeometryProperty
    def outer_radius(self):
        return self.source.GetOuterRadius()

    @outer_radius.setter
    def outer_radius(self, value):
        self.source.SetOuterRadius(value)

    @GeometryProperty
    def circumferential_resolution(self):
        return self.source.GetCircumferentialResolution()

    @circumferential_resolution.setter
    def circumferential_resolution(self, value):
        self.source.SetCircumferentialResolution(value)

    @GeometryProperty
    def radial_resolution(self):
        return self.source.GetRadialResolution()

    @radial_resolution.setter
    def radial_resolution(self, value):
        self.source.SetRadialResolution(value)
