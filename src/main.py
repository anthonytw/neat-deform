from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys
import gui.GUIWindow
import cProfile
import sip

def main( ):
    # Create application and open window.
    sip.enableautoconversion(QtCore.QVariant, False)
    application = QApplication( sys.argv )
    guiWindow = gui.GUIWindow.Window()
    guiWindow.show()
    application.exec_()

if __name__ == "__main__":
    #cProfile.run('main( )', 'results')
    main()
