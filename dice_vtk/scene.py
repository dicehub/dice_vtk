# Standard Python modules
# =======================

# External modules
# ================
from vtk import vtkRenderWindow
from vtk import vtkInteractorStyleSwitch
from vtk import vtkGraphicsFactory
from vtk import vtkRenderer
from vtk import vtkUnsignedCharArray
from vtk import vtkGenericOpenGLRenderWindow
from vtk import vtkBoundingBox
from vtk import vtkLight
# DICE modules
# ============
from dice_tools import wizard, diceProperty, diceSlot
from dice_tools import DICEObject, diceCall
from dice_vtk.properties import VtkSceneProperties
from dice_vtk.interactor import Interactor
from dice_vtk.geometries import TransformGismo
from dice_vtk.geometries import AxesWidget

import lz4
import os
from time import time
import mmap
from OpenGL import GL
from tempfile import NamedTemporaryFile
from contextlib import contextmanager
import weakref
import sys

class RenderWindowProxy(vtkGenericOpenGLRenderWindow):

    __render_window = None
    __current_proxy = None

    def __init__(self, scene):
        if not RenderWindowProxy.__render_window:
            RenderWindowProxy.__render_window = vtkRenderWindow()
            RenderWindowProxy.__render_window.SetOffScreenRendering(1)
        self.__scene = scene

    def SetSize(self, sx, sy):
        super().SetSize(sx, sy)
        if ((RenderWindowProxy.__current_proxy is not None) and
                (RenderWindowProxy.__current_proxy() == self)):
            RenderWindowProxy.__render_window.SetSize(sx, sy)

    @staticmethod
    def release(ref):
        if RenderWindowProxy.__current_proxy == ref:
            renderers = RenderWindowProxy.__render_window.GetRenderers()
            renderers.InitTraversal()
            while r:
                RenderWindowProxy.__render_window.RemoveRenderer(r)
                r = renderers.GetNextItem()
            RenderWindowProxy.__current_proxy = None

    def deactivate(self):
        if ((RenderWindowProxy.__current_proxy is not None) and
                (RenderWindowProxy.__current_proxy() == self)):
            interactor = self.GetInteractor()
            interactor.SetRenderWindow(self)
            renderers = RenderWindowProxy.__render_window.GetRenderers()
            renderers.InitTraversal()
            r = renderers.GetNextItem()
            while r:
                RenderWindowProxy.__render_window.RemoveRenderer(r)
                self.AddRenderer(r)
                r = renderers.GetNextItem()
            RenderWindowProxy.__current_proxy = None

    def activate(self):
        if RenderWindowProxy.__current_proxy is not None:
            proxy = RenderWindowProxy.__current_proxy()
            if proxy == self:
                return
            proxy.deactivate()
        RenderWindowProxy.__current_proxy = weakref.ref(self, self.release)
        RenderWindowProxy.__render_window.SetSize(self.GetSize())
        renderers = self.GetRenderers()
        renderers.InitTraversal()
        r = renderers.GetNextItem()
        while r:
            self.RemoveRenderer(r)
            RenderWindowProxy.__render_window.AddRenderer(r)
            r = renderers.GetNextItem()
        RenderWindowProxy.__render_window.SetNumberOfLayers(self.GetNumberOfLayers())
        interactor = self.GetInteractor()
        interactor.SetRenderWindow(RenderWindowProxy.__render_window)


    def Render(self):
        self.activate()
        RenderWindowProxy.__render_window.Render()
        while GL.glGetError():
            pass
        size = RenderWindowProxy.__render_window.GetSize()
        buffer = GL.glReadPixels(0, 0, size[0], size[1], GL.GL_RGBA, 
                             GL.GL_UNSIGNED_BYTE)
        self.__scene.updated(size, buffer)


class VtkScene(DICEObject):
    """
    Implements interactive 3D scene with own render, camera and interactor.
    Uses `VTK <http://vtk.org>`_ to do the staff.
    """
    __render_window = None

    def __init__(self, size_x=1, size_y=1, **kwargs):
        super().__init__(base_type='ExposedView', **kwargs)
        self.__size_x = size_x
        self.__size_y = size_y

        self.frame = None

        # if 'win' in sys.platform:
        #     import uuid
        #     uid = str(uuid.uuid4())
        #     if self.mmap(uid):
        #         self.frame = mmap.mmap(-1, 1, uid)
        # else:
        #     with NamedTemporaryFile(buffering=0) as f:
        #         f.write(b'\x00')
        #         if self.mmap(f.name):
        #             self.frame = mmap.mmap(f.fileno(), 0)

        self.renderer = vtkRenderer()

        self.overlay = vtkRenderer()
        self.overlay.SetLayer(1)
        self.overlay.InteractiveOff()

        self.render_window = RenderWindowProxy(self)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(size_x, size_y)
        self.render_window.AddRenderer(self.overlay)
        self.render_window.SetNumberOfLayers(2)

        self.interactor = Interactor(self)
        self.transform_gismo = TransformGismo(self)
        self.interactor.Enable()
        self.interactors = [self.interactor]

        self.__objects = []
        self.__render_deferred = False
        self.selection = set()
        self.__name = 'Unnamed'
        self.__active = True
        self.__properties = VtkSceneProperties(self)
        wizard.w_vtk_scene_created(self)
        wizard.subscribe(self.w_reset_camera_to_object)
        wizard.subscribe(self.w_property_changed)
        self.__axes = AxesWidget()
        self.add_object(self.__axes)

    def connect(self):
        super().connect()
        self.render()

    @diceProperty('QVariant')
    def properties(self):
        return self.__properties

    @property
    def animation(self):
        return self.__properties.animation

    @animation.setter
    def animation(self, value):
        self.__properties.animation = value
        
    def w_reset_camera_to_object(self, objs, scale = None):
        if set(self.__objects) & set(objs):
            bbox = vtkBoundingBox()
            for o in objs:
                bbox.AddBounds(o.get_bounds(self))
            bounds = [0]*6
            bbox.GetBounds(bounds)
            if scale is not None:
                for i in range(0, 6, 2):
                    ext = (bounds[i+1] - bounds[i]) * (scale - 1) / 2
                    bounds[i] -= ext
                    bounds[i+1] += ext
            self.renderer.ResetCamera(bounds)
            # self.update_camera()
            self.render()

    def push_interactor(self, interactor):
        self.interactors[-1].disable()
        self.interactors.append(interactor)
        interactor.enable()

    def pop_interactor(self):
        self.interactors.pop().disable()
        self.interactors[-1].enable()

    @diceProperty('QString', name='sceneName')
    def scene_name(self):
        return self.__name

    @scene_name.setter
    def scene_name(self, name):
        if name != self.__name:
            self.__name = name
    @property
    def size(self):
        return set(self.__size_x, self.__size_y)

    @property
    def objects(self):
        return self.__objects

    def delete(self):
        self.clear()
        wizard.unsubscribe(self)
        super().delete()

    def clear(self):
        """
        Removes all geometry object from scene.
        """
        while self.__objects:
            obj = self.__objects.pop()
            obj.detach(self)
            self.__properties.remove_object(obj)
        self.render()
        
    def w_property_changed(self, obj, name, value):
        if obj in self.__objects:
            self.renderer.ResetCameraClippingRange()
            self.render(True)

    def updated(self, size, data):
        if self.frame is not None:
            if len(self.frame) != size[0]*size[1]*4:
                self.frame.resize(size[0]*size[1]*4)
            self.frame[:] = data
            self._update(size[0], size[1], True)
        else:
            b = bytes(data)
            data = lz4.block.compress(b)
            self._update(size[0], size[1], True, data)

    @diceCall
    def _update(self, sx, sy, flip, data):
        pass

    def size_changed(self, size_x, size_y):
        """
        Size changed event handler.

        :param size_x: New size x dimension.
        :param size_y: New size y dimension.
        """
        size_x = max(1, size_x)
        size_y = max(1, size_y)
        self.__size_x = size_x
        self.__size_y = size_y
        self.interactors[-1].set_size(size_x, size_y)
        self.render_window.SetSize(size_x, size_y)
        # self.update_camera()
        self.render()

    def w_geometry_object_selection_state(self, obj, enabled):
        if enabled:
            self.selection.add(obj)
        else:
            self.selection.discard(obj)
        wizard.w_scene_object_selection_state(self, obj, enabled)
        self.render()

    '''
    Mouse Events
    ============
    '''
    def mouse_press(self, btn, x, y, modifiers):
        """
        Mouse button press event handler.

        :param btn: Mouse button code.
        :param x: X coordinate of position where mouse pressed.
        :param y: Y coordinate of position where mouse pressed.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """

        y = self.__size_y - y
        self.interactors[-1].mouse_press(btn, x, y, modifiers)
        # self.render(False)


    def mouse_release(self, btn, x, y, modifiers):
        """
        Mouse button release event handler.

        :param btn: Mouse button code.
        :param x: X coordinate of position where mouse pressed.
        :param y: Y coordinate of position where mouse pressed.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """

        y = self.__size_y - y
        self.interactors[-1].mouse_release(btn, x, y, modifiers)
        # self.render(False)

    def mouse_move(self, x, y, modifiers):
        """
        Mouse move event handler.

        :param x: X coordinate of position mouse moved to.
        :param y: Y coordinate of position mouse moved to.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """
        y = self.__size_y - y
        self.interactors[-1].mouse_move(x, y, modifiers)
        # self.update_camera()
        # self.render(False, True)

    def mouse_wheel(self, delta_x, delta_y, x, y, modifiers):
        """
        Mouse wheel event handler.

        :param delta_x: Unused.
        :param delta_y: Mouse wheel turn offset.
        :param x: X coordinate of position where mouse wheel was turned.
        :param y: Y coordinate of position where mouse wheel was turned.
        :param modifiers: Keyboard modifiers, i.e. 'Alt', 'Control', 'Shift'.
        """

        y = self.__size_y - y
        self.interactors[-1].wheel(delta_x, delta_y, x, y, modifiers)
        # self.update_camera()
        # self.render(False)

    @diceProperty("bool")
    def active(self):
        return self.__active

    @active.setter
    def active(self, value):
        if value != self.__active:
            self.__active = value
            if value and self.__render_deferred:
                self.render(False)

    def __deferred_render(self):
        if self.__render_deferred:
            self.render(False)

    def render(self, deferred=True):
        """
        Starts scene rendering.

        :param deferred: When True rendering wil be started next tick.
        """

        if deferred:
            if not self.__render_deferred:
                self.__render_deferred = True
                if self.__active:
                    wizard.timeout(self.__deferred_render, 0)  # render next tick
        elif self.__active:
            self.__render_deferred = False
            self.update_camera()
            self.render_window.Render()

    def add_object(self, obj, reset_camera=True):
        """
        Adds geometry object to scene.

        :param obj: Geometry object.
        """
        if obj not in self.objects:
            self.__objects.append(obj)
            wizard.subscribe(self, obj)
            obj.attach(self)
            self.__properties.add_object(obj)
            wizard.w_scene_object_added(self, obj)
            if reset_camera:
                self.reset_camera()
            else:
                self.render()

    def remove_object(self, obj):
        """
        Removes geometry object from scene.

        :param obj: Geometry object.
        """
        if obj in self.objects:
            self.__objects.remove(obj)
            self.selection.discard(obj)
            wizard.unsubscribe(self, obj)
            obj.detach(self)
            self.__properties.remove_object(obj)
            wizard.w_scene_object_removed(self, obj)
            self.render()

    @diceSlot(name='resetCamera')
    def reset_camera(self):
        """
        Automatically set up the camera based on the visible actors. The camera
        will reposition itself to view the center point of the actors, and move
        along its initial view plane normal (i.e., vector defined from camera
        position to focal point) so that all of the actors can be seen.
        """
        self.renderer.ResetCamera()
        # self.update_camera()
        self.render()


    def update_camera(self):
        self.renderer.ResetCameraClippingRange()
        camera = self.renderer.GetActiveCamera()
        clipping_range = camera.GetClippingRange()
        focal_point = camera.GetFocalPoint()
        position = camera.GetPosition()
        roll = camera.GetRoll()
        view = camera.GetViewUp()

        overlay_cam = self.overlay.GetActiveCamera()
        overlay_cam.SetFocalPoint(focal_point)
        overlay_cam.SetPosition(position)
        overlay_cam.SetRoll(roll)
        self.overlay.ResetCameraClippingRange()

        wizard.w_scene_camera_updated(self,
                                      clipping_range=clipping_range,
                                      focal_point=focal_point,
                                      position=position,
                                      view=view,
                                      roll=roll)

    def get_camera_params(self, camera=None):
        """
        Returns dict with camera parameters values. Keys are 'clipping_range',
        'focal_point', 'position', 'view', 'roll'.
        'clipping_range' is the location of the near and far clipping planes
        along the direction of projection. Both of these values must be
        positive. How the clipping planes are set can have a large impact on
        how well z-buffering works. In particular the front clipping plane can
        make a very big difference. Setting it to 0.01 when it really could be
        1.0 can have a big impact on your z-buffer resolution farther away.
        The default clipping range is (0.1,1000). Clipping distance is measured
        in world coordinate unless a scale factor exists in camera's
        ModelTransformMatrix.

        'focal_point' is the focal of the camera in world coordinates. The
        default focal point is the origin.

        'position' is the position of the camera in world coordinates. The
        default position is (0,0,1).

        'view' is the view up direction for the camera. The default is (0,1,0).

        'roll' is the roll angle of the camera about the direction of
        projection.

        :param camera: The vtkCamera object to get parameters from. If is None
        current camera of renderer is used.

        :return: dict
        """

        camera = self.renderer.GetActiveCamera()
        return dict(
                clipping_range = camera.GetClippingRange(),
                focal_point = camera.GetFocalPoint(),
                position = camera.GetPosition(),
                view = camera.GetViewUp(),
                roll = camera.GetRoll()
            )

    def set_camera_params(self, camera=None,
                          clipping_range=(0.01, 1000.01),
                          focal_point=(0., 0., 0.),
                          position=(0., 0., 1.),
                          roll=0.,
                          view=(0., 0., 1.)):
        """
        Changes camera parameters to given.

        :param camera: The vtkCamera object to get parameters from. If is None
        current camera of renderer is used.

        :param clipping_range: Location of the near and far clipping planes
        along the direction of projection. Both of these values must be
        positive. How the clipping planes are set can have a large impact on
        how well z-buffering works. In particular the front clipping plane can
        make a very big difference. Setting it to 0.01 when it really could be
        1.0 can have a big impact on your z-buffer resolution farther away.
        Clipping distance is measured in world coordinate unless a scale factor
        exists in camera's ModelTransformMatrix.

        :param focal_point: The focal of the camera in world coordinates. The
        default focal point is the origin.

        :param position: The position of the camera in world coordinates.

        :param roll: The roll angle of the camera about the direction of
        projection.

        :param view: The view up direction for the camera. The default is
        (0,1,0).
        """

        camera = self.renderer.GetActiveCamera()
        camera.SetClippingRange(clipping_range)
        camera.SetFocalPoint(focal_point)
        camera.SetPosition(position)
        camera.SetRoll(roll)
        camera.SetViewUp(view)
        self.render()
