from parse_log import parse_log
import sys
import pylab
#import cPickle
import os

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
                net.setValue( 'Bias', 0.3 )

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

for log_file in log_files:
    log = parse_log( "%s%s" % (directory, log_file), evaluate_xor2 )

    # Store results for additional post-processing.
    #cPickle.dump( log, open('log.p', 'wb') )

    # Plot results.

    # Plot evaluation results.
    pylab.subplot( 3, 1, 1 )
    pylab.plot( log.evaluation )
    pylab.title( 'Evaluation results' )
    pylab.xlabel( 'Generation' )
    pylab.ylabel( '% correct' )

    # Plot fitness.
    pylab.subplot( 3, 1, 2 )
    pylab.plot( log.average_fitness )
    pylab.title( 'Average fitness' )
    pylab.xlabel( 'Generation' )
    pylab.ylabel( 'Fitness' )

    # Plot species.
    pylab.subplot( 3, 1, 3 )
    pylab.plot( log.species_count )
    pylab.title( 'Species Count' )
    pylab.xlabel( 'Generation' )
    pylab.ylabel( 'Species Count' )

    pylab.show()
