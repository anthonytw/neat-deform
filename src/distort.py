# Imports.
from sys import exit, argv

# Check input arguments.
if len( argv ) != 4:
    print "Proper usage: ./run distort.py <network> <input_image> <output_image>"
    exit( 0 )

# Imports.
import PyHyperNEAT as neat
from PyQt5.QtGui import QApplication, QImage, QPixmap

import gui.PopulationModel

print "-------------------------------------------------------------------"
print "DISTORTING IMAGE"

# Load the file and generate the network.
print "-------------------------------------------------------------------"
print "Loading network..."
neat.initialize()
population = neat.load( argv[1] )
individual = population.getIndividual( 0, population.getGenerationCount() - 1 )
network = individual.spawnFastPhenotypeStack()

# Open the input image.
print "-------------------------------------------------------------------"
print "Distorting image..."
distortion = gui.PopulationModel.PopulationItem()

application = QApplication( argv )
image_map = QPixmap( argv[2] )
distorted_image_map = distortion.distort( image_map, network )
distorted_image = QImage( distorted_image_map )
distorted_image.save( argv[3] )

# Cleanup.
print "-------------------------------------------------------------------"
print "Done, cleaning up."
print "-------------------------------------------------------------------"
neat.cleanup()
