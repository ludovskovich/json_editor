from PySide2.QtWidgets import QApplication
from MainWindow import MainWindow
import sys

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()