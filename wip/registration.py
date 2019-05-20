from ccpi.viewer.CILViewer2D import CILViewer2D
import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.util import numpy_support
import glob
import numpy


class cilToRGB(VTKPythonAlgorithmBase):
    '''vtkAlgorithm to crop a vtkPolyData with a Mask

    This is really only meant for point clouds: see points2vertices function

    
    gm = cilToRGB()
    gm.SetInputConnection(0, translate.GetOutputPort())
    gm.SetColor(cilToRGB.GREEN)
    gm.Update()
    
    stack = gm.GetOutput()
    
    print ("that's what is in the image ", (
        stack.GetScalarComponentAsFloat(20,20,20,0) ,
        stack.GetScalarComponentAsFloat(20,20,20,1) , 
        stack.GetScalarComponentAsFloat(20,20,20,2)))

    gm2 = cilToRGB()
    gm2.SetInputConnection(0, voi.GetOutputPort())
    gm2.SetColor(cilToRGB.MAGENTA)
    gm2.Update()
    add = vtk.vtkImageMathematics()
    add.SetOperationToAdd()
    add.SetInputConnection(0,gm.GetOutputPort())
    add.SetInputConnection(1,gm2.GetOutputPort())
    add.Update()
    print ("that's what is in the image ", (
        stack.GetScalarComponentAsFloat(20,20,20,0) ,
        stack.GetScalarComponentAsFloat(20,20,20,1) , 
        stack.GetScalarComponentAsFloat(20,20,20,2)))
    '''
    GREEN = (0,1,0.5)
    MAGENTA = (1,0,0.5)

    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=1, nOutputPorts=1)
        self.__color = None
        ncolors = vtk.VTK_UNSIGNED_SHORT_MAX + 1

        
    def SetColor(self, color):
        '''Sets the value at which the mask is active'''
        if color not in [ cilToRGB.GREEN, cilToRGB.MAGENTA ] :
            raise ValueError('Color must be GREEN or MAGENTA. Got' , color)

        if color != self.__color:
            self.__color = color
            #color = (1.,1.,1.)
            self.Modified()

    def GetColor(self):
        return self.__color

    def FillInputPortInformation(self, port, info):
        if port == 0:
            info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkImageData")
        elif port == 1:
            info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkImageData")
        
        return 1

    def FillOutputPortInformation(self, port, info):
        info.Set(vtk.vtkDataObject.DATA_TYPE_NAME(), "vtkImageData")
        return 1

    def RequestData(self, request, inInfo, outInfo):
        self.point_in_mask = 0
        inimage1 = vtk.vtkDataSet.GetData(inInfo[0])
        output = vtk.vtkImageData.GetData(outInfo)
        
        stack = vtk.vtkImageData()
        sliced = inimage1.GetExtent()
        stack.SetExtent(sliced[0],sliced[1], 
                        sliced[2],sliced[3], 
                        sliced[4], sliced[5])
        stack.AllocateScalars(inimage1.GetScalarType(), 3)
        dims = inimage1.GetDimensions()
        stack_array = numpy.reshape(
        numpy_support.vtk_to_numpy(
                        stack.GetPointData().GetScalars()
                        ),
            (dims[0],dims[1],dims[2],3) , order='F'
        )
        im1 = numpy.reshape(
            numpy_support.vtk_to_numpy(
                        inimage1.GetPointData().GetScalars()
                        ),
            (dims[0],dims[1],dims[2]), order='F'
        )
        
        color = self.__color
        for channel in range(3):
            stack_array[:,:,:,channel] = im1 * color[channel]    
        # put the output in the out port
        output.ShallowCopy(stack)
        return 1 
    def GetOutput(self):
        return self.GetOutputDataObject(0)


class cilImageMathematics(VTKPythonAlgorithmBase):
    '''vtkAlgorithm to do image mathematics with int images returning float images

    '''
    ADD = numpy.add
    SUBTRACT = numpy.subtract
    MULTIPLY = numpy.multiply
    DIVIDE = numpy.divide

    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=2, nOutputPorts=1)
        self.__operation = None
        self.__out_dtype = vtk.VTK_FLOAT

    def SetOperation(self, operation):
        '''Sets the value at which the mask is active'''
        if operation not in [cilImageMathematics.ADD, cilImageMathematics.SUBTRACT,
            cilImageMathematics.MULTIPLY, cilImageMathematics.DIVIDE]:
            raise ValueError('unsupported operation ', operation)
        
        if operation != self.__operation:
            self.__operation = operation
            #color = (1.,1.,1.)
            print ("operation set to", operation)
            self.Modified()

    def GetOperation(self):
        return self.__operation
    def SetOutputScalarTypeToFloat(self):
        self.__out_dtype = vtk.VTK_FLOAT
        self.Modified()
    def SetOutputScalarTypeToDouble(self):
        self.__out_dtype = vtk.VTK_DOUBLE
        self.Modified()
    def GetOutputType(self):
        return self.__out_dtype

    def FillInputPortInformation(self, port, info):
        if port == 0:
            info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkImageData")
        elif port == 1:
            info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkImageData")
        
        return 1

    def FillOutputPortInformation(self, port, info):
        info.Set(vtk.vtkDataObject.DATA_TYPE_NAME(), "vtkImageData")
        return 1

    def add_to_float(self,x,y, **kwargs):
        return float(x) + float(y)
    def subtract_to_float(self,x,y, **kwargs):
        return float(x) - float(y)
    def multiply_to_float(self,x,y, **kwargs):
        return float(x) * float(y)
    def divide_to_float(self,x,y, **kwargs):
        return float(x) / float(y)

    def RequestData(self, request, inInfo, outInfo):
        print ("RequestData")
        inimage1 = vtk.vtkDataSet.GetData(inInfo[0])
        inimage2 = vtk.vtkDataSet.GetData(inInfo[1])
        output = vtk.vtkImageData.GetData(outInfo)
        print ("inimage1 ", inimage1.GetScalarTypeAsString())
        print ("inimage2 ", inimage2.GetScalarTypeAsString())
        stack = vtk.vtkImageData()
        sliced = inimage1.GetExtent()
        stack.SetExtent(sliced[0],sliced[1], 
                        sliced[2],sliced[3], 
                        sliced[4], sliced[5])
        stack.AllocateScalars(self.__out_dtype, 1)
        print ("Allocated ", stack.GetScalarTypeAsString())
        dims = inimage1.GetDimensions()
        stack_array = numpy.reshape(
        numpy_support.vtk_to_numpy(
                        stack.GetPointData().GetScalars()
                        ),
            (dims[0],dims[1],dims[2]) , order='F'
        )
        im1 = numpy.reshape(
            numpy_support.vtk_to_numpy(
                        inimage1.GetPointData().GetScalars()
                        ),
            (dims[0],dims[1],dims[2]), order='F'
        )
        im2 = numpy.reshape(
            numpy_support.vtk_to_numpy(
                        inimage2.GetPointData().GetScalars()
                        ),
            (dims[0],dims[1],dims[2]), order='F'
        )
        operation = self.__operation
        if operation == cilImageMathematics.ADD:
            func = self.add_to_float
        elif operation == cilImageMathematics.SUBTRACT:
            func = self.subtract_to_float
        elif operation == cilImageMathematics.MULTIPLY:
            func = self.multiply_to_float
        elif operation == cilImageMathematics.DIVIDE:
            func = self.divide_to_float
        else:
            raise ValueError('Unsupported operation ', operation)
        print (func)
        np_op = numpy.frompyfunc(func, 2, 1)
        print (np_op)
        if self.__out_dtype == vtk.VTK_FLOAT:
            dtype = numpy.float32
        elif self.__out_dtype == vtk.VTK_DOUBLE:
            dtype = numpy.float64
        print ("doing it")
        a = numpy.asarray(np_op(im1,im2), dtype=dtype)
        #stack_array[:] = numpy.asarray(np_op(im1,im2), dtype=dtype)
        stack_array[:,:,:] = a
        #print ("operation" , a)
        print (im1.min(), im2.min(), im1.max(), im2.max(), a.min(), a.max())
        # put the output in the out port
        output.ShallowCopy(stack)
        return 1 
    def GetOutput(self):
        return self.GetOutputDataObject(0)

def OnKeyPressEvent(interactor, event):
    '''https://gitlab.kitware.com/vtk/vtk/issues/15777'''
    trans = list(translate.GetTranslation())
    if interactor.GetKeyCode() == "j":
        trans[1] += 1
    elif interactor.GetKeyCode() == "n":
        trans[1] -= 1
    elif interactor.GetKeyCode() == "b":
        trans[0] -= 1
    elif interactor.GetKeyCode() == "m":
        trans[0] += 1
    translate.SetTranslation(*trans)
    translate.Update()
    subtract.Update()
    v.setInputData(subtract.GetOutput())
    


#%%
if __name__ == '__main__':
    err = vtk.vtkFileOutputWindow()
    err.SetFileName("viewer.log")
    vtk.vtkOutputWindow.SetInstance(err)

    wildcard_filenames = '204506_8bit/*.tif'
    filenames = glob.glob(wildcard_filenames)

    reader = vtk.vtkTIFFReader()
    sa = vtk.vtkStringArray()
    #i = 0
    # while (i < 1054):
    for fname in filenames:
        #fname = os.path.join(directory,"8bit-1%04d.tif" % i)
        i = sa.InsertNextValue(fname)

    print("read {} files".format(i))

    reader.SetFileNames(sa)
    # reader.Update()
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName('../../../../CCPi-Simpleflex/data/head.mha')
    reader.Update()
    extent = reader.GetOutput().GetExtent()

    voi = vtk.vtkExtractVOI()
    voi.SetInputData(reader.GetOutput())
    voi.SetVOI(extent[1]//10, int(extent[1] *(0.9)),extent[3]//10, int(extent[3] *(0.9)) , extent[4], extent[5])
    voi.Update()

    translate = vtk.vtkImageTranslateExtent()
    translate.SetTranslation(5,-5,0)
    translate.SetInputData(voi.GetOutput())
    translate.Update()




    # print ("out of the reader", reader.GetOutput())
    if False:
        wildcard_filenames2 = '204507_8bit/*.tif'
        filenames2 = glob.glob(wildcard_filenames2)

        reader2 = vtk.vtkTIFFReader()
        sa2 = vtk.vtkStringArray()
        for fname in filenames2:
            i = sa2.InsertNextValue(fname)

        print("read {} files".format(i))

        reader2.SetFileNames(sa)
        reader2.Update()
    use_vtk = True
    if use_vtk:
        cast1 = vtk.vtkImageCast()
        cast2 = vtk.vtkImageCast()
        cast1.SetInputConnection(voi.GetOutputPort())
        cast1.SetOutputScalarTypeToFloat()
        cast2.SetInputConnection(translate.GetOutputPort())
        cast2.SetOutputScalarTypeToFloat()
        
        subtract = vtk.vtkImageMathematics()
        subtract.SetOperationToSubtract()
        # subtract.SetInput1Data(voi.GetOutput())
        # subtract.SetInput2Data(translate.GetOutput())
        subtract.SetInputConnection(1,cast1.GetOutputPort())
        subtract.SetInputConnection(0,cast2.GetOutputPort())
        
        subtract.Update()
    else:
        subtract = cilImageMathematics()
        subtract.SetOperation(cilImageMathematics.SUBTRACT)
        #subtract.SetOperation('pippo')
        subtract.SetOutputScalarTypeToFloat()
        subtract.SetInputConnection(0,voi.GetOutputPort())
        subtract.SetInputConnection(1,translate.GetOutputPort())
        subtract.Update()

    print ("subtract type", subtract.GetOutput().GetScalarTypeAsString())
    
    stats = vtk.vtkImageHistogramStatistics()
    stats.SetInputConnection(subtract.GetOutputPort())
    stats.Update()
    print ("stats ", stats.GetMinimum(), stats.GetMaximum(), stats.GetMean(), stats.GetMedian())
    
    v = CILViewer2D()

    v.style.AddObserver('KeyPressEvent', OnKeyPressEvent, 0.5)

    v.setInputData(subtract.GetOutput())
    v.startRenderLoop()