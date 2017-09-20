from vtk import vtkCommand
from vtk import vtkGenericRenderWindowInteractor
from vtk import vtkMath
from vtk import vtkInteractorStyleSwitch

from dice_tools import wizard
import math

class BasicInteractor:

    NoModifier = 0x00000000
    ShiftModifier = 0x02000000
    ControlModifier = 0x04000000
    AltModifier = 0x08000000
    MetaModifier = 0x10000000
    KeypadModifier = 0x20000000
    GroupSwitchModifier = 0x40000000

    LeftButton = 0x00000001
    RightButton = 0x00000002
    MidButton = 0x00000004

    def enable(self):
        pass

    def disable(self):
        pass

    def set_size(self, size_x, size_y):
        pass

    def mouse_press(self, btn, x, y, modifiers):
        pass

    def mouse_release(self, btn, x, y, modifiers):
        pass

    def mouse_move(self, x, y, modifiers):
        pass

    def key_press(self, key, x, y, modifiers):
        pass

    def key_release(self, key, x, y, modifiers):
        pass

    def wheel(self, delta_x, delta_y, x, y, modifiers):
        pass


class Interactor(vtkGenericRenderWindowInteractor, BasicInteractor):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.renderer = scene.renderer
        self.overlay = scene.overlay

        self.style = vtkInteractorStyleSwitch()
        self.style.SetCurrentStyleToTrackballCamera()
        self.style.GetCurrentStyle().SetMotionFactor(20)
        self.SetEnableRender(False)
        self.SetRenderWindow(scene.render_window)
        self.SetInteractorStyle(self.style)

        self.picker = self.GetPicker()
        self.ex, self.ey = (-1, -1)
        self.pick = 0

        self.AddObserver(vtkCommand.RenderEvent, self.render)

    def render(self, obj, ev):
        self.scene.render(False)

    def enable(self):
        self.SetSize(self.scene.render_window.GetSize())
        self.Enable()

    def set_size(self, x, y):
        self.SetSize(x, y)

    def disable(self):
        self.Disable()

    def InvokeEvent(self, evt):
        if self.GetEnabled():
            vtkGenericRenderWindowInteractor.InvokeEvent(self, evt)

    def mouse_press(self, btn, x, y, modifiers):
        self.SetEventInformation(x, y,
                                 modifiers & self.ControlModifier,
                                 modifiers & self.ShiftModifier)
        self.SetAltKey(modifiers & self.AltModifier)

        if btn == self.LeftButton:
            self.ex, self.ey = self.GetEventPosition()
            ex, ey = self.GetEventPosition()
            self.scene.render_window.activate()
            result = self.picker.Pick(float(ex), float(ey), 0.0, self.overlay)
            if result == 0:
                result = self.picker.Pick(float(ex), float(ey), 0.0, self.renderer)

            if result != 0:
                actor = self.picker.GetActor()
                wizard.w_scene_actor_pressed(actor, ex, ey,
                    control_modifier = modifiers & self.ControlModifier == 0)

            self.InvokeEvent(vtkCommand.LeftButtonPressEvent)
        elif btn == self.RightButton:
            self.InvokeEvent(vtkCommand.RightButtonPressEvent)
        elif btn == self.MidButton:
            self.InvokeEvent(vtkCommand.MiddleButtonPressEvent)

    def mouse_release(self, btn, x, y, modifiers):
        self.SetEventInformation(x, y,
                                 modifiers & self.ControlModifier,
                                 modifiers & self.ShiftModifier)
        self.SetAltKey(modifiers & self.AltModifier)

        if btn == self.LeftButton:
            ex, ey = self.GetEventPosition()
            delta = vtkMath.Distance2BetweenPoints(
                (self.ex, self.ey, 0), (ex, ey, 0))
            if delta < 5:
                self.scene.render_window.activate()
                result = self.picker.Pick(float(ex), float(ey), 0.0, self.overlay)
                if result == 0:
                    result = self.picker.Pick(float(ex), float(ey), 0.0, self.renderer)

                if result == 0:
                    wizard.w_scene_actor_clicked(None, ex, ey,
                        control_modifier = modifiers & self.ControlModifier == 0)
                    wizard.w_geometry_object_clicked(None,
                        control_modifier = modifiers & self.ControlModifier == 0)
                else:
                    actor = self.picker.GetActor()
                    wizard.w_scene_actor_clicked(actor, ex, ey,
                        control_modifier = modifiers & self.ControlModifier == 0)
                    geometry_object = getattr(actor, 'geometry_object', None)
                    if geometry_object:
                        wizard.w_geometry_object_clicked(geometry_object,
                            control_modifier = modifiers & self.ControlModifier == 0)

            self.InvokeEvent(vtkCommand.LeftButtonReleaseEvent)
        elif btn == self.RightButton:
            self.InvokeEvent(vtkCommand.RightButtonReleaseEvent)
        elif btn == self.MidButton:
            self.InvokeEvent(vtkCommand.MiddleButtonReleaseEvent)

    def mouse_move(self, x, y, modifiers):
        self.SetEventInformation(x, y,
                                      modifiers & self.ControlModifier,
                                      modifiers & self.ShiftModifier)
        self.SetAltKey(modifiers & self.AltModifier)
        self.InvokeEvent(vtkCommand.MouseMoveEvent)

    def key_press(self, key, x, y, modifiers):
        self.SetEventInformation(x, y,
                                 ctrl=(modifiers & self.ControlModifier),
                                 shift=(modifiers & self.ShiftModifier),
                                 keycode=chr(key)
                                 )
        self.SetAltKey(modifiers & self.AltModifier)
        self.InvokeEvent(vtkCommand.KeyPressEvent)
        self.InvokeEvent(vtkCommand.CharEvent)

    def key_release(self, key, x, y, modifiers):
        self.SetEventInformation(x, y,
                                 modifiers & self.ControlModifier,
                                 modifiers & self.ShiftModifier,
                                 chr(key))
        self.SetAltKey(modifiers & self.AltModifier)
        self.InvokeEvent(vtkCommand.KeyReleaseEvent)

    def wheel(self, delta_x, delta_y, x, y, modifiers):
        self.SetEventInformation(x, y,
                                 modifiers & self.ControlModifier,
                                 modifiers & self.ShiftModifier)
        self.SetAltKey(modifiers & self.AltModifier)
        if delta_y > 0:
            self.InvokeEvent(vtkCommand.MouseWheelForwardEvent)
        else:
            self.InvokeEvent(vtkCommand.MouseWheelBackwardEvent)
