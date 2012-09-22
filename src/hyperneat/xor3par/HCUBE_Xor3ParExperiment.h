#ifndef __Xor3ParExperiment_h__
#define __Xor3ParExperiemnt_h__

#include "Experiments/HCUBE_Experiment.h"

namespace HCUBE
{
    class Xor3ParExperiment : public Experiment
    {
        public:
            Xor3ParExperiment( string _experimentName, int _threadID );
            virtual ~Xor3ParExperiment() { }

            virtual NEAT::GeneticPopulation* createInitialPopulation(int populationSize);
            virtual void processGroup(shared_ptr<NEAT::GeneticGeneration> generation);
            virtual void processIndividualPostHoc(shared_ptr<NEAT::GeneticIndividual> individual);

            virtual bool performUserEvaluations()
            {
                return false;
            }

            virtual inline bool isDisplayGenerationResult()
            {
                return displayGenerationResult;
            }

            virtual inline void setDisplayGenerationResult(bool _displayGenerationResult)
            {
                displayGenerationResult=_displayGenerationResult;
            }

            virtual inline void toggleDisplayGenerationResult()
            {
                displayGenerationResult=!displayGenerationResult;
            }

            virtual Experiment * clone();

            virtual void resetGenerationData(shared_ptr<NEAT::GeneticGeneration> generation) {}
            virtual void addGenerationData(shared_ptr<NEAT::GeneticGeneration> generation,shared_ptr<NEAT::GeneticIndividual> individual) {}
        };
}

#endif
