#ifndef IMAGEEXPERIMENT_H_
#define IMAGEEXPERIMENT_H_

#include "Experiments/HCUBE_Experiment.h"

namespace HCUBE
{
	class ImageExperiment : public Experiment
	{
		public:
			ImageExperiment( string _experimentName, int _threadID );
			virtual ~ImageExperiment() { }

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

		private:
		    double calculate_reward( NEAT::FastNetwork<float> & network );

	};
}


#endif /* IMAGEEXPERIMENT_H_ */
