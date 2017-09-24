# External modules
# ================
from vtk import vtkPolyDataMapper, \
    vtkActor, \
    vtkPoints, \
    vtkCellArray, \
    vtkPolyData, \
    vtkDoubleArray, \
    vtkMath, \
    vtkUnsignedCharArray, \
    vtkTubeFilter

# Python modules
# ==============
import math

# DICE modules
# ============
from .simple_geometry import SimpleGeometry


class Tubes(SimpleGeometry):
    def __init__(self, name='Tubes', **kwargs):
        super().__init__(name=name,
            source=vtkTubeFilter, **kwargs)

        # Setup
        # =====

        self.tube_radius = vtkDoubleArray()
        self.poly_data = vtkPolyData()

        self.num_vertices = 256         # No. of vertices
        self.num_cycles = 5             # No. of spiral cycles
        self.start_tube_radius = 0.5
        self.end_tube_radius = 0.5      # Start/end tube radii
        self.spiral_radius = 2          # Spiral radius
        self.height = 10                # Height
        self.num_surf_elem = 8          # No. of surface elements for each tube vertex

        vtk_pi = vtkMath().Pi()

        # Create points and cells for the spiral
        points = vtkPoints()
        for i in range(self.num_vertices):
            # Spiral coordinates
            vx = self.spiral_radius * math.cos(2 * math.pi * self.num_cycles * i / (self.num_vertices - 1))
            vy = self.spiral_radius * math.sin(2 * math.pi * self.num_cycles * i / (self.num_vertices - 1))
            vz = self.height * i / self.num_vertices
            points.InsertPoint(i, vx, vy, vz)

        lines = vtkCellArray()
        lines.InsertNextCell(self.num_vertices)
        for i in range(self.num_vertices):
            lines.InsertCellPoint(i)

        self.poly_data.SetPoints(points)
        self.poly_data.SetLines(lines)

        # Varying tube radius using sine-function
        self.tube_radius.SetName("TubeRadius")
        self.tube_radius.SetNumberOfTuples(self.num_vertices)
        for i in range(self.num_vertices):
            self.tube_radius.SetTuple1(i,
                                       self.start_tube_radius +
                                       (self.end_tube_radius - self.start_tube_radius) *
                                       math.sin(vtk_pi*i/(self.num_vertices - 1)))
        self.poly_data.GetPointData().AddArray(self.tube_radius)
        self.poly_data.GetPointData().SetActiveScalars("TubeRadius")

        # RBG array (could add Alpha channel too I guess...)
        # Varying from blue to red
        colors = vtkUnsignedCharArray()
        colors.SetName("Colors")
        colors.SetNumberOfComponents(3)
        colors.SetNumberOfTuples(self.num_vertices)
        for i in range(self.num_vertices):
            colors.InsertTuple3(i,
                                int(255 * i/(self.num_vertices - 1)),
                                0,
                                int(255 * (self.num_vertices - 1 - i)/(self.num_vertices - 1)))

        self.poly_data.GetPointData().AddArray(colors)

        self.source.SetInputData(self.poly_data)
        self.source.SetNumberOfSides(self.num_surf_elem)
        self.source.SetVaryRadiusToVaryRadiusByAbsoluteScalar()

        self.mapper.ScalarVisibilityOn()
        self.mapper.SetScalarModeToUsePointFieldData()


