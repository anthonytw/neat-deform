from PyQt4.QtCore import *
from random import randint

import matplotlib.pyplot as plt

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
        self.cross_correlate = False

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
    def execute_iteration(
        self,
        iteration_id,
        max_iteration,
        selection ):
        print "  - EvolveThread:exec: iter[%d] selection: " % iteration_id,
        print selection

        # Assign reward to selection (or random reward if none are selected).
        if len(selection) > 0:
            for index in selection:
                self.parent().population.getIndividual(index).reward( randint(80,120) )
        else:
            for index in xrange(self.parent().population.getIndividualCount()):
                self.parent().population.getIndividual(index).reward( randint(10,40) )

        # Finish evaluations.
        self.parent().experiment.finishEvaluations()

        # Get next generation.
        self.parent().experiment.produceNextGeneration()
        self.parent().experiment.preprocessPopulation()
        self.parent().population = self.parent().experiment.pythonEvaluationSet()

        # Update population model.
        if self.parent().population.getIndividualCount() != self.parent().population_model.rowCount():
            print "WARNING: Discrepency between population size and model size! Things might blow up. Wear a hardhat."

        # Reset image cache every generation.
        image_cache = []

        rows = self.parent().population_model.rowCount()
        update_index = iteration_id * rows + 1
        max_update_index = max_iteration * rows
        selection = []
        for i in xrange(rows):
            print " - Updating network %2d with new network..." % i,
            index = self.parent().population_list.model().index(i, 0)

            # If performing cross-correlation or on the last iteration, update network.
            if self.cross_correlate or ((iteration_id + 1) == max_iteration):
                individual = self.parent().population.getIndividual(i)
                network = individual.spawnFastPhenotypeStack()
                self.parent().population_model.update_item(i, network)

            # Perform cross correlation with cached images. Do not perform on the last
            # iteration because the selection is not being updated.
            if self.cross_correlate and ((iteration_id + 1) < max_iteration):
                entropy = self.parent().population_model.image_entropy(i)
                similar_image_found = False
                for [ref_entropy, ref_autocorr] in image_cache:
                    crosscorr = self.parent().population_model.correlate_image(entropy, ref_entropy)
                    simrange = (0.6*ref_autocorr, 1.2*ref_autocorr)
                    print "   - - ccor: %.4f; acor: %.4f simrange: " % (crosscorr, ref_autocorr),
                    print simrange
                    if (crosscorr >= simrange[0]) and (crosscorr <= simrange[1]):
                        similar_image_found = True
                        break

                # No similar image found?
                if not similar_image_found:
                    autocorr = self.parent().population_model.correlate_image(entropy, entropy)
                    image_cache.append( [entropy, autocorr] )
                    selection.append( i )
                    print "- Found unique"
                else:
                    print "- Found similar"

            print "Done"

            # Update element status.
            self.update_progress.emit( update_index, max_update_index )
            update_index += 1

        return selection

    # Add job to workflow.
    def add_job( self, iterations, selection, cross_correlate = False ):
        # Handle mutex lock / unlock.
        job_locker = QMutexLocker( self.job_mutex )

        # Add job.
        self.job = iterations
        self.selection = []
        self.cross_correlate = cross_correlate
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
