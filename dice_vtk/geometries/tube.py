# External modules
# ================
from vtk import vtkLineSource, \
    vtkPolyDataMapper, \
    vtkActor, \
    vtkTubeFilter

# DICE modules
# ============
from .simple_geometry import SimpleGeometry
from .geometry_base import GeometryProperty


class Tube(SimpleGeometry):
    def __init__(self, name='Tube', **kwargs):
        super().__init__(name=name,
            source=vtkTubeFilter, **kwargs)

        self.line = vtkLineSource()
        self.line.SetPoint1(0, 0, 0)
        self.line.SetPoint2(1, 1, 1)

        self.source.SetInputConnection(self.line.GetOutputPort())
        self.source.SetRadius(.025)
        self.source.SetNumberOfSides(50)
        self.source.SetCapping(1)
        self.source.Update()

        self.actor.GetProperty().SetOpacity(0.5)

    @GeometryProperty
    def point1(self):
        return self.line.GetPoint1()

    @point1.setter
    def point1(self, value):
        self.line.SetPoint1(value)

    @GeometryProperty
    def point2(self):
        return self.line.GetPoint2()

    @point1.setter
    def point2(self, value):
        self.line.SetPoint2(value)

    @GeometryProperty
    def radius(self):
        return self.source.GetRadius()

    @radius.setter
    def radius(self, value):
        self.source.SetRadius(value)
