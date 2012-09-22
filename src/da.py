import PyHyperNEAT as neat
import sys

file = sys.argv[1]
pop = neat.loadFromPopulation( file )
generations = pop.getGenerationCount()
individuals = pop.getIndividualCount(generations-1)

print "Loaded population from '%s'..." % file
print " - Generations: %d" % generations
print " - Ind/gen:     %d" % individuals

print "Determining maximum fitness..."

speciesIDs = set()
max_fit = -1
max_fit_id = -1
max_fit_species = -1
for i in xrange(individuals):
    ind = pop.getIndividual( i, generations-1 )
    fitness = ind.getFitness()
    speciesID = ind.getSpeciesID()
    if speciesID not in speciesIDs:
        print " - Found new species ID: %d" % speciesID
        speciesIDs.add( speciesID )
        speciesIDs.add(speciesID)
    print " - Evaluating individual %d (fitness %f; species %d)..." % (i, fitness, speciesID)
    if fitness > max_fit:
        print "   - Found new fitness leader! %f -> %f" % (max_fit, fitness)
        max_fit = fitness
        max_fit_id = i
        max_fit_species = speciesID

print "Most fit individual: ID: %d Species: %d Fitness: %f" % (max_fit_id, max_fit_species, max_fit)
print "Evaluation:"

ind = pop.getIndividual( max_fit_id, generations-1 )
net = ind.spawnFastPhenotypeStack()
for x1 in xrange(2):
    for x2 in xrange(2):
        net.reinitialize()

        net.setValue( "X1", x1 )
        net.setValue( "X2", x2 )

        net.update()

        output = net.getValue( "Output" )
        output_int = 1 if output > 0.5 else 0
        expected_output = x1 ^  x2

        print "X1: %d X2: %d | Result: %f/%d Expected: %d" % (x1, x2, output, output_int, expected_output)
