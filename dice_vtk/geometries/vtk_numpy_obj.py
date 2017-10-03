# External modules
# ================
from vtk import vtkPolyData, vtkPoints, vtkCellArray
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from vtk import vtkPolyDataMapper
from vtk import vtkActor
from vtk import vtkFloatArray
from vtk import vtkIdList

# DICE modules
# ============
from .geometry_base import GeometryBase

class VtkNumpyOBJ(GeometryBase):
    def __init__(self, **props):
        GeometryBase.__init__(self, 'VtkNumpyOBJ', **props)

        poly = vtkPolyData()

        if 'data' in props:
            data = props.pop('data')
            print('>>>>>>>>>>>>> type(data)', type(data), 'len(data)',
                  len(data), '/ 3 =', len(data) / 3)
            if isinstance(data, list):
                data = np.array(data)
            print('>>>>>>>>>>>>> type(data)', type(data), 'len(data)',
                  len(data), '/ 3 =', len(data) / 3)
            self.__verts = data.reshape((-1, 3))
            print('>>>>>>>>>>>>> len(__verts)',
                  len(self.__verts), '/ 3 =', len(self.__verts) / 3)
            self.__tris = np.insert(
                np.arange(len(self.__verts), dtype='i8').reshape((-1, 3)),
                0, 3, axis=1
            ).reshape(-1)

            points = vtkPoints()
            points.SetData(numpy_to_vtk(self.__verts))

            cells = vtkCellArray()

            cells.SetCells(
                int(len(self.__tris)/4), numpy_to_vtkIdTypeArray(self.__tris))

            poly.SetPoints(points)
            poly.SetPolys(cells)
        else:
            # TODO: Texture coordinates
            m = props.pop('mesh')
            # if (m.tcoords_same_as_verts or not m.has_tcoords) \
            #     and (m.normals_same_as_verts or not m.has_normals):
            np.set_printoptions(threshold=21)
            print('>>>>>>>>>>>>> len(m.points)', len(m.points), '/3 =',
                  len(m.points)/3, np.array(m.points))
            points = vtkPoints()
            points.SetData(numpy_to_vtk(np.array(m.points).reshape((-1, 3))))
            poly.SetPoints(points)
            if m.point_elems:
                poly.SetVerts(m.point_elems)
            if m.line_elems:
                poly.SetLines(m.line_elems)
            if m.polys:
                print('>>>>>>>>>>>>> len(m.polys)', len(m.polys), '/3 =',
                      len(m.polys) / 3)
                cells = vtkCellArray()
                for p in m.polys:
                    il = vtkIdList()
                    for v in p:
                        il.InsertNextId(v)
                    cells.InsertNextCell(il)
                poly.SetPolys(cells)
            if m.has_normals and m.normals_same_as_verts:
                print('>>>>>>>>>>>>> len(m.normals)', len(m.normals), '/3 =',
                      len(m.normals) / 3, np.array(m.normals))
                poly.GetPointData().SetNormals(
                    numpy_to_vtk(np.array(m.normals).reshape((-1, 3))))
            # else:
            #     new_normals = vtkFloatArray()
            #     new_normals.SetNumberOfComponents(3)
            #     new_normals.SetName('Normals')
            #     new_polys = vtkCellArray()

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(poly)
        actor = vtkActor()
        actor.GetProperty().SetInterpolationToFlat()
        actor.SetMapper(mapper)

        poly.ComputeBounds()
        self.bounds = poly.GetBounds()
        self.insert(mapper, actor)
        self.apply_props(props)

    from .geometry_props import \
        color, \
        representation, \
        visible, \
        opacity, \
        line_width, \
        point_size, \
        edge_color, \
        edge_visible, \
        position
