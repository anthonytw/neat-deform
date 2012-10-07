from PyQt4.QtGui import QApplication
import sys
import gui.GUIWindow
import cProfile

def main( ):
    # Create application and open window.
    application = QApplication( sys.argv )
    guiWindow = gui.GUIWindow.Window()
    guiWindow.show()
    application.exec_()

if __name__ == "__main__":
    #cProfile.run('main( )', 'results')
    main()
