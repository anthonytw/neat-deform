import PyHyperNEAT as neat
import os, sys
from subprocess import call
from datetime import datetime
from random import randint

start_dir = os.getcwd()

experiment_run_dir  = "../external/HyperNEAT/NE/HyperNEAT/out"
experiment_data_dir = "data"
experiment_name     = "Xor"
experiment_number   = 1
output_name         = "output"

# Specified experiment in command line arguments?
if len(sys.argv) >= 2:
    experiment_name = sys.argv[1]
if len(sys.argv) >= 3:
    experiment_number = int(sys.argv[2])

# Experiment prefix.
prefix = datetime.now().strftime("%y%m%d_%H%M%S")

# Move to experiment directory.
print "Moving to experiment run directory '%s'..." % experiment_run_dir
os.chdir( experiment_run_dir )

# Initialize HyperNEAT.
print "Initializing HyperNEAT..."
neat.initializeHyperNEAT()

# Load experiment.
print "Running HyperNEAT experiment '%s'..." % experiment_name
neat.setupExperiment( "%s/%sExperiment.dat" % (experiment_data_dir, experiment_name), "%s.xml" % output_name )

maxgen = neat.getMaximumGenerations()

experimentRun = neat.Py_Experiment()

for x in range(maxgen):
    
    if(x > 0):
        experimentRun.produceNextGeneration()
        
    #population pre-process, in experiment running
    experimentRun.preprocessPopulation()
    
    #evaluation run subclass from experiment run
    evalRun = experimentRun.pythonEvaluationSet()
    
    #genetic gen object
    geneticPop = evalRun.runPython()
    
    #experiment object
    experiment = evalRun.getExperimentObject()
    
    #the actual image experiment genetic gen object, reward
    #This reward can be change to image reward
    reward = randint(0,10)
    #take the 0th member of the genetic generation object, this will be passed to network to spawn a new network
    #then the network will be evaluated like the XOR experiment
    #the output will display to the user and they will upvote/downvote the picture
    #experiment.processGroupAndSetReward(geneticPop,reward)
    
    experimentRun.finishEvaluations()

# Cleanup.
print "Cleaning up..."
neat.cleanupHyperNEAT()

# Move files over.
os.chdir( start_dir )
call( "mv %s output/%s_%02d_%s.xml.gz" % ("%s/%s_best.xml.gz" % (experiment_run_dir, output_name), experiment_name, experiment_number, prefix), shell=True )

# Done.
print "===== Done."
