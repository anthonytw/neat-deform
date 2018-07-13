from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os.path
import sys
import PyHyperNEAT as neat
from random import randint
from datetime import datetime

from PopulationModel import *
from EvolveThread import *

class Window(QMainWindow):
    def __init__( self, parent = None ):
        super(Window, self).__init__( parent )
        self.setWindowTitle( 'Interactive Distortion Evolver' )

        ### Experiment Configuration
        # ATW: TODO: When we start getting reasonable distortions, there
        # needs to be a method to reload an old population. For now we'll
        # always make a new one.

        self.experiment_data_dir  = "../external/HyperNEAT/NE/HyperNEAT/out/data"
        self.date_specifier = datetime.now().strftime("%y%m%d_%H%M%S")
        self.image_storage = []

        # Initialize HyperNEAT.
        neat.initialize()

        # See if there is an output directory.
        if not os.path.exists(os.getcwd() + "/output"):
            os.mkdir(os.getcwd() + "/output")

        # Load the image experiment.
        self.experiment = neat.setupExperiment(
            "%s/ImageExperiment.dat" % self.experiment_data_dir,
            "output/imageExp_out_%s.xml" % self.date_specifier )

        # Grab the global parameters.
        self.globals = neat.getGlobalParameters()
        population_size = int(self.globals.getParameterValue('PopulationSize'))

        ### GUI Configuration

        # Set default window size.
        self.setFixedSize( 670, 700 )

        # Initialize the list view for the distorted images.
        lv = QListView( )
        lv.setViewMode( QListView.IconMode )
        lv.setUniformItemSizes( True )
        lv.setSelectionRectVisible( True )
        lv.setMovement( QListView.Static )
        lv.setSelectionMode( QListView.MultiSelection )
        lv.setEditTriggers( QListView.CurrentChanged )
        lv.setResizeMode( QListView.Adjust )
        lv.setIconSize( QSize(120, 120) )
        lv.setMinimumSize( 500, 385 )
        lv.setSpacing( 5 )
        lv.setEnabled( False )
        self.population_list = lv

        # Context menu.
        lv.setContextMenuPolicy( Qt.CustomContextMenu )
        lv.customContextMenuRequested.connect(self.handle_context_menu)

        # Create the population model.
        pm = PopulationModel( population_size )
        self.population_model = pm
        lv.setModel( pm )
        for i in xrange(population_size):
            self.population_model.update_item( i, DummyNetwork( i % 4 + 1 ) )

        # Monitor population list selection changes.
        lv.selectionModel().selectionChanged.connect(self.handle_listview_change )

        # Initialize widgets for displaying the graphic and for choosing
        # a new base image.
        btn_select_image = QPushButton( "Load Image" )
        btn_select_image.released.connect(self.select_image)
        lbl_image = QLabel( "Nothing loaded" )
        lbl_image.setFixedSize( 120, 120 )
        self.original_image_label = lbl_image
        image_layout = QVBoxLayout()
        image_layout.addWidget( btn_select_image )
        image_layout.addWidget( lbl_image )

        # Initialize a horizontal layout for the parameters.
        gb = QGroupBox( "Evolution Parameters" )
        gb.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )

        tw = QTableWidget( 1, 2 )
        tw.setHorizontalHeaderLabels("Parameter;Value".split(';'))
        tw.setColumnWidth( 0, 350 )
        tw.horizontalHeader().setStretchLastSection( True )
        tw.itemChanged.connect(self.handle_parameter_change)
        self.parameter_table = tw

        tw_layout = QVBoxLayout()
        tw_layout.addWidget( tw )
        gb.setLayout( tw_layout )

        param_layout = QHBoxLayout()
        param_layout.addLayout( image_layout )
        param_layout.addWidget( gb )

        # Grab the global parameters.
        parameter_count = self.globals.getParameterCount()
        tw.setRowCount( parameter_count )
        for p in xrange(parameter_count):
            parameter_name = self.globals.getParameterName( p )
            tw.model().setData( tw.model().index( p, 0 ), parameter_name )
            tw.model().setData( tw.model().index( p, 1 ), self.globals.getParameterValue( parameter_name ) )
            index = tw.item( p, 0 )
            index.setFlags( index.flags() ^ Qt.ItemIsEditable )

        # Initialize a horizontal layout for the evolve button.
        btn_evolve = QPushButton( "Shuffle" )
        btn_evolve.released.connect(self.evolve_image)
        btn_evolve.setEnabled( False )
        self.btn_evolve = btn_evolve
        self.btn_evolve.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )

        self.spin_evolve_iterations = QSpinBox()
        self.spin_evolve_iterations.setRange( 1, 100 )
        self.spin_evolve_iterations.setValue( 1 )

        self.cb_cross_correlate = QCheckBox( "X-Corr" )
        self.cb_cross_correlate.setChecked( True )

        control_layout = QHBoxLayout()
        control_layout.addWidget( btn_evolve )
        control_layout.addWidget( self.spin_evolve_iterations )
        control_layout.addWidget( self.cb_cross_correlate )

        # Initialize vertical central layout.
        central_layout = QVBoxLayout()
        central_layout.addLayout( param_layout )
        central_layout.addWidget( lv )
        central_layout.addLayout( control_layout )
        central_widget = QFrame()
        central_widget.setLayout( central_layout )

        self.setCentralWidget( central_widget )

        # Create a menu
        self.image_menu = QMenu("Menu", self)
        self.image_menu_save_image = self.image_menu.addAction("Save Selected Images")
        self.image_menu_save_network = self.image_menu.addAction("Save Selected Neural Network")

        ### Initialization

        # Handle command line parameters.
        if len(sys.argv) >= 2:
            self.select_image(sys.argv[1])

        # Create progress dialog.
        self.progress_dialog = QProgressDialog( self );
        self.progress_dialog.setLabelText( "Evolving population..." )
        self.progress_dialog.setWindowModality( Qt.WindowModal );
        self.progress_dialog.setVisible( False )
        self.progress_dialog.setCancelButton( None )

        # Start evolver thread.
        self.evolve_thread = EvolveThread( self )
        self.evolve_thread.finished_job.connect( self.finish_evolution )
        self.evolve_thread.update_progress.connect( self.update_evolution_progress )
        self.evolve_thread.start()

        # Generate first population.
        self.population = self.experiment.pythonEvaluationSet()
        self.evolve_image()

    # Destructor.
    def __del__( self ):
        # Save best population.
        self.experiment.saveBest()

        # Cleanup HyperNEAT.
        neat.cleanup()

        # Exit evolve thread.
        try:
            self.evolve_thread.terminate()
            self.evolve_thread.wait( 5000 )
        except NameError:
            print "Evolve thread not created yet, thus not destroyed."

    # Update a parameter value.
    def handle_parameter_change( self, parameter ):
        column = parameter.column()
        if column == 1:
            row = parameter.row()
            parameter_name = self.globals.getParameterName( row )
            current_value = self.globals.getParameterValue( parameter_name )
            v = parameter.data(Qt.EditRole)
            if v.canConvert(QVariant.Double):
                v.convert(QVariant.Double)
                self.globals.setParameterValue(parameter_name, v.value())
            else:
                parameter.setText("%.2f" % current_value)

    # Choose a new image to work with.
    def select_image( self, file_name = None ):
        if file_name == None:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Select Image", "",
                "Image Files (*.png *.jpg *.bmp)" );

        if os.path.isfile(file_name):
            # Disable evolve button.
            self.btn_evolve.setEnabled( False )

            # Load image.
            print "Loading image: %s..." % file_name
            self.population_list.setEnabled( True )
            self.original_image = QImage( file_name )
            scaled_image = self.original_image.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.population_model.set_original_image( scaled_image )
            self.original_image_label.setPixmap( QPixmap(scaled_image) )

            # Enable evolve button.
            self.btn_evolve.setEnabled( True )

    # Handles listview changes. We only care if elements are selected.
    def handle_listview_change( self, selected, deselected ):
        selection = self.population_list.selectionModel().hasSelection()
        if selection:
            self.spin_evolve_iterations.setEnabled( False )
            self.btn_evolve.setText('Evolve')
        else:
            self.spin_evolve_iterations.setEnabled( True )
            self.btn_evolve.setText('Shuffle')

    # Evolve the image with the selected individuals.
    def evolve_image( self ):
        # Disable evolve button.
        self.btn_evolve.setEnabled( False )
        self.spin_evolve_iterations.setEnabled( False )
        self.cb_cross_correlate.setEnabled( False )

        # Configure progress dialog.
        self.progress_dialog.setRange( 0, self.spin_evolve_iterations.value()*self.population.getIndividualCount() )
        self.progress_dialog.setValue( 0 )
        self.progress_dialog.setVisible( True )

        # Set job.
        indices = self.population_list.selectionModel().selectedRows()
        self.evolve_thread.add_job(
            self.spin_evolve_iterations.value(), indices,
            self.cb_cross_correlate.isChecked() )

    # Update evolution progress.
    def update_evolution_progress( self, completed, max ):
        if self.progress_dialog.maximum() != max:
            self.progress_dialog.setMaximum( max )
        self.progress_dialog.setValue( completed )

    # Finish evolution process.
    def finish_evolution( self ):
        # Update icons.
        for i in xrange(self.population_model.rowCount()):
            self.population_model.update_icon(i)
            index = self.population_list.model().index(i, 0)
            self.population_list.selectionModel().select(index, QItemSelectionModel.Select)
            self.population_list.selectionModel().select(index, QItemSelectionModel.Deselect)

        # Close dialog.
        self.progress_dialog.setVisible( False )

        # Reenable evolve button.
        self.cb_cross_correlate.setEnabled( True )
        self.spin_evolve_iterations.setEnabled( True )
        self.btn_evolve.setEnabled( True )

    def handle_context_menu( self, point ):
        # Show the context menu if items are selected.
        indices = self.population_list.selectionModel().selectedRows()
        if len(indices) > 0:
            action = self.image_menu.exec_( self.population_list.mapToGlobal(point) )

            # Save the selected images.
            if action == self.image_menu_save_image:
                file_name, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Image(s) as...", "",
                    "PNG Image (*.png)" );
                if file_name:
                    if file_name.length() - file_name.lastIndexOf('.png', -1, Qt.CaseInsensitive) == 4:
                        file_name.chop( 4 )
                    print "Save image(s) to: %s" % file_name
                    for index in indices:
                        index_file_name = "%s_%d.png" % (file_name, index.row())
                        print " - Saving image: %s..." % (index_file_name),
                        sys.stdout.flush()
                        distorted_image_map = self.population_model.distort(
                            index.row(), self.original_image )
                        distorted_image = QImage( distorted_image_map )
                        distorted_image.save( index_file_name )
                        print "Done."
                else:
                    print "Save image(s): Canceled"

            # Save the selected networks.
            elif action ==  self.image_menu_save_network:
                file_name, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Network(s) as...", "",
                    "XML File (*.xml)" );
                if file_name:
                    print "Save network(s) to: %s" % file_name
                    for index in indices:
                        index_file_name = "%s_%d.xml" % (file_name, index.row())
                        print " - Saving network: %s..." % (index_file_name),
                        sys.stdout.flush()
                        self.population.getIndividual(index.row()).saveToFile(
                            str(index_file_name), False )
                        print "Done."
                else:
                    print "Save network(s): Canceled"
