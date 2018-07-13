from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image
import cStringIO
import numpy

def convertQ2PIL( image ):
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    image.save(buffer, "PNG")

    strio = cStringIO.StringIO()
    strio.write(buffer.data())
    buffer.close()
    strio.seek(0)
    pil_im = Image.open(strio)
    return pil_im

def showQ( image ):
    pil_image = convertQ2PIL( image )
    pil_image.show()
    return pil_image

def PIL2array(img):
    return numpy.array(img.getdata(), numpy.uint8).reshape(img.size[1], img.size[0], 3)

def array2PIL(arr):
    if len(arr.shape) == 3:
        mode = 'RGB'
        size = (arr.shape[1], arr.shape[0])
        arr = arr.reshape(arr.shape[0]*arr.shape[1], arr.shape[2])
    else:
        mode = 'L'
        size = (arr.shape[1], arr.shape[0])
        arr = arr.reshape(arr.shape[0]*arr.shape[1])
    return Image.frombuffer(mode, size, arr.tostring(), 'raw', mode, 0, 1)
