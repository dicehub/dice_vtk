from .geometry_base import VisObject
import vtk


class ScalarBarWidgetInstance:

    def __init__(self, scene, actor):
        self.widget = vtk.vtkScalarBarWidget()
        self.widget.SetInteractor(scene.interactor)
        self.widget.SetScalarBarActor(actor)
        self.widget.GetScalarBarRepresentation().SetPosition(0.05, 0.4)
        self.widget.GetScalarBarRepresentation().SetPosition2(0.1, 0.5)
        self.widget.On()

    def destroy(self):
        self.widget.Off()


class ScalarBarWidget(VisObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instances = {}
        self.__lut = vtk.vtkLookupTable()

        # This creates a blue to red lut.
        # Other lut: https://imagej.nih.gov/ij/download/luts/
        # How to set: https://public.kitware.com/pipermail/vtkusers/2011-April/067138.html
        self.__lut.SetHueRange(0.667, 0.0)
        # self.__lut.SetNumberOfTableValues(256)

        self.__lut.Build()
        self.__scalar_bar = vtk.vtkScalarBarActor()
        self.__scalar_bar.SetOrientationToHorizontal()
        self.__scalar_bar.SetLookupTable(self.__lut)
        self.__scalar_bar.SetTextPositionToSucceedScalarBar()

    @property
    def scalar_bar(self):
        return self.__scalar_bar

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

    @property
    def title(self):
        return self.GetTitle()

    @title.setter
    def title(self, value):
        self.__scalar_bar.SetTitle(value)
