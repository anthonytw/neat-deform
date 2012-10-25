from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PopulationModel import *
import os.path
import sys
import PyHyperNEAT as neat
from datetime import datetime

class Window(QMainWindow):
    def __init__( self, parent = None ):
        super(Window, self).__init__( parent )

        ### Experiment Configuration
        # ATW: TODO: When we start getting reasonable distortions, there
        # needs to be a method to reload an old population. For now we'll
        # always make a new one.

        self.experiment_data_dir  = "../external/HyperNEAT/NE/HyperNEAT/out/data"
        self.date_specifier = datetime.now().strftime("%y%m%d_%H%M%S")

        # Initialize HyperNEAT.
        neat.initialize()

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

        #pop-up menu
        lv.setContextMenuPolicy(Qt.CustomContextMenu)
        lv.connect(lv, SIGNAL('customContextMenuRequested (const QPoint&)'),self.onContext)

        # Create the population model.
        pm = PopulationModel( population_size )
        self.population_model = pm
        lv.setModel( pm )
        for i in xrange(population_size):
            self.population_model.update_item( i, DummyNetwork( i % 4 + 1 ) )

        # Monitor population list selection changes.
        self.connect(
            lv.selectionModel(),
            SIGNAL('selectionChanged(const QItemSelection &, const QItemSelection &)'),
            self.handle_listview_change )

        # Initialize widgets for displaying the graphic and for choosing
        # a new base image.
        btn_select_image = QPushButton( "Load Image" )
        self.connect( btn_select_image, SIGNAL('released()'), self.select_image )
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
        tw.setHorizontalHeaderLabels(QString("Parameter;Value").split(';'))
        tw.setColumnWidth( 0, 350 )
        tw.horizontalHeader().setStretchLastSection( True )
        self.connect( tw, SIGNAL('itemChanged(QTableWidgetItem *)'), self.handle_parameter_change )
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
        btn_evolve = QPushButton( "Evolve" )
        self.connect( btn_evolve, SIGNAL('released()'), self.evolve_image )
        btn_evolve.setEnabled( False )
        self.btn_evolve = btn_evolve

        control_layout = QHBoxLayout()
        control_layout.addWidget( btn_evolve )

        # Initialize vertical central layout.
        central_layout = QVBoxLayout()
        central_layout.addLayout( param_layout )
        central_layout.addWidget( lv )
        central_layout.addLayout( control_layout )
        central_widget = QFrame()
        central_widget.setLayout( central_layout )

        self.setCentralWidget( central_widget )

        ### Initialization

        # Handle command line parameters.
        if len(sys.argv) >= 2:
            self.select_image(sys.argv[1])

        # Generate first population.
        self.get_next_generation( initializing=True )

    # Destructor.
    def __del__( self ):
        # Save best population.
        self.experiment.saveBest()

        # Cleanup HyperNEAT.
        neat.cleanup()

    # Update a parameter value.
    def handle_parameter_change( self, parameter ):
        column = parameter.column()
        if column == 1:
            row = parameter.row()
            parameter_name = self.globals.getParameterName( row )
            current_value = self.globals.getParameterValue( parameter_name )
            (new_value, is_a_float) = parameter.data(Qt.EditRole).toFloat()
            if is_a_float:
                self.globals.setParameterValue( parameter_name, new_value )
            else:
                parameter.setText( "%.2f" % current_value )

    # Choose a new image to work with.
    def select_image( self, file_name = None ):
        if file_name == None:
            file_name = QFileDialog.getOpenFileName(
                self,
                "Select Image", "",
                "Image Files (*.png *.jpg *.bmp)" );
        if os.path.isfile(file_name):
            print "Loading image: %s..." % file_name
            self.population_list.setEnabled( True )
            self.original_image = QPixmap( file_name )
            scaled_image = self.original_image.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.population_model.set_original_image( scaled_image )
            self.original_image_label.setPixmap( scaled_image )

    # Handles listview changes. We only care if elements are selected.
    def handle_listview_change( self, selected, deselected ):
        evolve_btn_enabled = self.population_list.selectionModel().hasSelection()
        if self.btn_evolve.isEnabled() != evolve_btn_enabled:
            self.btn_evolve.setEnabled( evolve_btn_enabled )

    # Get next generation.
    def get_next_generation( self, initializing = False ):
        if not initializing:
            self.experiment.produceNextGeneration()
        self.experiment.preprocessPopulation()
        self.population = self.experiment.pythonEvaluationSet()

        # Update population model.
        if self.population.getIndividualCount() != self.population_model.rowCount():
            print "WARNING! Discrepency between population size and model size! Things might blow up. Wear a hardhat."

        for i in xrange(self.population_model.rowCount()):
            print "Updating network %2d with new network..." % i,
            index = self.population_list.model().index(i, 0)
            self.population_list.selectionModel().select(index, QItemSelectionModel.Select)
            individual = self.population.getIndividual(i)
            network = individual.spawnFastPhenotypeStack()
            self.population_model.update_item(i, network)
            self.population_list.selectionModel().select(index, QItemSelectionModel.Deselect)
            self.population_list.repaint()
            print "Done"

    # Evolve the image with the selected individuals.
    def evolve_image( self ):
        # Add a reward to all selected elements.
        indices = self.population_list.selectionModel().selectedRows()
        for index in indices:
            self.population.getIndividual(index.row()).reward( 100 )

        # Deselect elements.
        self.population_list.selectionModel().clearSelection()

        # Finish evaluation.
        self.experiment.finishEvaluations()

        # Get next generation.
        self.get_next_generation()


    def onContext(self,point):
       # Create a menu
       menu = QMenu("Menu", self)
       save_image = menu.addAction("Save Selected Images")
       # Show the context menu.
       action = menu.exec_(self.population_list.mapToGlobal(point))
       if action ==save_image:
           self.population_model.save_image(self.population_list.selectionModel().selectedRows())

