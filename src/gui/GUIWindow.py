from PyQt4.QtGui import *
from PopulationModel import *
import os.path

class Window(QMainWindow):
    def __init__( self, parent = None ):
        super(Window, self).__init__( parent )

        # Set default window size.
        self.setFixedSize( 545, 600 )

        # Initialize the list view for the distorted images.
        lv = QListView( )
        lv.setViewMode( QListView.IconMode )
        lv.setUniformItemSizes( True )
        lv.setSelectionRectVisible( True )
        lv.setMovement( QListView.Static )
        lv.setSelectionMode( QListView.MultiSelection )
        lv.setEditTriggers( QListView.NoEditTriggers )
        lv.setResizeMode( QListView.Adjust )
        lv.setIconSize( QSize(120, 120) )
        lv.setMinimumSize( 500, 385 )
        lv.setSpacing( 5 )
        self.population_list = lv

        # Create the population model.
        pm = PopulationModel( 12 )
        self.population_model = pm
        lv.setModel( pm )
        for i in xrange(12):
            self.population_model.update_item( i, DummyNetwork( i % 4 + 1 ) )

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

        param_layout = QHBoxLayout()
        param_layout.addLayout( image_layout )
        param_layout.addWidget( gb )

        # Initialize vertical central layout.
        central_layout = QVBoxLayout()
        central_layout.addLayout( param_layout )
        central_layout.addWidget( lv )
        central_widget = QFrame()
        central_widget.setLayout( central_layout )

        self.setCentralWidget( central_widget )

    def select_image( self ):
        file_name = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)" );
        if os.path.isfile(file_name):
            print "Loading image: %s..." % file_name
            self.original_image = QPixmap( file_name )
            scaled_image = self.original_image.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.population_model.set_original_image( scaled_image )
            self.original_image_label.setPixmap( scaled_image )
