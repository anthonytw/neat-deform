from PyQt4.QtGui import *
from PopulationModel import *

class Window(QMainWindow):
    def __init__( self, parent = None ):
        super(Window, self).__init__( parent )

        # Set default window size.
        self.setFixedSize( 800, 800 )

        # Initialize the list view for the distorted images.
        lv = QListView( )
        lv.setViewMode( QListView.IconMode )
        lv.setUniformItemSizes( True )
        lv.setSelectionRectVisible( True )
        lv.setMovement( QListView.Static )
        lv.setSelectionMode( QListView.MultiSelection )
        lv.setEditTriggers( QListView.NoEditTriggers )
        lv.setResizeMode( QListView.Adjust )
        lv.setIconSize( QSize(180, 180) )
        lv.setMinimumSize( 760, 570 )
        lv.setSpacing( 5 )
        self.population_list = lv

        # Create the population model.
        pm = PopulationModel( 12 )
        self.population_model = pm
        pm.set_original_image( QPixmap("birfday_lolcat_h.jpg") )
        for i in xrange(10):
            pm.update_item( i, DummyNetwork( DummyNetwork.OneToOne ) )
        for i in xrange(10, 12):
            pm.update_item( i, DummyNetwork( DummyNetwork.Flip ) )

        lv.setModel( pm )

        # Initialize widgets for displaying the graphic and for choosing
        # a new base image.
        btn_select_image = QPushButton( "Load Image" )
        lbl_image = QLabel( "Nothing loaded" )
        lbl_image.setFixedSize( 180, 180 )
        lbl_image.setPixmap( pm.original_image.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation) )
        self.original_image_label = lbl_image
        image_layout = QVBoxLayout()
        image_layout.addWidget( btn_select_image )
        image_layout.addWidget( lbl_image )

        # Initialize a horizontal layout for the parameters.
        param_layout = QHBoxLayout()
        param_layout.addLayout( image_layout )

        # Initialize vertical central layout.
        central_layout = QVBoxLayout()
        central_layout.addLayout( param_layout )
        central_layout.addWidget( lv )
        central_widget = QFrame()
        central_widget.setLayout( central_layout )

        self.setCentralWidget( central_widget )
