#import PyHyperNEAT as neat
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from scipy import *
import cStringIO
import Image
import os
import sys

# Represents a dummy network for testing.
class DummyNetwork:
    # Network distortion types.
    OneToOne = 1
    HFlip    = 2
    VFlip    = 3
    Flip     = 4

    def __init__( self, network_type = OneToOne ):
        self.network_type = network_type
        self.x_in = 0.0
        self.y_in = 0.0

    def reinitialize( self ):
        pass

    def setValue( self, name, value ):
        if name == 'X':
            self.x_in = float(value)
        elif name == 'Y':
            self.y_in = float(value)

    def update( self ):
        pass

    def getValue( self, name ):
        if name == 'XOUT':
            ret_val = self.x_in
            if self.network_type == DummyNetwork.HFlip:
                ret_val = -ret_val
            elif name == 'YOUT':
                ret_val = self.y_in
                if self.network_type == DummyNetwork.VFlip:
                    ret_val = -ret_val

        if self.network_type == DummyNetwork.Flip:
            return -ret_val
        else:
            return ret_val

# Represents one element in a popluation.
class PopulationItem:
    def __init__( self ):
        self.network = None
        self.distorted_image = None
        self.icon = None
        self.entropy = None

    def update_distortion( self, image, network = None ):
        if network != None:
            self.network = network

        if (image != None) and (self.network != None):
            self.distorted_image = self.distort( image, self.network )
            self.icon = QIcon(self.distorted_image)

    #@profile
    def distort( self, image_map, network ):
        #return QPixmap( QImage(image_map) )
        # Convert whatever's sent in to the appropriate image format.
        image = QImage( image_map )
        image.convertToFormat( QImage.Format_RGB32 )

        # Extract channel data from the image.
        buffer = QBuffer( )
        buffer.open( QBuffer.ReadWrite )
        image.save( buffer, 'PNG' )
        strio = cStringIO.StringIO()
        strio.write( buffer.data( ) )
        buffer.close( )
        strio.seek( 0 )
        pil_image = Image.open( strio )
        pil_image.load()
        self.entropy = self.calculate_entropy(pil_image)
        image_chan_i = pil_image.split()
        image_chan = [
            image_chan_i[0].load(),
            image_chan_i[1].load(),
            image_chan_i[2].load()]

        # Create a new image of the same size.
        distorted_image = QImage( image.width(), image.height(), QImage.Format_RGB32 )

        # Determine normalized coordinates.
        x_norm = image.width() / 2.0
        y_norm = image.height() / 2.0

        # For each pixel, run the network with the destination point to determine
        # which pixels to blend.
        for y in xrange(image.height()):
            for x in xrange(image.width()):
                y_norm_in = (y - y_norm) / y_norm
                x_norm_in = (x - x_norm) / x_norm

                # Evaluate network.
                network.reinitialize( )
                network.setValue( 'X', x_norm_in )
                network.setValue( 'Y', y_norm_in )
                network.setValue( 'Bias', .5 )
                network.update( )

                x_norm_out = network.getValue( 'XOUT' )
                y_norm_out = network.getValue( 'YOUT' )

                # Determine pixel coordinates and clamp to the image boundaries.
                y_out = y_norm_out * y_norm + y_norm
                x_out = x_norm_out * x_norm + x_norm
                if y_out < 0.0:
                    y_out = 0.0
                elif y_out > image.height() - 1:
                    y_out = image.height() - 1
                    if x_out < 0.0:
                        x_out = 0.0
                    elif x_out > image.width() - 1:
                        x_out = image.width() - 1

                # Determine row and column pixels and weights.
                x_o1 = int(x_out)
                x_o2 = x_o1 + 1 if x_o1 < image.width() - 1 else x_o1
                y_o1 = int(y_out)
                y_o2 = y_o1 + 1 if y_o1 < image.height() - 1 else y_o1
                x_w = x_out - x_o1
                y_w = y_out - y_o1

                # Combine pixels.
                p = [0, 0, 0]
                for i in xrange(3):
                    p1 = int(round(
                        image_chan[i][x_o1, y_o1]*(1-x_w) +
                        image_chan[i][x_o2, y_o1]*(x_w) ))
                    p2 = int(round(
                        image_chan[i][x_o1, y_o2]*(1-x_w) +
                        image_chan[i][x_o2, y_o2]*(x_w) ))
                    p[i] = p1*(1-y_w) + p2*(y_w)

                # Set value.
                distorted_image.setPixel(
                    x, y, qRgb(p[0], p[1], p[2]) )

        return QPixmap(distorted_image)

    def get_distorted_image( self ):
        return QVariant() if self.distorted_image == None else self.distorted_image

    def get_icon( self ):
        return QVariant() if self.icon == None else self.icon

    def calculate_entropy(self, image):
        image = inner(image, [299, 587, 114]) / 1000
        return (image - image.mean()) / image.std()

# A simple class for handling a population model.
class PopulationModel(QAbstractListModel):
    def __init__( self, population_size, parent = None ):
        super(PopulationModel, self).__init__( parent )
        self.image_number = 0
        self.population_size = population_size
        self.original_image = None
        self.population = [PopulationItem() for x in xrange(self.population_size)]

    def set_original_image( self, image ):
        self.original_image = image
        for i in xrange(self.population_size):
            self.update_item( i )

    def update_item( self, index, network = None ):
        self.population[index].update_distortion( self.original_image, network )

    def image_entropy(self,index):
        return self.population[index].entropy

    def distort( self, index, image_map ):
        return self.population[index].distort(
            image_map, self.population[index].network )

    def rowCount( self, parent = QModelIndex() ):
        return len(self.population)

    def correlate_image(self, image_entropy1, image_entropy2):
        return correlate2d(image_entropy1, image_entropy2, mode='same').max()

    def data( self, index, role ):
        if (not index.isValid()) or (index.row() >= self.population_size):
            return None

        if role == Qt.DecorationRole:
            return self.population[index.row()].get_icon( )
        elif role == Qt.SizeHintRole:
            return QSize(120, 120)
        else:
            return QVariant()
