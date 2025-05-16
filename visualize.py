import numpy as np
import vtk
from vtk.util import numpy_support

def create_volume(data, colormap='gray', opacity=0.2):
    # Convert NumPy array to VTK image data
    vtk_data = numpy_support.numpy_to_vtk(num_array=data.ravel(order='F'), deep=True, array_type=vtk.VTK_FLOAT)
    image = vtk.vtkImageData()
    image.SetDimensions(data.shape[::-1])
    image.SetSpacing(1, 1, 1)
    image.GetPointData().SetScalars(vtk_data)

    # Create transfer functions
    colorFunc = vtk.vtkColorTransferFunction()
    if colormap == 'gray':
        colorFunc.AddRGBPoint(np.min(data), 0.0, 0.0, 0.0)
        colorFunc.AddRGBPoint(np.max(data), 1.0, 1.0, 1.0)
    elif colormap == 'rainbow':
        colorFunc.SetColorSpaceToHSV()
        colorFunc.HSVWrapOff()
        colorFunc.AddRGBPoint(np.min(data), 0.0, 0.0, 1.0)
        colorFunc.AddRGBPoint(np.max(data), 1.0, 0.0, 0.0)

    opacityFunc = vtk.vtkPiecewiseFunction()
    opacityFunc.AddPoint(np.min(data), 0.0)
    opacityFunc.AddPoint(np.max(data), opacity)

    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorFunc)
    volumeProperty.SetScalarOpacity(opacityFunc)
    volumeProperty.ShadeOff()
    volumeProperty.SetInterpolationTypeToLinear()

    volumeMapper = vtk.vtkSmartVolumeMapper()
    volumeMapper.SetInputData(image)

    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    return volume


def create_transducer_points(points, color=(0, 1, 1)):
    vtk_points = vtk.vtkPoints()
    for p in points:
        vtk_points.InsertNextPoint(p.tolist())

    vertices = vtk.vtkCellArray()
    for i in range(len(points)):
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(i)

    pointPolyData = vtk.vtkPolyData()
    pointPolyData.SetPoints(vtk_points)
    pointPolyData.SetVerts(vertices)

    pointMapper = vtk.vtkPolyDataMapper()
    pointMapper.SetInputData(pointPolyData)

    pointActor = vtk.vtkActor()
    pointActor.SetMapper(pointMapper)
    pointActor.GetProperty().SetColor(color)
    pointActor.GetProperty().SetPointSize(4)

    return pointActor


def visualize(ct, pmap, tr_coords):
    volume_ct = create_volume(ct, colormap='gray', opacity=0.1)
    volume_pmap = create_volume(pmap, colormap='rainbow', opacity=0.2)
    transducer_actor = create_transducer_points(tr_coords)

    renderer = vtk.vtkRenderer()
    renderer.AddVolume(volume_ct)
    renderer.AddVolume(volume_pmap)
    renderer.AddActor(transducer_actor)
    renderer.SetBackground(1.0, 1.0, 1.0)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(800, 800)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    interactor.Start()


def main():
    sample_path = "./sample/TFUScapes/data/A00060925/exp_0.npz"
    data = np.load(sample_path)
    tr_coords = np.array(data["tr_coords"])
    ct = np.array(data["ct"], dtype=np.float32)
    pmap = np.array(data["pmap"], dtype=np.float32)

    visualize(ct, pmap, tr_coords)

if __name__ == "__main__":
    main()
