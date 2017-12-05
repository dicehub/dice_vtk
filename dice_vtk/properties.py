# Standard Python modules
# =======================
# from collections import namedtuple

# External modules
# ================

# DICE modules
# ============
from dice_tools import wizard, DICEObject, diceProperty, diceSignal, diceSlot
from dice_tools.helpers.xmodel import modelRole, modelMethod, ModelItem
from dice_tools.helpers.xmodel import standard_model
from dice_vtk.geometries.geometry_base import GeometryBase
from dice_vtk.geometries import ClipWidget, CutterWidget
from vtk import vtkMath


class VtkObject(ModelItem):

    def __init__(self, props, obj, **kwargs):
        super().__init__(**kwargs)
        self.__props = props
        self.__model = self.__props.model
        self.__obj = obj
        wizard.subscribe(self.w_property_changed, obj=obj)
        wizard.subscribe(self.w_geometry_object_clicked, obj=obj)

    def w_geometry_object_clicked(self, obj, *args, **kwargs):
        self.__model.current_item = self

    def w_property_changed(self, obj, name, value):
        wizard.w_model_update_item(self)

    @property
    def obj(self):
        return self.__obj

    @modelRole('name')
    def name(self):
        return self.__obj.name

    @modelRole('isVisible')
    def is_visible(self):
        return self.__obj.visible

    @is_visible.setter
    def is_visible(self, value):
        self.__obj.visible = value

    @modelRole('representation')
    def representation(self):
        return self.__obj.representation

    @modelRole('opacity')
    def opacity(self):
        return self.__obj.opacity

    @modelRole('color')
    def color(self):
        return list(self.__obj.color)

    @modelMethod('zoom')
    def zoom(self):
        wizard.w_reset_camera_to_object([self.obj])

    @modelRole('removable')
    def removable(self):
        return self.__obj in self.__props.widgets

    @modelMethod('remove')
    def remove(self):
        self.__props.remove_widget(self)


class AnimControl(DICEObject):

    def __init__(self, props, **kwargs):
        super().__init__(base_type='QObject', **kwargs)
        self.__widget = None
        self.__props = props
        self.__scene = props.scene
        self.__animation = None
        self.__active = True

    update = diceSignal(name='update')

    @diceProperty('QVariant', notify=update)
    def available(self):
        return self.__animation is not None

    @diceProperty('QVariant', notify=update)
    def active(self):
        return self.__active

    @active.setter
    def active(self, value):
        if self.__active != value:
            self.__active = value
            self.update()

    @property
    def animation(self):
        return self.__animation

    @animation.setter
    def animation(self, value):
        if self.__animation != value:
            if self.__animation:
                wizard.unsubscribe(None, self.on_anim_event, self.__animation)
            self.__animation = value
            if self.__animation:
                wizard.subscribe(None, self.on_anim_event, self.__animation)
            self.update()

    def on_anim_event(self, *args, **kwargs):
        self.update()
        self.__scene.render()
        
    @diceProperty('QVariant', notify=update)
    def playing(self):
        if self.__animation:
            return self.__animation.playing
    
    @diceProperty('QVariant', notify=update)
    def frame(self):
        if self.__animation:
            return self.__animation.frame
        return -1

    @frame.setter
    def frame(self, value):
        if self.__animation:
            self.__animation.set_frame(value)

    @diceProperty('QVariant', notify=update)
    def times(self):
        if self.__animation:
            return self.__animation.times
        return []

    @diceProperty('QVariant', notify=update)
    def loop(self):
        if self.__animation:
            return self.__animation.loop

    @loop.setter
    def loop(self, value):
        if self.__animation:
            self.__animation.loop = value
            self.update()

    @diceSlot(name='play')
    def play(self):
        if self.__animation:
            self.__animation.play()

    @diceSlot(name='stop')
    def stop(self):
        if self.__animation:
            self.__animation.stop()

    @diceSlot(name='backward')
    def backward(self):
        if self.__animation:
            self.__animation.stop()
            frame = max(0, self.__animation.frame-1)
            self.__animation.set_frame(frame)
    
    @diceSlot(name='forward')
    def forward(self):
        if self.__animation:
            self.__animation.stop()
            frame = min(len(self.__animation.times)-1, self.__animation.frame+1)
            self.__animation.set_frame(frame)

    @diceSlot(name='begin')
    def begin(self):
        if self.__animation:
            self.__animation.stop()
            frame = 0
            self.__animation.set_frame(frame)
    
    @diceSlot(name='end')
    def end(self):
        if self.__animation:
            self.__animation.stop()
            frame = len(self.__animation.times)-1
            self.__animation.set_frame(frame)


class PlaneProps(DICEObject):

    def __init__(self, props, **kwargs):
        super().__init__(base_type='QObject', **kwargs)
        self.__widget = None
        self.__props = props
        self.__scene = props.scene
        self.__model = props.model
        wizard.subscribe(self, props.model)

    def w_property_changed(self, obj, name, value):
        self.update()

    def w_model_selection_changed(self, model, selected, deselected):
        if len(self.__model.selection) == 1:
            for v in self.__model.selection:
                if isinstance(v.obj, (ClipWidget, CutterWidget)):
                    self.__widget = v.obj
                    wizard.subscribe(self.w_property_changed, self.__widget)
                    self.update()
                    return
        if self.__widget:
            wizard.unsubscribe(self.w_property_changed, self.__widget)
            self.__widget = None
            self.update()

    update = diceSignal(name='update')

    def set_widget(self, widget):
        self.__widget = widget
        self.update()

    @diceProperty('QVariant', notify=update)
    def active(self):
        return self.__widget is not None

    @diceProperty('QVariantList', notify=update)
    def normal(self):
        if self.__widget:
            return list(self.__widget.plane_normal)
        return [0, 0, 0]

    @normal.setter
    def normal(self, value):
        if self.__widget:
            self.__widget.plane_normal = value
        self.update()

    @diceProperty('QVariantList', notify=update)
    def origin(self):
        if self.__widget:
            return self.__widget.plane_origin
        return [0, 0, 0]

    @origin.setter
    def origin(self, value):
        if self.__widget:
            self.__widget.plane_origin = value
        self.update()

    @diceSlot(name='setNormalX')
    def set_normal_x(self):
        if self.__widget:
            self.__widget.plane_normal = (1, 0, 0)
        self.update()

    @diceSlot(name='setNormalY')
    def set_normal_y(self):
        if self.__widget:
            self.__widget.plane_normal = (0, 1, 0)
        self.update() 

    @diceSlot(name='setNormalZ')
    def set_normal_z(self):
        if self.__widget:
            self.__widget.plane_normal = (0, 0, 1)
        self.update() 

    @diceSlot(name='setNormalCam')
    def set_normal_cam(self):
        if self.__widget:
            camera = self.__scene.renderer.GetActiveCamera()
            direction = camera.GetViewPlaneNormal()
            self.__widget.plane_normal = direction
        self.update() 

    @diceSlot(name='setCamNormal')
    def set_cam_normal(self):
        if self.__widget:
            camera = self.__scene.renderer.GetActiveCamera()
            focal_point = [0, 0, 0]
            vtkMath.Subtract(camera.GetPosition(),
                self.__widget.plane_normal,
                focal_point)
            camera.SetFocalPoint(focal_point)
            self.__scene.renderer.ResetCamera(
                self.__widget.target.get_bounds(self.__scene))
            self.__scene.update_camera()
            self.__scene.render()

    @diceSlot(name='apply')
    def apply(self):
        if self.__widget:
            self.__widget.apply()

    @diceProperty('bool', name='clip', notify=update)
    def clip(self):
        if self.__widget:
            return isinstance(self.__widget, ClipWidget)
        return False

    @diceProperty('bool', name='insideOut', notify=update)
    def inside_out(self):
        if self.__widget and isinstance(self.__widget, ClipWidget):
            return self.__widget.inside_out
        return False

    @inside_out.setter
    def inside_out(self, value):
        if self.__widget and isinstance(self.__widget, ClipWidget):
            self.__widget.inside_out = value
        self.update()

    @diceProperty('bool', notify=update)
    def crinkle(self):
        if self.__widget and isinstance(self.__widget, ClipWidget):
            return self.__widget.crinkle
        return False

    @crinkle.setter
    def crinkle(self, value):
        if self.__widget and isinstance(self.__widget, ClipWidget):
            self.__widget.crinkle = value
        self.update()


class VtkSceneProperties(DICEObject):

    def __init__(self, scene, **kwargs):
        super().__init__(base_type='QObject', **kwargs)
        self.__scene = scene
        self.__model = standard_model(VtkObject)
        self.__widgets = set()
        self.__plane_props = PlaneProps(self)
        self.__anim_control = AnimControl(self)
        wizard.subscribe(self, self.__model)
        wizard.subscribe(self.w_geometry_object_clicked)

    def remove_widget(self, item):
        self.__scene.remove_object(item.obj)

    @diceProperty('QVariant', name='planeProperties')
    def plane_properties(self):
        return self.__plane_props

    @diceProperty('QVariant', name='animationControl')
    def animation_control(self):
        return self.__anim_control

    @property
    def scene(self):
        return self.__scene

    @property
    def widgets(self):
        return self.__widgets

    @property
    def animation(self):
        return self.__anim_control.animation

    @animation.setter
    def animation(self, value):
        self.__anim_control.animation = value
        self.update()

    def w_geometry_object_clicked(self, obj, *args, **kwargs):
        if obj is None:
            self.__model.current_item = None

    def w_model_selection_changed(self, model, selected, deselected):
        for v in deselected:
            v.obj.set_selected(False)
        for v in selected:
            v.obj.set_selected(True)
        self.update()

    def add_object(self, obj):
        if not isinstance(obj, GeometryBase):
            return

        if isinstance(obj, (ClipWidget, CutterWidget)):
            for v in self.model:
                if v.obj == obj.target:
                    v.elements.append(VtkObject(self, obj))
                    if obj in self.__widgets:
                        self.__model.current_item = v.elements[-1]
                    break
        else:
            self.__model.root_elements.append(VtkObject(self, obj))

    def remove_object(self, obj):
        if not isinstance(obj, GeometryBase):
            return

        def clear(item):
            for v in item.elements:
                if v.obj in self.__widgets:
                    self.__scene.remove_object(v.obj)
                    self.__widgets.discard(v.obj)
                    clear(v)
                else:
                    self.__model.root_elements.append(v)

        if isinstance(obj, (ClipWidget, CutterWidget)):
            for v in self.model:
                if v.obj == obj.target:
                    for i, vv in enumerate(v.elements):
                        if vv.obj == obj:
                            del v.elements[i]
                            self.__widgets.discard(obj)
                            clear(vv)
                            break
                    break
        else:
            for i, v in enumerate(self.__model.root_elements):
                if v.obj == obj:
                    del self.__model.root_elements[i]
                    clear(v)
                    break

    update = diceSignal(name='update')

    @diceProperty('QVariant')
    def model(self):
        return self.__model

    @diceProperty('QVariant', notify=update)
    def active(self):
        return len(self.__model.selection)

    @diceProperty('QVariant', name='hasAnimation', notify=update)
    def has_animation(self):
        return self.__anim_control.animation != None

    @diceProperty('QVariant', name='edgeVisible', notify=update)
    def edge_visible(self):
        if self.__model.selection:  
            values = set([bool(v.obj.edge_visible) for v in self.__model.selection])
            if len(values) == 1:
                return values.pop()

    @edge_visible.setter
    def edge_visible(self, value):
        for v in self.__model.selection:
            v.obj.edge_visible = value
        self.update()

    @diceProperty('QVariant', notify=update)
    def representation(self):
        if self.__model.selection:  
            values = set([int(v.obj.representation) for v in self.__model.selection])
            if len(values) == 1:
                return values.pop()
        return -1

    @representation.setter
    def representation(self, value):
        for v in self.__model.selection:
            v.obj.representation = value
        self.update()

    @diceProperty('QVariantList', notify=update)
    def color(self):
        if self.__model.selection:  
            values = set([tuple(v.obj.color) for v in self.__model.selection])
            if len(values) == 1:
                return list(values.pop())
        return [1.0, 1.0, 1.0]

    @color.setter
    def color(self, value):
        for v in self.__model.selection:
            v.obj.color = value
        self.update()

    @diceProperty('QVariant', notify=update)
    def opacity(self):
        if self.__model.selection:  
            values = set([float(v.obj.opacity) for v in self.__model.selection])
            if len(values) == 1:
                return values.pop()
        return 1.0

    @opacity.setter
    def opacity(self, value):
        for v in self.__model.selection:
            v.obj.opacity = value
        self.update()

    @diceSlot()
    def clip(self):
        for v in self.__model.selection:
            widget = ClipWidget(v.obj)
            self.__widgets.add(widget)
            self.__scene.add_object(widget)
            break

    @diceSlot()
    def slice(self):
        for v in self.__model.selection:
            widget = CutterWidget(v.obj)
            self.__widgets.add(widget)
            self.__scene.add_object(widget)
            break

