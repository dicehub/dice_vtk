
import math
from .geometry_base import GeometryBase
from ..interactor import BasicInteractor
from dice_tools import wizard

from vtk import vtkArrowSource
from vtk import vtkPolyDataMapper
from vtk import vtkActor
from vtk import vtkCoordinate
from vtk import vtkMath
from vtk import vtkPlane
from vtk import mutable as vtk_mutable
from vtk import vtkBoundedPlanePointPlacer


class TransformGismo(BasicInteractor):

    def __init__(self, scene, **kwargs):
        super().__init__(**kwargs)

        self.scene = scene
        self.renderer = scene.renderer
        self.overlay = scene.overlay

        wizard.subscribe(self, scene)
        wizard.subscribe(self.w_property_changed)

        self.__sources = []
        self.__mappers = []
        self.__actors = []
        self.__targets = []

        orientation = [(0,0,0), (0,0,90), (0,-90,0)]
        colors = [(1,0,0), (0,1,0), (0,0,1)]

        for i in range(3):
            source = vtkArrowSource()
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(source.GetOutputPort())
            actor = vtkActor()
            actor.SetMapper(mapper)
            self.__sources.append(source)
            self.__mappers.append(mapper)
            self.__actors.append(actor)
            actor.SetOrientation(orientation[i])
            actor.GetProperty().SetColor(colors[i])
            self.overlay.AddActor(actor)
            wizard.subscribe(self, actor)
            actor.VisibilityOff()


    def w_scene_actor_pressed(self, actor, x, y, control_modifier):
        for i, v in enumerate(self.__actors):
            if v == actor:
                self.drag_axis = i
                self.drag_pos = list(self.__actors[0].GetPosition())
                self.drag_point = (x, y)
                self.scene.push_interactor(self)
                self.targets_pos = {}
                for t in self.__targets:
                    self.targets_pos[t] = t.position
                return

    def move(self, delta):
        new_pos = [0] * 3
        for v in self.__actors:
            vtkMath.Add(self.drag_pos, delta, new_pos)
            v.SetPosition(new_pos)

        for t in self.__targets:
            vtkMath.Add(self.targets_pos[t], delta, new_pos)
            t.position = new_pos

    def w_scene_camera_updated(self, scene, *args, **kwargs):
        size = self.__actors[0].GetXRange()
        apos = self.__actors[0].GetPosition()
        self.renderer.SetWorldPoint(*apos, 1)
        self.renderer.WorldToView()
        pt = (vtk_mutable(0),vtk_mutable(0))
        pt = self.renderer.GetViewPoint()
        pos = (pt[0] + 0.2, pt[1], pt[2])
        self.renderer.SetViewPoint(*pos)
        self.renderer.ViewToWorld()
        zpos = self.renderer.GetWorldPoint()
        scale = math.sqrt(vtkMath.Distance2BetweenPoints(apos, zpos[:3]))
        for v in self.__actors:
            v.SetScale(scale, scale, scale)

    def w_scene_object_selection_state(self, scene, obj, enabled):
        if enabled:
            if getattr(obj, 'movable', False):
                self.__targets.append(obj)
        else:
            try:
                self.__targets.remove(obj)
            except ValueError:
                pass

        if self.__targets:
            pos = self.__targets[0].position
            for v in self.__actors:
                v.SetPosition(pos)
                v.VisibilityOn()
        else:
            for v in self.__actors:
                v.VisibilityOff()

    def w_property_changed(self, obj, name, value):
        if self.__targets and self.__targets[0] == obj and name == 'position':
            for v in self.__actors:
                v.SetPosition(value)

    def mouse_release(self, btn, x, y, modifiers):
        self.scene.pop_interactor()

    def mouse_move(self, x, y, modifiers):
        self.renderer.SetWorldPoint(*self.drag_pos, 1.0)
        self.renderer.WorldToDisplay()
        display_pt = self.renderer.GetDisplayPoint()
        display_pt = (display_pt[0] + x - self.drag_point[0],
                display_pt[1] + y - self.drag_point[1])


        plane = vtkPlane()
        plane.SetOrigin(self.drag_pos)

        axis_vector = [0, 0, 0]
        axis_vector[self.drag_axis] = 1

        overlay_cam = self.renderer.GetActiveCamera()
        cam_up = overlay_cam.GetViewUp()
        cam_pos = overlay_cam.GetPosition()
        cam_vec = [0] * 3
        vtkMath.Subtract(cam_pos, self.drag_pos, cam_vec)
        plane_normal = [0] * 3
        vtkMath.Cross(axis_vector, cam_vec, plane_normal)
        vtkMath.Cross(axis_vector, plane_normal, plane_normal)
        plane.SetNormal(plane_normal)

        world_pt = [0]*3
        world_orient = [0]*9

        pp = vtkBoundedPlanePointPlacer()
        pp.SetProjectionNormalToOblique()
        pp.SetObliquePlane(plane)

        pp.ComputeWorldPosition(
                self.renderer,
                display_pt,
                world_pt,
                world_orient
            )

        new_pos = self.drag_pos[:]
        new_pos[self.drag_axis] = world_pt[self.drag_axis]
        pos_delta = [0] * 3
        vtkMath.Subtract(new_pos, self.drag_pos, pos_delta)
        self.move(pos_delta)
