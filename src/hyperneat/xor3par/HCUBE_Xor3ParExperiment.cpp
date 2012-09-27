#include "HCUBE_Defines.h"
#include "xor3par/HCUBE_Xor3ParExperiment.h"

using namespace NEAT;
namespace HCUBE
{
    Xor3ParExperiment::Xor3ParExperiment(string _experimentName,int _threadID) :
        Experiment(_experimentName,_threadID)
    { }

    NEAT::GeneticPopulation * Xor3ParExperiment::createInitialPopulation(int populationSize)
    {
        cout << "Creating Xor 3 Parity initial population..." << endl;
        GeneticPopulation *population = new GeneticPopulation();
        vector<GeneticNodeGene> genes;

        genes.push_back(GeneticNodeGene("Bias",  "NetworkSensor",     0, false));
        genes.push_back(GeneticNodeGene("X1",    "NetworkSensor",     0, false));
        genes.push_back(GeneticNodeGene("X2",    "NetworkSensor",     0, false));
        genes.push_back(GeneticNodeGene("X3",    "NetworkSensor",     0, false));
        genes.push_back(GeneticNodeGene("Output","NetworkOutputNode", 1, false, ACTIVATION_FUNCTION_SIGMOID));

        for (int a=0;a<populationSize;a++)
        {
            shared_ptr<GeneticIndividual> individual(new GeneticIndividual(genes,true,1.0));

            for (int b=0;b<0;b++)
            {
                individual->testMutate();
            }

            population->addIndividual(individual);
        }

        cout << "Finished creating population\n";
        return population;
    }

    double Xor3ParExperiment::calculate_reward( NEAT::FastNetwork<float> & network )
    {
        const int max_correct = 8; // 2^3 possible scenarios.
        int correct_answers = 0;

        double total_error = 0.0;

        for ( int x1 = 0; x1 < 2; ++x1 )
        for ( int x2 = 0; x2 < 2; ++x2 )
        for ( int x3 = 0; x3 < 2; ++x3 )
        {
            network.reinitialize();

            network.setValue( "X1", x1 );
            network.setValue( "X2", x2 );
            network.setValue( "X3", x3 );
            network.setValue( "Bias", 1.0f );

            network.update();

            double output = network.getValue( "Output" );
            int output_i = output > 0.5 ? 1 : 0;
            int expected_output_i = x1 ^ x2 ^ x3;
            double expected_output = double(expected_output_i);

            if ( output_i == expected_output_i )
                ++correct_answers;

            total_error += fabs(expected_output - output);
        }

        double sensitivity = correct_answers / double(max_correct);
        int sensitivity_i = static_cast<int>(sensitivity);
        double reward = 10.0*correct_answers + sensitivity*10.0 + sensitivity_i*40.0 - total_error*total_error + 9.0;

        if ( reward < 1.0 )
            reward = 1.0;

        return reward;
    }

    void Xor3ParExperiment::processGroup(shared_ptr<NEAT::GeneticGeneration> generation)
    {
        NEAT::FastNetwork<float> network = group[0]->spawnFastPhenotypeStack<float>();

        double reward = calculate_reward( network );
        group[0]->reward(reward);
    }

    void Xor3ParExperiment::processIndividualPostHoc(shared_ptr<NEAT::GeneticIndividual> individual)
    {
        NEAT::FastNetwork<float> network = individual->spawnFastPhenotypeStack<float>();

        double reward = calculate_reward( network );
        const double max_reward = 8*8 + 10.0 + 9.0;
        cout << "POST HOC ANALYSIS: " << reward << "/" << max_reward << endl;
    }

    Experiment* Xor3ParExperiment::clone()
    {
        Xor3ParExperiment * experiment = new Xor3ParExperiment(*this);

        return experiment;
    }
}
