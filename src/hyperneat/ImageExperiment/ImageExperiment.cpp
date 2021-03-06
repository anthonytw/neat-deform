#include "HCUBE_Defines.h"
#include "ImageExperiment/ImageExperiment.h"

using namespace NEAT;
namespace HCUBE
{
	ImageExperiment::ImageExperiment(string _experimentName,int _threadID) :
        Experiment(_experimentName,_threadID)
    {
        /*layerInfo = NEAT::LayeredSubstrateInfo();

        //Piece input layer (a)
        layerInfo.layerSizes.push_back(JGTL::Vector2<int>(1024,1));
        layerInfo.layerValidSizes.push_back(JGTL::Vector2<int>(1024,1));
        layerInfo.layerNames.push_back("Input");
        layerInfo.layerIsInput.push_back(true);
        layerInfo.layerLocations.push_back(JGTL::Vector3<float>(0,0,0));

        //OutputLayer (e)
        layerInfo.layerSizes.push_back(JGTL::Vector2<int>(1,1));
        layerInfo.layerValidSizes.push_back(JGTL::Vector2<int>(1,1));
        layerInfo.layerNames.push_back("Output");
        layerInfo.layerIsInput.push_back(false);
        layerInfo.layerLocations.push_back(JGTL::Vector3<float>(0,8,0));

        //inputs connect to hidden
        layerInfo.layerAdjacencyList.push_back(std::pair<string,string>("Input","Output"));

        layerInfo.normalize = true;
        layerInfo.useOldOutputNames = false;

        substrate = NEAT::LayeredSubstrate<float>();
        substrate.setLayerInfo(layerInfo);*/
    }

	NEAT::GeneticPopulation * ImageExperiment::createInitialPopulation(
        int populationSize)
    {
        cout << "Creating Image Experiment initial population..." << endl;
        GeneticPopulation *population = new GeneticPopulation();
        vector<GeneticNodeGene> genes;

        genes.push_back(GeneticNodeGene("Bias", "NetworkSensor",     0, false));
        genes.push_back(GeneticNodeGene("X",    "NetworkSensor",     0, false));
        genes.push_back(GeneticNodeGene("Y",    "NetworkSensor",     0, false));
        //genes.push_back(GeneticNodeGene("Gauss","HiddenNode",      0.5, false, ACTIVATION_FUNCTION_GAUSSIAN));
        genes.push_back(GeneticNodeGene("XOUT", "NetworkOutputNode", 1, false, ACTIVATION_FUNCTION_SIGMOID));
        genes.push_back(GeneticNodeGene("YOUT", "NetworkOutputNode", 1, false, ACTIVATION_FUNCTION_SIGMOID));

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

    double ImageExperiment::calculate_reward( NEAT::FastNetwork<float> & network )
    {}

    void ImageExperiment::processGroup(shared_ptr<NEAT::GeneticGeneration> generation)
    {
        NEAT::FastNetwork<float> network = group[0]->spawnFastPhenotypeStack<float>();

        double reward = calculate_reward( network );
        group[0]->reward(reward);
    }

    void ImageExperiment::processIndividualPostHoc(shared_ptr<NEAT::GeneticIndividual> individual)
    {
        NEAT::FastNetwork<float> network = individual->spawnFastPhenotypeStack<float>();

        double reward = calculate_reward( network );
        const double max_reward = 8*8 + 10.0 + 9.0;
        cout << "POST HOC ANALYSIS: " << reward << "/" << max_reward << endl;
    }

    void setReward(shared_ptr<NEAT::GeneticIndividual> generation,double reward){
        generation->reward(reward);
    }

    Experiment* ImageExperiment::clone()
    {
        ImageExperiment * experiment = new ImageExperiment(*this);

        return experiment;
    }
}
