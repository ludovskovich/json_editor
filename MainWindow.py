from PySide2.QtWidgets import QWidget, QMainWindow, QAction, QScrollArea, QGridLayout, QVBoxLayout, QHBoxLayout, \
    QLineEdit, QPushButton, QMessageBox
from PySide2.QtGui import QIcon
from JsonReader import JsonReader
from Utilities import Utilities
from GroupContainer import WidgetContainer
import pydash as Pydash

class MainWindow(QMainWindow):
    openedData = ""
    grid = None
    textFields = {}
    currentModifications = None
    newEntryIndex = 0
    currentKeys = []
    path = "No File Loaded"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Json File Editor")
        self.setGeometry(100, 100, 680, 840)
        self.create_menu()

        #Creating basic fields
        self.openedData = {}
        startingItem = {"new": "file"}
        self.openedData["Root"] = startingItem
        self.refresh_file()

    # Recreates all fields and set them in a beautiful scroll area
    # probably has some performance impact, so don't call too often
    def refresh_file(self):
        #Apply currentModifications to openedData
        self.textFields.clear()
        widget = QWidget()
        data = self.display_json_object_layout(self.openedData, self.path, widget, self.textFields)
        widget.setLayout(data.layout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(widget)
        self.setCentralWidget(scrollArea)

    # Apply the changes of the modified dictionary inside the data imported from the json file
    def apply_changes(self, currentDict, openedData):
        for key in currentDict.keys():
            if type(currentDict[key]) == dict:
                openedData[key.text()] = {}
                self.apply_changes(currentDict[key], openedData[key.text()])
            elif type(currentDict[key]) == list:
                openedData[key.text()] = []
                for entry in currentDict[key]:
                    openedData[key.text()].append(entry.text())
            else:
                openedData[key.text()] = currentDict[key].text()

    # finds the "path" of keys of the sent values.
    # returns them as a list
    def find_keys(self, valueToLookFor, dictToSearchIn):
        returnedKeys = []
        for key in dictToSearchIn.keys():
            if dictToSearchIn[key] == valueToLookFor:
                returnedKeys.append(key)
            else:
                if type(dictToSearchIn[key]) == dict:
                    newKeys = self.find_keys(valueToLookFor, dictToSearchIn[key])

                    if len(newKeys) > 0:
                        returnedKeys.append(key)
                        for _key in newKeys:
                            returnedKeys.append(_key)

        return returnedKeys

    # This function uses Pydash to set the value inside nested dictionaries using a path of keys inside a list
    # Using Pydash saves a lot of time doing my own method doing the iterations
    # source : https://pydash.readthedocs.io/en/latest/api.html
    def nested_set(self, dictToUse, keys, value):
        Pydash.set_(dictToUse, keys, value)

    # Add a new entry depending on the type on the data structure
    def add_entry(self, i):
        self.openedData.clear()
        self.apply_changes(self.textFields, self.openedData)
        self.newEntryIndex += 1

        keys = self.find_keys(self.currentModifications, self.openedData)
        if i.text() == "New Key/Value":
            self.currentModifications[str(self.newEntryIndex)] = "new entry"
            print("New Key Value")
        elif i.text() == "New List":
            self.currentModifications[str(self.newEntryIndex)] = ["new entry", "new entry 2"]
            print("New List")
        elif i.text() == "New Dictionary":
            self.currentModifications[str(self.newEntryIndex)] = {"new": "entry"}
            print("New dictionary")
        elif i.text() == "New Field":
            self.currentModifications.append("new entry")

        self.nested_set(self.openedData, keys, self.currentModifications)
        self.refresh_file()

    # Add "New Entry" inside a list as a new element
    def add_entry_list(self):
        self.openedData.clear()
        self.apply_changes(self.textFields, self.openedData)
        self.newEntryIndex += 1

        keys = self.find_keys(self.currentModifications, self.openedData)
        self.currentModifications.append("New Entry")
        self.nested_set(self.openedData, keys, self.currentModifications)
        self.refresh_file()

    # Display the add menu when clicking an object.
    # Automatically add a single textfield when it's a list
    def show_add_menu(self, openedData):
        self.currentModifications = openedData

        if type(openedData) == list:
            self.add_entry_list()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Add Element")
            msgBox.setText("Select the type of element you which to add")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Open | QMessageBox.Save)
            msgBox.setButtonText(QMessageBox.Ok, "New Key/Value")
            msgBox.setButtonText(QMessageBox.Open, "New List")
            msgBox.setButtonText(QMessageBox.Save, "New Dictionary")
            msgBox.buttonClicked.connect(self.add_entry)
            x = msgBox.exec_()

    # Delete a specified object from the specified dictionary
    # then reloads the files to apply the changes
    def remove_object(self, data, objectToRemove):
        if objectToRemove == "Root":
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Operation Denied")
            msgBox.setText("Cannot remove the Root node")
            x = msgBox.exec_()
            return
        if type(data) == list:
            data.remove(objectToRemove)
        elif type(data) == dict:
            del(data[objectToRemove])

        self.currentModifications = data
        keys = self.find_keys(self.currentModifications, self.openedData)
        self.nested_set(self.openedData, keys, self.currentModifications)
        self.refresh_file()


    # Returns a lambda using the specified object
    def get_add_function(self, object):
        return lambda: self.show_add_menu(object)

    # Returns a lambda using the specified objects
    def get_remove_function(self, dict, objectToRemove):
        return lambda: self.remove_object(dict, objectToRemove)


    # Gets called when a text field is edited
    # Can probably replace that with returnPressed to confirm the input.
    def on_field_changes(self):
        self.apply_changes(self.textFields, self.openedData)
        self.refresh_file()

    def on_header_field_changes(self):
        for key in self.textFields:
            print ("")


    # This function generate all the LineEdit fields from a dictionary / list.
    # It's recursive when finding a dictionary inside "object"
    # returns the container that contains all the fields
    def display_json_object_layout(self, object, title, widget, textFieldsDict = None):
        vLayout = QVBoxLayout()
        widgetContainer = WidgetContainer(title)

        for key in object:
            HLayout = QHBoxLayout()
            labelLeft = QLineEdit()
            labelLeft.setText(str(key))
            labelLeft.editingFinished.connect(self.on_field_changes)
            self.currentKeys.append(key)
            if type(object[key]) == list:
                subVLayout = QVBoxLayout()
                index = 0
                listContainer = WidgetContainer(key)
                textFieldsDict[listContainer.header.textFieldLabel] = []
                print (listContainer.header.textFieldLabel.text())
                HLayout.addWidget(listContainer)
                containerLayout = QGridLayout(listContainer.contentWidget)
                addListElement = self.get_add_function(object[key])

                # Linking add remove to header
                addListParentFunction = self.get_add_function(object)
                removeListParentFunction = self.get_remove_function(object, str(key))
                listContainer.header.addButton.clicked.connect(addListParentFunction)
                listContainer.header.removeButton.clicked.connect(removeListParentFunction)

                # Linking text field event
                listContainer.titleTextField.editingFinished.connect(self.on_header_field_changes)

                # List Viewer Setup
                for value in object[key]:
                    textField = QLineEdit()
                    textField.setText(str(value))
                    subVLayout.addWidget(textField)
                    textField.editingFinished.connect(self.on_field_changes)

                    # add / remove Button
                    addButton = QPushButton("Add")
                    addButton.clicked.connect(addListElement)

                    removeButton = QPushButton("Remove")
                    removeListElement = self.get_remove_function(object[key], value)
                    removeButton.clicked.connect(removeListElement)

                    containerLayout.addWidget(addButton, index, 1)
                    containerLayout.addWidget(removeButton, index, 2)

                    # HLayout.addLayout(subVLayout)
                    textFieldsDict[listContainer.header.textFieldLabel].append(textField)
                    containerLayout.addWidget(textField, index, 0)
                    index += 1

            elif type(object[key]) == dict:
                # call the same function and return the new container created
                textFieldsDict[labelLeft] = {}
                self.currentKeys.clear()
                newLayout = self.display_json_object_layout(object[key], str(key), widget, textFieldsDict[labelLeft])

                # swap the key for the text fields generated in the new layout
                # new key is the QLineEdit of the header
                textFieldsDict[newLayout.header.textFieldLabel] = textFieldsDict[labelLeft]
                del textFieldsDict[labelLeft]

                addParentFunction = self.get_add_function(object)
                removeParentFunction = self.get_remove_function(object, str(key))
                newLayout.header.addButton.clicked.connect(addParentFunction)
                newLayout.header.removeButton.clicked.connect(removeParentFunction)
                newLayout.titleTextField.editingFinished.connect(self.on_header_field_changes)
                vLayout.addWidget(newLayout)
            else:
                textField = QLineEdit()
                textField.setText(str(object[key]))
                textFieldsDict[labelLeft] = textField
                textField.editingFinished.connect(self.on_field_changes)

                # add / remove Button
                addElementFunction = self.get_add_function(object)
                addButton = QPushButton("Add")
                addButton.clicked.connect(addElementFunction)
                removeButton = QPushButton("Remove")
                removeElement = self.get_remove_function(object, key)
                removeButton.clicked.connect(removeElement)

                HLayout.addWidget(labelLeft)
                HLayout.addWidget(textField)
                HLayout.addWidget(addButton)
                HLayout.addWidget(removeButton)

            vLayout.addLayout(HLayout)

        containerLayout = QGridLayout(widgetContainer.contentWidget)
        containerLayout.addLayout(vLayout, 0, 0)
        return widgetContainer

    # Shuts down the window
    def exit_app(self):
        self.close()

    # Pops a path window and opens a json file at the specified path
    # then generates the necessary fields
    def open_file(self):
        path = Utilities.open_file_diag(self)
        if len(path) > 0 :
            self.textFields.clear()
            self.textFields = {}
            self.openedData = {}
            jsonFile = JsonReader.open_json_as_dict(self, path)
            if "Root" not in jsonFile.keys():
                self.openedData["Root"] = JsonReader.open_json_as_dict(self, path)
            else :
                self.openedData = jsonFile

            self.path = path
            self.refresh_file()

    # Reapply the modifications of the text fields to the loaded data
    # then saves it in a json file (pops a path window)
    def save_file(self):
        self.openedData.clear()
        self.openedData = {}
        self.apply_changes(self.textFields, self.openedData)
        path = Utilities.save_file_diag(self)
        JsonReader.save_json(self, str(path[0]), self.openedData)

    # Create the toolbar at the top and link their functions
    def create_menu(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")

        # FILE MENU
        openAction = QAction(QIcon('images/open.png'), "Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.open_file)

        saveAction = QAction(QIcon('images/save.png'), "Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.save_file)

        exitAction = QAction(QIcon('images/exit.png'), "Exit", self)
        exitAction.setShortcut("Ctrl+Q")

        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        exitAction.triggered.connect(self.exit_app)
        fileMenu.addAction(exitAction)
