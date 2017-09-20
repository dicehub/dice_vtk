# External modules
# ================
from vtk import vtkPolyData, vtkPoints, vtkCellArray
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from vtk import vtkPolyDataMapper
from vtk import vtkQuadricLODActor
from vtk import vtkAppendPolyData
# DICE modules
# ============
from .simple_geometry import SimpleGeometry

class VtkNumpySTL(SimpleGeometry):

    def __init__(self, data, name='VtkNumpySTL', **kwargs):
        super().__init__(name=name, lod=True, **kwargs)

        self.__verts = data.reshape((-1, 3))
        self.__tris = np.insert(
                np.arange(len(self.__verts)
                    , dtype = 'i8').reshape((-1,3)), 0, 3, axis=1
            ).reshape(-1)

        points = vtkPoints()
        points.SetData(numpy_to_vtk(self.__verts))
        
        cells = vtkCellArray()

        cells.SetCells(int(len(self.__tris) / 4),
            numpy_to_vtkIdTypeArray(self.__tris))

        poly = vtkPolyData()
        poly.SetPoints(points)
        poly.SetPolys(cells)


        self.actor.GetProperty().SetInterpolationToFlat()
        source=vtkAppendPolyData()
        source.AddInputData(poly)
        self.source = source
        