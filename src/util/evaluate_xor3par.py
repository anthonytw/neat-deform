from parse_log import parse_log
import sys
import pylab
import cPickle
import os
from numpy import *

# Build network evaluation function.
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

def evaluate_xor3( net ):
    num_evals = 2**3
    passed_evals = 0
    for x1 in xrange(2):
        for x2 in xrange(2):
            for x3 in xrange(2):
                net.reinitialize()

                net.setValue( 'X1', x1 )
                net.setValue( 'X2', x2 )
                net.setValue( 'X3', x3 )
                net.setValue( 'Bias', 1.0 )

                net.update()

                output = 1 if net.getValue( 'Output' ) > 0.5 else 0
                expected_output = x1 ^ x2 ^ x3

                if output == expected_output:
                    passed_evals += 1
    return 100.0 * passed_evals / float(num_evals)

# Evaluate log file or directory.
directory = ""
log_files = []
if os.path.isdir(sys.argv[1]):
    ext = ".xml.gz"
    directory = "%s/" % sys.argv[1]
    log_files = [file for file in os.listdir(sys.argv[1]) if file.lower().endswith(ext)]
elif os.path.isfile(sys.argv[1]):
    log_files.append(sys.argv[1])
else:
    print "Invalid file or directory supplied: %s!" % sys.argv[1]
    raise

# Read and average the statistics.
avg_evaluation = None
avg_max_fitness = None
avg_average_fitness = None
avg_species_count = None
avg_node_count = None
avg_link_count = None
for log_file in log_files:
    log = parse_log( "%s%s" % (directory, log_file), evaluate_xor3 )
    pylab.plot( log.evaluation )
    pylab.show()
    length = len(log.evaluation)
    if avg_evaluation == None:
        avg_evaluation = zeros(length)
        avg_max_fitness = zeros(length)
        avg_average_fitness = zeros(length)
        avg_species_count = zeros(length)
        avg_node_count = zeros(length)
        avg_link_count = zeros(length)
    for i in xrange(length):
        avg_evaluation[i] += log.evaluation[i]
        avg_max_fitness[i] += log.max_fitness[i]
        avg_average_fitness[i] += log.average_fitness[i]
        avg_species_count[i] += log.species_count[i]
        avg_node_count[i] += log.node_count[i]
        avg_link_count[i] += log.link_count[i]

num_tests = len(log_files)
scale = 1 / float(num_tests)
avg_evaluation *= scale
avg_max_fitness *= scale
avg_average_fitness *= scale
avg_species_count *= scale
avg_node_count *= scale
avg_link_count *= scale

# Store results for additional post-processing.
metrics = open( 'log.p', 'wb' )
cPickle.dump( avg_evaluation, metrics )
cPickle.dump( avg_max_fitness, metrics )
cPickle.dump( avg_average_fitness, metrics )
cPickle.dump( avg_species_count, metrics )
cPickle.dump( avg_node_count, metrics )
cPickle.dump( avg_link_count, metrics )
metrics.close()
'''
# Load metrics.

metrics = open( 'log.p', 'rb' )
avg_evaluation = cPickle.load( metrics )
avg_max_fitness = cPickle.load( metrics )
avg_average_fitness = cPickle.load( metrics )
avg_species_count = cPickle.load( metrics )
avg_node_count = cPickle.load( metrics )
avg_link_count = cPickle.load( metrics )
metrics.close()
'''
# Plot results.

# Plot evaluation results.
pylab.subplot( 4, 1, 1 )
pylab.plot( avg_evaluation )
pylab.title( 'Evaluation results' )
pylab.ylabel( '% correct' )

# Plot fitness.
pylab.subplot( 4, 1, 2 )
pylab.plot( avg_average_fitness )
pylab.plot( avg_max_fitness )
pylab.legend( ['Average Fitness', 'Max Fitness'], loc='lower right' )
pylab.title( 'Average and max fitness' )
pylab.ylabel( 'Fitness' )

# Plot species.
pylab.subplot( 4, 1, 3 )
pylab.plot( avg_species_count )
pylab.title( 'Species Count' )
pylab.ylabel( 'Species Count' )

# Plot node and link counts.
pylab.subplot( 4, 1, 4 )
pylab.plot( avg_node_count )
pylab.plot( avg_link_count )
pylab.legend( ['Node Count', 'Link Count'], loc='upper left' )
pylab.title( 'Gene Size' )
pylab.ylabel( 'Genes' )
pylab.xlabel( 'Generations' )

pylab.show()
