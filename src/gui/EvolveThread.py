from PyQt4.QtCore import *
from random import randint

# A thread to handle image evolution.
class EvolveThread(QThread):

    # Define signals.
    finished_job = pyqtSignal()
    update_progress = pyqtSignal(int, int)  # update_progress( current, max )

    # Thread initialization.
    def __init__( self, parent = None ):
        print "EvolveThread::init"

        # Call QThread constructor.
        QThread.__init__( self, parent )

        # Create a mutex for job parameters.
        self.job_mutex = QMutex()

        # Initialize job parameters.
        self.job = 0
        self.selection = []

    # Run the thread.
    def run( self ):
        # Wait on jobs.
        while True:
            # Short wait (one second).
            self.sleep( 1 )

            # Check job queue.
            exiting = False
            next_job = self.start_next_job()
            if next_job:
                # If negative, exit thread.
                if next_job < 0:
                    exiting = True

                # If positive, run through generations.
                elif next_job > 0:
                    print "EvolveThread::job - iters[%d] initial_selection: " % next_job,
                    print self.selection

                    for iter in xrange(next_job):
                        self.selection = self.execute_iteration( iter, next_job, self.selection )
                    self.selection = []
            self.finish_job()

            # Emit the finished job signal if there was a job.
            if next_job:
                self.finished_job.emit()

            # Finished?
            if exiting:
                print "EvolveThread::exiting"
                break

    # Execute an iteration.
    def execute_iteration( self, iteration_id, max_iteration, selection ):
        print "  - EvolveThread:exec: iter[%d] selection: " % iteration_id,
        print selection

        # Assign reward to selection (or random reward if none are selected).
        if len(selection) > 0:
            for index in selection:
                self.parent().population.getIndividual(index).reward( 100 )
        else:
            for index in xrange(self.parent().population.getIndividualCount()):
                self.parent().population.getIndividual(index).reward( randint(1,10) )

        # Finish evaluations.
        self.parent().experiment.finishEvaluations()

        # Get next generation.
        self.parent().experiment.produceNextGeneration()
        self.parent().experiment.preprocessPopulation()
        self.parent().population = self.parent().experiment.pythonEvaluationSet()

        # Update population model.
        if self.parent().population.getIndividualCount() != self.parent().population_model.rowCount():
            print "WARNING: Discrepency between population size and model size! Things might blow up. Wear a hardhat."

        rows = self.parent().population_model.rowCount()
        update_index = iteration_id * rows + 1
        max_update_index = max_iteration * rows
        for i in xrange(rows):
            print " - Updating network %2d with new network..." % i,
            index = self.parent().population_list.model().index(i, 0)

            # ATW: TODO: As long as entropy is not being used to drive the evolution,
            # this stuff doesn't need to be calculated except for the last run.
            if (iteration_id + 1) == max_iteration:
                individual = self.parent().population.getIndividual(i)
                network = individual.spawnFastPhenotypeStack()
                self.parent().population_model.update_item(i, network)
                entropy = self.parent().population_model.image_entropy(i)

            print "Done"

            # Update element status.
            self.update_progress.emit( update_index, max_update_index )
            update_index += 1

        # ATW: TODO: This should return either an empty set (so all selections are
        # weighted "randomly") or it should return the best elements to move forward
        # (based on features, entropy, etc).
        return []

    # Add job to workflow.
    def add_job( self, iterations, selection ):
        # Handle mutex lock / unlock.
        job_locker = QMutexLocker( self.job_mutex )

        # Add job.
        self.job = iterations
        self.selection = []
        if len(selection) > 0:
            # If a selection is sent in, for only one iteration.
            self.job = 1

            # Extract row numbers.
            for sel in selection:
                self.selection.append( sel.row() )

    # Get next job from the workflow queue.
    def start_next_job( self ):
        # Lock the mutex here. Unlock in run function.
        self.job_mutex.lock()

        # Return most recent job after mutex has been locked.
        next_job = self.job
        self.job = 0
        return next_job

    # Finish the job.
    def finish_job( self ):
        # Unlock mutex.
        self.job_mutex.unlock()
