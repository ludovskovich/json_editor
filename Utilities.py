from PySide2.QtWidgets import QFileDialog

class Utilities:
    def open_file_diag(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        filename = ""
        if dlg.exec_():
            filename = dlg.selectedFiles()[0]

        return filename

    def save_file_diag(self):
        dlg = QFileDialog()
        path = dlg.getSaveFileName(self, "Save File", "", "Json (*.json)")
        if path:
            print(path[0])
            return path


