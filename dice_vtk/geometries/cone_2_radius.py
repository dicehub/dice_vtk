# External modules
# ================
from vtk import vtkParametricSpline, \
    vtkPolyDataMapper, \
    vtkActor, \
    vtkPoints, \
    vtkDoubleArray, \
    vtkParametricFunctionSource, \
    vtkTubeFilter, \
    vtkTupleInterpolator

# DICE modules
# ============
from .simple_geometry import SimpleGeometry

class Cone2Radius(SimpleGeometry):
    def __init__(self, name='Cone2Radius', **kwargs):
        super().__init__(name=name,
            source=vtkTubeFilter, **kwargs)

        self.radius1 = 0.2
        self.radius2 = 0.1
        point1 = [0, 0, 0]
        point2 = [0, 0, 1]
        points = vtkPoints()
        points.InsertPoint(0, point1[0], point1[1], point1[2])
        points.InsertPoint(1, point2[0], point2[1], point2[2])

        self.spline = vtkParametricSpline()
        self.spline.SetPoints(points)

        self.function = vtkParametricFunctionSource()
        # Interpolate the points
        self.function.SetParametricFunction(self.spline)
        self.function.SetUResolution(2)
        self.function.SetVResolution(2)
        self.function.SetWResolution(2)
        self.function.Update()

        # Interpolate the scalars
        rad = [1]
        self.interpolatedRadius = vtkTupleInterpolator()
        self.interpolatedRadius.SetInterpolationTypeToLinear()
        self.interpolatedRadius.SetNumberOfComponents(1)
        rad[0] = self.radius1
        self.interpolatedRadius.AddTuple(0, rad)
        rad[0] = self.radius2
        self.interpolatedRadius.AddTuple(1, rad)

        # Generate the radius scalars
        self.tubeRadius = vtkDoubleArray()
        self.tubeRadius.SetName("TubeRadius")
        n = self.function.GetOutput().GetNumberOfPoints()
        self.tubeRadius.SetNumberOfTuples(n)
        t_min = self.interpolatedRadius.GetMinimumT()
        t_max = self.interpolatedRadius.GetMaximumT()
        r = [0]
        for i in range(n):
            t = (t_max - t_min)/(n - 1)*i + t_min
            self.interpolatedRadius.InterpolateTuple(t, r)
            self.tubeRadius.SetTuple1(i, r[0])

        self.polyData = self.function.GetOutput()
        self.polyData.GetPointData().AddArray(self.tubeRadius)
        self.polyData.GetPointData().SetActiveScalars("TubeRadius")

        # Create a tube (cylinder) around the line
        self.source.SetInputData(self.polyData)
        self.source.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
        self.source.SetRadius(.025)
        self.source.SetNumberOfSides(50)
        self.source.SetCapping(1)
        self.source.Update()

        self.mapper.ScalarVisibilityOff()
        self.actor.GetProperty().SetOpacity(0.5)
