
from vtk import vtkActor
from vtk import vtkPolyDataMapper
from vtk import vtkPlaneSource
from vtk import vtkPOpenFOAMReader
from vtk import vtkDataSetSurfaceFilter
from vtk import vtkQuadricLODActor
# DICE modules
# ============
from .simple_geometry import SimpleGeometry
import os

from vtk import vtkAppendFilter
from vtk import vtkAlgorithm
from vtk import vtkDataObject
from vtk import vtkPythonAlgorithm
from vtk import vtkMultiBlockDataSet
from vtk import vtkDataSet
from vtk import vtkUnstructuredGrid
from ..animation import VtkSceneAnimation
from vtk import vtkExtractBlock
from itertools import chain

class FOAMFilter:

    def __init__(self, foam_mesh, patch_index):
        self.__foam_mesh = foam_mesh
        self.__patch_index = patch_index

    def Initialize(self, vtkself):
        vtkself.SetNumberOfInputPorts(1)
        vtkself.SetNumberOfOutputPorts(1)

    def FillInputPortInformation(self, vtkself, port, info):
        info.Set(vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkMultiBlockDataSet")
        return 1

    def FillOutputPortInformation(self, vtkself, port, info):
        info.Set(vtkDataObject.DATA_TYPE_NAME(), "vtkUnstructuredGrid")
        return 1

    def ProcessRequest(self, vtkself, request, inInfo, outInfo):
        inp = vtkMultiBlockDataSet.GetData(inInfo[0])
        if not inp:
            return 1
        out = vtkUnstructuredGrid.GetData(outInfo)
        if not out:
            return 1

        def iter_patches(dataset):
            for i in range(dataset.GetNumberOfBlocks()):
                block = dataset.GetBlock(i)
                if block.IsA("vtkMultiBlockDataSet"):
                    for v in iter_patches(block):
                        yield v
                else:
                    yield block

        for i, result in enumerate(iter_patches(inp)):
            if i == self.__patch_index:
                break
        else:
            return 1

        if result.IsA("vtkPolyData"):
            filt = vtkAppendFilter()
            filt.AddInputData(result)
            filt.Update()
            result = filt.GetOutput()

        out.ShallowCopy(result)
        return 1

class FOAMMesh(SimpleGeometry, VtkSceneAnimation):

    def __init__(self, path, name='internalMesh', **kwargs):
        super().__init__(name=name, lod=True, **kwargs)

        reader = vtkPOpenFOAMReader()

        reader.SetCaseType(1)
        reader.CreateCellToPointOn()
        reader.CacheMeshOff()
        reader.DecomposePolyhedraOn()
        reader.ReleaseDataFlagOn()
        reader.ReadZonesOn()
        reader.SetFileName(os.path.join(path, 'p.foam'))
        reader.Update()

        reader.EnableAllCellArrays()
        reader.EnableAllLagrangianArrays()
        reader.EnableAllPointArrays()
        reader.EnableAllPatchArrays()
        reader.Update()

        self.__reader = reader

        patch_names = []
        for i in range(reader.GetNumberOfPatchArrays()):
            name = reader.GetPatchArrayName(i)
            patch_names.append(name)
        self.__patch_names = patch_names

        source = vtkPythonAlgorithm()
        self.filter = FOAMFilter(self, self.__patch_names.index('internalMesh'))
        source.SetPythonObject(self.filter)
        source.AddInputConnection(reader.GetOutputPort())

        self.source = source

        patches = []
        for i, n in enumerate(self.__patch_names):
            print('pname=', n, i)
            if n != 'internalMesh':
                obj = SimpleGeometry(name=n, lod=True)
                source = vtkPythonAlgorithm()
                obj.__filt = FOAMFilter(self, i)
                source.SetPythonObject(obj.__filt)
                source.AddInputConnection(reader.GetOutputPort())
                obj.source = source
                patches.append(obj)

        self.__patches = patches

        self.__cell_names = []
        cellsNum = reader.GetNumberOfCellArrays()
        for i in range(cellsNum):
            name = reader.GetCellArrayName(i)
            self.__cell_names.append(name)

        self.__point_names = []
        pointsNum = reader.GetNumberOfPointArrays()
        for i in range(pointsNum):
            name = reader.GetPointArrayName(i)
            self.__point_names.append(name)

        times = []
        time_values = reader.GetTimeValues()
        for i in range(time_values.GetNumberOfValues()):
            times.append(time_values.GetValue(i))
        self.times = times
        self.set_frame(-1)


    @property
    def patch_names(self):
        return self.__patch_names

    @property
    def patches(self):
        return self.__patches

    @property
    def cell_array_names(self):
        return self.__cell_names

    @property
    def point_array_names(self):
        return self.__point_names

    @property
    def reader(self):
        return self.__reader

    def update(self, time):
        self.__reader.SetTimeValue(time)
        self.__reader.Modified()
        self.__reader.Update()
