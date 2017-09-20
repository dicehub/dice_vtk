from .simple_geometry import SimpleGeometry
from vtk import vtkSphereSource
from .geometry_base import GeometryProperty

class Sphere(SimpleGeometry):

    def __init__(self, name='Sphere', **kwargs):
        super().__init__(name=name,
            source=vtkSphereSource, **kwargs)

    @GeometryProperty
    def radius(self):
        return self.source.GetRadius()

    @radius.setter
    def radius(self, value):
        self.source.SetRadius(value)

    @GeometryProperty
    def start_phi(self):
        return self.source.GetStartPhi()

    @start_phi.setter
    def start_phi(self, value):
        self.source.SetStartPhi(value)

    @GeometryProperty
    def end_phi(self):
        return self.source.GetEndPhi()

    @end_phi.setter
    def end_phi(self, value):
        self.source.SetEndPhi(value)

    @GeometryProperty
    def phi_resolution(self):
        return self.source.GetPhiResolution()

    @phi_resolution.setter
    def phi_resolution(self, value):
        self.source.GetPhiResolution(value)

    @GeometryProperty
    def start_theta(self):
        return self.source.GetStartTheta()

    @start_theta.setter
    def start_theta(self, value):
        self.source.SetStartTheta(value)

    @GeometryProperty
    def end_theta(self):
        return self.source.GetEndTheta()

    @end_theta.setter
    def end_theta(self, value):
        self.source.SetEndTheta(value)

    @GeometryProperty
    def theta_resolution(self):
        return self.source.GetThetaResolution()

    @theta_resolution.setter
    def theta_resolution(self, value):
        self.source.SetThetaResolution(value)
