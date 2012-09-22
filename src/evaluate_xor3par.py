from parse_log import parse_log
import sys
import pylab
import cPickle

# Build network evaluation function.
def evaluate( net ):
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
    return passed_evals / float(num_evals)

# Evaluate log file.
log_file = sys.argv[1]
log = parse_log( log_file, evaluate )

# Store results for additional post-processing.
cPickle.dump( log, open('log.p', 'wb') )

# Plot results.
pylab.plot( log.evaluation )
pylab.show()
