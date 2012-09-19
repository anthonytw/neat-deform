import PyHyperNEAT as neat
import os
from subprocess import call
from datetime import datetime

start_dir = os.getcwd()

experiment_run_dir  = "../external/HyperNEAT/NE/HyperNEAT/out"
experiment_data_dir = "data"
experiment_name     = "Xor3Par"
output_name         = "output"

# Move to experiment directory.
print "Moving to experiment run directory '%s'..." % experiment_run_dir
os.chdir( experiment_run_dir )

# Initialize HyperNEAT.
print "Initializing HyperNEAT..."
neat.initializeHyperNEAT()

# Load experiment.
print "Running HyperNEAT experiment '%s'..." % experiment_name
neat.setupExperiment( "%s/%sExperiment.dat" % (experiment_data_dir, experiment_name), "%s.xml" % output_name )

# Cleanup.
print "Cleaning up..."
neat.cleanupHyperNEAT()

# Move files over.
os.chdir( start_dir )
call( "mv %s output/%s_%s_%s.xml.gz" % ("%s/%s_best.xml.gz" % (experiment_run_dir, output_name), experiment_name, datetime.now().strftime("%y%m%d_%H%M%S"), output_name), shell=True )

# Done.
print "Done."
