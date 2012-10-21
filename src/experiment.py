import PyHyperNEAT as neat
import os, sys
from subprocess import call
from datetime import datetime
import random

def evaluate_xor2( net ):
    num_evals = 2**2
    passed_evals = 0
    for x1 in xrange(2):
        for x2 in xrange(2):
            net.reinitialize()

            net.setValue( 'X1', x1 )
            net.setValue( 'X2', x2 )
            net.setValue( 'Bias', 0.3 )

            net.update()

            output = 1 if net.getValue( 'Output' ) > 0.5 else 0
            expected_output = x1 ^ x2

            if output == expected_output:
                passed_evals += 1
    return 100.0 * passed_evals / float(num_evals)

start_dir = os.getcwd()

experiment_run_dir  = "../external/HyperNEAT/NE/HyperNEAT/out"
experiment_data_dir = "data"
experiment_name     = "Xor"
experiment_number   = 1
output_name         = "output"

print "%s - %d" % (experiment_name, experiment_number)

# Specified experiment in command line arguments?
if len(sys.argv) >= 2:
    experiment_name = sys.argv[1]
if len(sys.argv) >= 3:
    experiment_number = int(sys.argv[2])

print "%s - %d" % (experiment_name, experiment_number)

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
experimentRun = neat.setupExperiment( "%s/%sExperiment.dat" % (experiment_data_dir, experiment_name), "%s.xml" % output_name )

maxgen = neat.getMaximumGenerations()

for x in range(maxgen):

    if(x > 0):
        experimentRun.produceNextGeneration()

    #population pre-process, in experiment running
    experimentRun.preprocessPopulation()

    #vector = neat.GeneticIndividualVector()

    #evaluation run subclass from experiment run
    geneticIndividuals = experimentRun.pythonEvaluationSet()

    for generation in xrange(geneticIndividuals.getIndividualCount()):

        ind = geneticIndividuals.getIndividual( generation )

        net = ind.spawnFastPhenotypeStack()

        reward_value = evaluate_xor2(net)

        ind.reward(reward_value)

    #geneticIndividuals.sortByFitness()

    #geneticIndividuals.cleanup()

    experimentRun.finishEvaluations()

# Store the output file.
experimentRun.saveBest()

# Cleanup.
print "Cleaning up..."
neat.cleanupHyperNEAT()

# Move files over.
os.chdir( start_dir )
call( "mv %s output/%s_%02d_%s.xml.gz" % ("%s/%s_best.xml.gz" % (experiment_run_dir, output_name), experiment_name, experiment_number, prefix), shell=True )

# Done.
print "===== Done."
