from vtk import vtkActor
from vtk import vtkPolyDataMapper
from vtk import vtkPlaneSource
from vtk import vtkBoxWidget
from vtk import vtkPlanes
from vtk import vtkTransform
from vtk import vtkSphereSource
from vtk import vtkCoordinate
from vtk import vtkMath
from vtk import vtkPlane
from vtk import mutable as vtk_mutable
from vtk import vtkBoundedPlanePointPlacer
import math
# DICE modules
# ============
from .geometry_base import GeometryBase, GeometryProperty
from ..interactor import BasicInteractor
from dice_tools import wizard
from itertools import chain

class WidgetInstance(BasicInteractor):
    def __init__(self, parent, scene):
        self.parent = parent
        self.scene = scene
        self.renderer = scene.renderer

        self.__handles = []
        for v in range(6):
            source = vtkSphereSource()
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(source.GetOutputPort())
            actor = vtkActor()
            actor.SetMapper(mapper)
            self.__handles.append(actor)
            scene.renderer.AddActor(actor)
            wizard.subscribe(self, actor)
        self.update()
        wizard.subscribe(self, scene)

    def update(self):
        for i in range(6):
            pos = [0, 0, 0]
            for j in range(3):
                if (i == j) or (i == (j + 3)):
                    pos[j] = self.parent.minmax[i]
                else:
                    pos[j] = (self.parent.minmax[j+3] + self.parent.minmax[j]) / 2
            self.__handles[i].SetPosition(pos)
            if i in self.parent.selected_faces:
                self.__handles[i].GetProperty().SetColor(1, 0, 0)
            else:
                self.__handles[i].GetProperty().SetColor(1, 1, 1)
            self.__handles[i].SetVisibility(self.parent.visible)

    def destroy(self, scene):
        pass

    def w_scene_actor_clicked(self, actor, x, y, control_modifier):
        for i, v in enumerate(self.__handles):
            if v == actor:        
                self.parent.selected_faces = [i]
                wizard.w_multipatchbox_face_clicked(self.parent, i)

    def w_scene_actor_pressed(self, actor, x, y, control_modifier):
        for i, v in enumerate(self.__handles):
            if v == actor and i in self.parent.selected_faces:        
                self.drag_axis = i
                self.drag_pos = actor.GetPosition()
                self.drag_point = (x, y)
                self.scene.push_interactor(self)
                return

    def w_scene_camera_updated(self, scene, *args, **kwargs):
        for i, handle in enumerate(self.__handles):
            size = handle.GetXRange()
            apos = handle.GetPosition()
            self.renderer.SetWorldPoint(*apos, 1)
            self.renderer.WorldToView()
            pt = self.renderer.GetViewPoint()
            pos = (pt[0] + 0.05, pt[1], pt[2])
            self.renderer.SetViewPoint(*pos)
            self.renderer.ViewToWorld()
            zpos = self.renderer.GetWorldPoint()
            scale = math.sqrt(vtkMath.Distance2BetweenPoints(apos, zpos[:3]))

            dist = min((self.parent.max[j] - self.parent.min[j] for j in range(3)
                   if (i != j) and (i != (j + 3))))

            scale = min(scale, dist/3.0)
            handle.SetScale(scale, scale, scale)

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
        axis_vector[self.drag_axis%3] = 1

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
        minmax = self.parent.minmax[:]
        value = world_pt[self.drag_axis%3]
        if self.drag_axis < 3 and value > minmax[self.drag_axis + 3]:
            self.drag_axis = self.drag_axis + 3
        elif self.drag_axis >= 3 and value < minmax[self.drag_axis - 3]:
            self.drag_axis = self.drag_axis - 3
        minmax[self.drag_axis] = value
        self.parent.minmax = minmax

class MultiPatchBox(GeometryBase):
    # 0     1     2     3     4     5
    # xmin, ymin, zmin, xmax, ymax, zmax

    build_data = (
            ((0, 3), (0, 4, 2), (0, 1, 5), 1, 2),
            ((0, 3), (0, 1, 5), (3, 1, 2), 2, 0),
            ((0, 3), (0, 4, 2), (3, 1, 2), 1, 0),
            ((3, 6), (3, 1, 5), (3, 4, 2), 1, 2),
            ((3, 6), (0, 4, 5), (3, 4, 2), 0, 2),
            ((3, 6), (0, 4, 5), (3, 1, 5), 0, 1),
        )

    def __init__(self, name='MultiPatchBox', **props):
        GeometryBase.__init__(self, name=name, **props)

        self.widgets = {}
        self.__minmax = [-0.5, -0.5, -0.5, 0.5, 0.5, 0.5]
        self.__resolution = [1, 1, 1]
        self.__planes = []
        self.__actors = []
        self.__selected_faces = []

        for v in range(6):
            source = vtkPlaneSource()
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(source.GetOutputPort())
            actor = vtkActor()
            actor.SetMapper(mapper)
            self.__planes.append(source)
            actor.GetProperty().SetEdgeColor(1, 1, 1)
            actor.PickableOff()
            self.__actors.append(actor)
        
        self.visible = True
        self.edge_visible = True
        self.opacity = 0.5
        self.representation = 2
        self.color = [0, 0, 0.6]

        self.__rebuild()
        self.active_widget = None
        wizard.subscribe(self.w_scene_actor_clicked, actor=None)

    def get_bounds(self, scene):
        return list(chain(*zip(self.min, self.max)))

    def get_sources(self):
        return self.__planes

    def get_actors(self):
        return self.__actors

    def get_color(self):
        return self.__color

    def set_color(self, value):
        self.__color = value
        for i, a in enumerate(self.__actors):
            if i not in self.__selected_faces:
                a.GetProperty().SetColor(value)

    @GeometryProperty
    def opacity(self):
        return self.__opacity

    @opacity.setter
    def opacity(self, value):
        self.__opacity = value
        for a in self.__actors:
            a.GetProperty().SetOpacity(value)

    def w_scene_actor_clicked(self, actor, *args, **kwargs):
        self.selected_faces = []

    def attach(self, scene):
        for a in self.__actors:
            scene.renderer.AddActor(a)
        self.widgets[scene] = WidgetInstance(self, scene)

    def detach(self, scene):
        for a in self.__actors:
            scene.renderer.RemoveActor(a)
        widget = self.widgets.pop(scene)
        widget.destroy(scene)

    def widget_callback(self, widget, event):
        planes = vtkPlanes()
        widget.GetPlanes(planes)

        points = planes.GetPoints()
        points_list = []
        for i in range(points.GetNumberOfPoints()):
            point = points.GetPoint(i)
            points_list.append(point)

        p_min = list(map(min, zip(*points_list)))
        p_max = list(map(max, zip(*points_list)))

        self.active_widget = widget
        self.minmax = p_min + p_max
        self.active_widget = None

    def __rebuild(self):
        for i in range(6):
            plane = self.__planes[i]
            o, p1, p2, r1, r2 = self.build_data[i]

            plane.SetOrigin(self.__minmax[o[0]:o[1]])
            plane.SetPoint1(self.__minmax[p1[0]], self.__minmax[p1[1]], self.__minmax[p1[2]])
            plane.SetPoint2(self.__minmax[p2[0]], self.__minmax[p2[1]], self.__minmax[p2[2]])
            plane.SetResolution(self.__resolution[r1], self.__resolution[r2])
        
        for v in self.widgets.values():
            v.update()

    @GeometryProperty('int')
    def selected_faces(self):
        return self.__selected_faces

    @selected_faces.setter
    def selected_faces(self, value):
        self.__selected_faces = value
        for i, v in enumerate(self.__actors):
            if i in self.__selected_faces:
                v.GetProperty().SetColor(1, 0, 0)
            else:
                v.GetProperty().SetColor(self.__color)
        for v in self.widgets.values():
            v.update()

    @GeometryProperty
    def representation(self):
        return self.__representation

    @representation.setter
    def representation(self, value):
        self.__representation = value
        for a in self.__actors:
            a.GetProperty().SetRepresentation(value)

    @GeometryProperty
    def position(self):
        return [(v[0]+v[1])/2.0 for v in zip(self.min, self.max)]

    @position.setter
    def position(self, value):
        s = [(v[1]-v[0])/2 for v in zip(self.min, self.max)]
        self.min = [value[i]-s[i] for i in range(3)]
        self.max = [value[i]+s[i] for i in range(3)]

    @GeometryProperty
    def edge_visible(self):
        return self.__edge_visible

    @edge_visible.setter
    def edge_visible(self, value):
        self.__edge_visible = value
        for a in self.__actors:
            a.GetProperty().SetEdgeVisibility(value)

    @GeometryProperty('int')
    def resolution_x(self):
        return self.__resolution[0]

    @resolution_x.setter
    def resolution_x(self, value):
        self.__resolution[0] = value
        self.__rebuild()

    @GeometryProperty('int')
    def resolution_y(self):
        return self.__resolution[1]

    @resolution_y.setter
    def resolution_y(self, value):
        self.__resolution[1] = value
        self.__rebuild()

    @GeometryProperty('int')
    def resolution_z(self):
        return self.__resolution[2]

    @resolution_z.setter
    def resolution_z(self, value):
        self.__resolution[2] = value
        self.__rebuild()

    @GeometryProperty('QVariantList')
    def resolution(self):
        return self.__resolution

    @resolution.setter
    def resolution(self, value):
        self.__resolution = value
        self.__rebuild()

    @GeometryProperty('float')
    def min_x(self):
        return self.__minmax[0]

    @min_x.setter
    def min_x(self, value):
        self.__minmax[0] = value
        self.__rebuild()

    @GeometryProperty('float')
    def min_y(self):
        return self.__minmax[1]

    @min_y.setter
    def min_y(self, value):
        self.__minmax[1] = value
        self.__rebuild()

    @GeometryProperty('float')
    def min_z(self):
        return self.__minmax[2]

    @min_z.setter
    def min_z(self, value):
        self.__minmax[2] = value
        self.__rebuild()                

    @GeometryProperty('float')
    def max_x(self):
        return self.__minmax[3]

    @max_x.setter
    def max_x(self, value):
        self.__minmax[3] = value
        self.__rebuild()

    @GeometryProperty('float')
    def max_y(self):
        return self.__minmax[4]

    @max_y.setter
    def max_y(self, value):
        self.__minmax[4] = value
        self.__rebuild()

    @GeometryProperty('float')
    def max_z(self):
        return self.__minmax[5]

    @max_z.setter
    def max_z(self, value):
        self.__minmax[5] = value
        self.__rebuild()  

    @GeometryProperty('QVariantList')
    def min(self):
        return self.__minmax[:3]

    @min.setter
    def min(self, value):
        self.__minmax[:3] = value
        self.__rebuild()

    @GeometryProperty('QVariantList')
    def max(self):
        return self.__minmax[3:]

    @max.setter
    def max(self, value):
        self.__minmax[3:] = value
        self.__rebuild() 

    @GeometryProperty('QVariantList')
    def minmax(self):
        return self.__minmax

    @minmax.setter
    def minmax(self, value):
        self.__minmax = value
        self.__rebuild() 

    @GeometryProperty('bool')
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value):
        self.__visible = value
        for v in self.__actors:
            v.SetVisibility(value)
        for v in self.widgets.values():
            v.update()