from vtk import vtkCommand, \
    vtkActor, \
    vtkPlaneSource, \
    vtkCubeSource, \
    vtkAxesActor, \
    vtkOrientationMarkerWidget, \
    vtkPolyDataNormals, \
    vtkPolyDataMapper, \
    vtkLODActor, \
    vtkOBJReader, \
    vtkSTLReader, \
    vtkCubeAxesActor, \
    vtkPlaneWidget

import sys
VTK_GRID_LINES_FURTHEST = 2

from .geometry_base import VisObject


class AxesWidgetInstance:
    def __init__(self, scene):
        self.interactor = scene.interactor
        self.__w_plane_actor = vtkLODActor()
        self.__w_plane_source = vtkPlaneSource()
        self.__w_plane_mapper = vtkPolyDataMapper()
        self.__axis_widget = vtkOrientationMarkerWidget()
        __w_axes = vtkAxesActor()
        self.__axis_widget.SetOrientationMarker(__w_axes)
        self.__axis_widget.SetInteractor(self.interactor)
        self.__axis_widget.SetEnabled(1)
        self.__axis_widget.SetViewport(0.0, 0.0, 0.3, 0.3)
        self.__axis_widget.PickingManagedOff()
        self.__axis_widget.InteractiveOff()
        self.__axis_widget.SetOutlineColor(1, 0, 0)

    def destroy(self):
        self.__axis_widget.SetEnabled(0)


class AxesWidget(VisObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_plane = 5
        self.border_x_min = -4
        self.border_x_max = 4
        self.border_y_min = -4
        self.border_y_max = 4
        self.border_z_min = -4
        self.border_z_max = 4
        self.ci = 0.5
        self.instances = {}

    def attach(self, scene):
        super().attach(scene)
        self.instances[scene] = AxesWidgetInstance(scene)

    def detach(self, scene):
        super().detach(scene)
        self.instances.pop(scene).destroy()
