import xml.dom.minidom
import PyHyperNEAT as neat
import gzip

class HyperNEATResults:
    def __init__( self, filename = '', evaluation_function = None ):
        self.filename = filename

        self.average_fitness = []
        self.species_count = []
        self.evaluation = []

        if evaluation_function != None:
            self.refresh( evaluation_function )

    def refresh( self, evaluation_function ):
        # Parse DOM for statistics.
        self.parse_dom()

        # Fetch additional statistics from the network.
        self.evaluate_network( evaluation_function )

    def parse_dom( self ):
        print "Parsing XML for average fitness and species counts..."

        # Reset stats.
        self.average_fitness = []
        self.species_count = []
        on_generation = 0

        # Load XML.
        xml_file = gzip.open( self.filename, 'r' ).read()
        dom = xml.dom.minidom.parseString( xml_file )

        # Fetch all generations.
        generations = dom.getElementsByTagName( 'GeneticGeneration' )
        for generation in generations:
            # Only care about the generation number, species count, and
            # average fitness.
            generation_number = int(generation.getAttribute('GenNumber'))
            if generation_number != on_generation:
                print "ERROR: Generation discrepency: %d != %d! Missing data?" % (generation_number, on_generation)

            self.average_fitness.append(
                float(generation.getAttribute('AverageFitness')) )
            self.species_count.append(
                int(generation.getAttribute('SpeciesCount')) )

            on_generation += 1

    def evaluate_network( self, evaluation_function ):
        print "Evaluating the networks..."

        # Reset statistics.
        self.evaluation = []

        # Load population.
        population = neat.loadFromPopulation( self.filename )

        # Go through each generation, build the best network, and evaluate the completion results.
        for generation in xrange(population.getGenerationCount()):
           # First individual is always the most fit.
           ind = population.getIndividual( 0, generation )

           # Build network.
           net = ind.spawnFastPhenotypeStack()

           # Evaluate the network.
           self.evaluation.append( evaluation_function(net) )

def parse_log( filename, evaluation_function ):
    return HyperNEATResults( filename, evaluation_function )
