from vtk import vtkActor
from vtk import vtkTransform
from vtk import vtkSphereSource
from vtk import vtkPolyDataMapper
from vtk import vtkMath

import math

from .geometry_base import GeometryBase, GeometryProperty
from ..interactor import BasicInteractor
from dice_tools import wizard

class WidgetInstance(BasicInteractor):

    def __init__(self, parent, scene):
        self.parent = parent
        self.scene = scene
        self.renderer = scene.renderer

        source = vtkSphereSource()
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        self.actor = vtkActor()
        self.actor.SetMapper(mapper)
        self.update()
        scene.renderer.AddActor(self.actor)
        wizard.subscribe(self, self.actor)
        wizard.subscribe(self, scene)

    def update(self):
        self.actor.SetVisibility(self.parent.visible)
        self.actor.SetPosition(self.parent.position)
        self.actor.GetProperty().SetColor(self.parent.get_color())
        self.actor.GetProperty().SetOpacity(self.parent.opacity)
        self.actor.GetProperty().SetRepresentation(self.parent.representation)
        self.actor.GetProperty().SetEdgeVisibility(self.parent.edge_visible)
        if self.parent.target:
            size = self.actor.GetXRange()
            apos = self.actor.GetPosition()
            self.renderer.SetWorldPoint(*apos, 1)
            self.renderer.WorldToView()
            pt = self.renderer.GetViewPoint()
            pos = (pt[0] + 0.05, pt[1], pt[2])
            self.renderer.SetViewPoint(*pos)
            self.renderer.ViewToWorld()
            zpos = self.renderer.GetWorldPoint()
            scale = math.sqrt(vtkMath.Distance2BetweenPoints(apos, zpos[:3]))
            target_bounds = self.parent.target.get_bounds(self.scene)
            dist = min((target_bounds[i+1]-target_bounds[i] for i in range(0, 6, 2)))
            scale = min(scale, dist/3.0)
            self.actor.SetScale(scale, scale, scale)

    def destroy(self, scene):
        scene.renderer.RemoveActor(self.actor)

    def w_scene_actor_clicked(self, actor, x, y, control_modifier):
        wizard.w_geometry_object_clicked(self.parent, x, y, control_modifier)

    def w_scene_camera_updated(self, scene, *args, **kwargs):
        self.update()


class DynamicSphere(GeometryBase):

    def __init__(self, name='DynamicSphere', **kwargs):
        super().__init__(name=name, **kwargs)
        self.widgets = {}
        self.__position = [0, 0, 0]
        self.__color = [0.5, 1, 1]
        self.__opacity = 0.8
        self.__target = None
        self.__visible = True
        self.__representation = 2
        self.__edge_visible = False

    def get_bounds(self, scene):
        return self.widgets[scene].actor.GetBounds()

    def get_sources(self):
        return ()

    def get_actors(self):
        return ()

    def get_data(self):
        return ()

    def attach(self, scene):
        GeometryBase.attach(self, scene)
        self.widgets[scene] = WidgetInstance(self, scene)

    def detach(self, scene):
        widget = self.widgets.pop(scene)
        widget.destroy(scene)

    @GeometryProperty
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = value
        for v in self.widgets.values():
            v.update()

    def get_color(self):
        return self.__color

    def set_color(self, value):
        self.__color = value
        for v in self.widgets.values():
            v.update()

    @GeometryProperty
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        self.__target = value
        for v in self.widgets.values():
            v.update()

    @GeometryProperty
    def opacity(self):
        return self.__opacity

    @opacity.setter
    def opacity(self, value):
        self.__opacity = value
        for v in self.widgets.values():
            v.update()

    @GeometryProperty('str')
    def representation(self):
        return self.__representation

    @representation.setter
    def representation(self, value):
        self.__representation = value
        for v in self.widgets.values():
            v.update()

    @GeometryProperty
    def edge_visible(self):
        return self.__edge_visible

    @edge_visible.setter
    def edge_visible(self, value):
        self.__edge_visible = value
        for v in self.widgets.values():
            v.update()

    @GeometryProperty('bool')
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = value
        for v in self.widgets.values():
            v.update()