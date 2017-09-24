from .geometry_base import VisObject
import vtk

class ScalarBarWidgetInstance:

    def __init__(self, scene, actor):
        self.widget = vtk.vtkScalarBarWidget()
        self.widget.SetInteractor(scene.interactor)
        self.widget.SetScalarBarActor(actor)
        self.widget.GetScalarBarRepresentation().SetPosition(0,0.3)
        self.widget.GetScalarBarRepresentation().SetPosition2(0.1,0.5)
        self.widget.On()

    def destroy(self):
        self.widget.Off()

class ScalarBarWidget(VisObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instances = {}
        self.__lut = vtk.vtkLookupTable()
        self.__lut.Build()
        self.__scalar_bar = vtk.vtkScalarBarActor()
        self.__scalar_bar.SetOrientationToHorizontal()
        self.__scalar_bar.SetLookupTable(self.__lut)

    @property
    def lut(self):
        return self.__lut

    def attach(self, scene):
        super().attach(scene)
        self.instances[scene] = ScalarBarWidgetInstance(
            scene, self.__scalar_bar)

    def detach(self, scene):
        super().detach(scene)
        self.instances.pop(scene).destroy()