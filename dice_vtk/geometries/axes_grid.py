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


class AxesGridInstance:
    def __init__(self, parent, scene, axes_off='y'):
        self.interactor = scene.interactor
        self.renderer = scene.renderer
        self.parent = parent
        self.axes_off = axes_off

        self.__w_plane_actor = vtkLODActor()
        self.__w_plane_source = vtkPlaneSource()
        self.__w_plane_mapper = vtkPolyDataMapper()

        if axes_off == 'x':
            self.__w_plane_source.SetOrigin(0, parent.border_y_min, parent.border_z_max)
            self.__w_plane_source.SetPoint1(0, parent.border_y_max, parent.border_z_max)
            self.__w_plane_source.SetPoint2(0, parent.border_y_min, parent.border_z_min)
        if axes_off == 'y':
            self.__w_plane_source.SetOrigin(parent.border_x_min, 0, parent.border_z_min)
            self.__w_plane_source.SetPoint1(parent.border_x_min, 0, parent.border_z_max)
            self.__w_plane_source.SetPoint2(parent.border_x_max, 0, parent.border_z_min)
        if axes_off == 'z':
            self.__w_plane_source.SetOrigin(parent.border_x_min, parent.border_y_min, 0)
            self.__w_plane_source.SetPoint1(parent.border_x_min, parent.border_y_max, 0)
            self.__w_plane_source.SetPoint2(parent.border_x_max, parent.border_y_min, 0)

        self.__w_plane_source.SetNormal(
            5 if axes_off == 'x' else 0,
            5 if axes_off == 'y' else 0,
            5 if axes_off == 'z' else 0
        )

        self.__w_plane_mapper.SetInputConnection(self.__w_plane_source.GetOutputPort())
        self.__w_plane_actor.SetMapper(self.__w_plane_mapper)
        self.__w_plane_actor.GetProperty().SetOpacity(0.1)
        self.__w_plane_actor.GetProperty().SetColor(
            1 if axes_off == 'x' else 0,
            1 if axes_off == 'y' else 0,
            1 if axes_off == 'z' else 0)
        self.__w_plane_actor.SetPickable(0)

        self.renderer.AddActor(self.__w_plane_actor)

        self.__w_cube_axes_actor = vtkCubeAxesActor()
        self.__w_cube_axes_actor.SetBounds(self.__w_plane_actor.GetBounds())
        self.__w_cube_axes_actor.SetCamera(self.renderer.GetActiveCamera())

        for i in range(0, 3):
            self.__w_cube_axes_actor.GetLabelTextProperty(i).SetColor(
                0.7 if axes_off == 'x' else 0.0,
                0.7 if axes_off == 'y' else 0.0,
                0.7 if axes_off == 'z' else 0.0
            )
            self.__w_cube_axes_actor.GetTitleTextProperty(i).SetColor(
                1.0 if axes_off == 'x' else 0.0,
                1.0 if axes_off == 'y' else 0.0,
                1.0 if axes_off == 'z' else 0.0
            )

        if axes_off != 'x':
            self.__w_cube_axes_actor.DrawXGridlinesOn()
        if axes_off != 'y':
            self.__w_cube_axes_actor.DrawYGridlinesOn()
        if axes_off != 'z':
            self.__w_cube_axes_actor.DrawZGridlinesOn()

        self.__w_cube_axes_actor.GetXAxesGridlinesProperty().SetEdgeVisibility(1)
        self.__w_cube_axes_actor.GetYAxesGridlinesProperty().SetEdgeVisibility(1)
        self.__w_cube_axes_actor.GetZAxesGridlinesProperty().SetEdgeVisibility(1)
        self.__w_cube_axes_actor.GetXAxesLinesProperty().SetColor(1, 0, 1)
        self.__w_cube_axes_actor.GetYAxesLinesProperty().SetColor(1, 0, 1)
        self.__w_cube_axes_actor.GetZAxesLinesProperty().SetColor(1, 0, 1)
        self.__w_cube_axes_actor.SetGridLineLocation(VTK_GRID_LINES_FURTHEST)

        if axes_off == 'x':
            self.__w_cube_axes_actor.SetXAxisLabelVisibility(0)
            self.__w_cube_axes_actor.SetXAxisVisibility(0)
        if axes_off == 'y':
            self.__w_cube_axes_actor.SetYAxisLabelVisibility(0)
            self.__w_cube_axes_actor.SetYAxisVisibility(0)
        if axes_off == 'z':
            self.__w_cube_axes_actor.SetZAxisLabelVisibility(0)
            self.__w_cube_axes_actor.SetZAxisVisibility(0)

        self.renderer.AddActor(self.__w_cube_axes_actor)

    def setSize(self):
        if self.parent.border_x_min != 0 and self.parent.border_x_max != 0 \
                and self.parent.border_y_min != 0 and self.parent.border_y_max != 0 \
                and self.parent.border_z_min != 0 and self.parent.border_z_max != 0:
            if self.axes_off == 'x':
                self.__w_plane_source.SetOrigin(0, self.parent.border_y_min, self.parent.border_z_max)
                self.__w_plane_source.SetPoint1(0, self.parent.border_y_max, self.parent.border_z_max)
                self.__w_plane_source.SetPoint2(0, self.parent.border_y_min, self.parent.border_z_min)
            if self.axes_off == 'y':
                self.__w_plane_source.SetOrigin(self.parent.border_x_min, 0, self.parent.border_z_min)
                self.__w_plane_source.SetPoint1(self.parent.border_x_min, 0, self.parent.border_z_max)
                self.__w_plane_source.SetPoint2(self.parent.border_x_max, 0, self.parent.border_z_min)
            if self.axes_off == 'z':
                self.__w_plane_source.SetOrigin(self.parent.border_x_min, self.parent.border_y_min, 0)
                self.__w_plane_source.SetPoint1(self.parent.border_x_min, self.parent.border_y_max, 0)
                self.__w_plane_source.SetPoint2(self.parent.border_x_max, self.parent.border_y_min, 0)
            self.__w_cube_axes_actor.SetBounds(self.__w_plane_actor.GetBounds())

    def destroy(self):
        self.renderer.RemoveActor(self.__w_plane_actor)
        self.renderer.RemoveActor(self.__w_cube_axes_actor)


class AxesGrid(VisObject):

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
        GeometryBase.attach(self, scene)
        self.instances[str(id(scene)) + 'x'] = AxesGridInstance(self, scene, axes_off='x')
        self.instances[str(id(scene)) + 'y'] = AxesGridInstance(self, scene, axes_off='y')
        self.instances[str(id(scene)) + 'z'] = AxesGridInstance(self, scene, axes_off='z')

    def detach(self, scene):
        GeometryBase.detach(self, scene)
        self.instances[str(id(scene)) + 'x'].destroy()
        self.instances[str(id(scene)) + 'y'].destroy()
        self.instances[str(id(scene)) + 'z'].destroy()
        del self.instances[str(id(scene)) + 'x']
        del self.instances[str(id(scene)) + 'y']
        del self.instances[str(id(scene)) + 'z']
