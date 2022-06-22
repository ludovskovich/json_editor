from PySide2 import QtWidgets, QtGui

# This part has been taken from the internet
# it's a widget that act as a container and can be collapsed/extended
# source : https://github.com/aronamao/PySide2-Collapsible-Widget

class GroupTitle(QtWidgets.QWidget):
    textFieldLabel = None
    addButton = None
    removeButton = None

    def __init__(self, title, content):
        super(GroupTitle, self).__init__()

        self.content = content
        self.open_icon = QtGui.QPixmap("images/unfolded.png")
        self.closed_icon = QtGui.QPixmap("images/folded.png")

        stacked = QtWidgets.QStackedLayout(self)
        stacked.setStackingMode(QtWidgets.QStackedLayout.StackAll)

        # background of the header
        bg = QtWidgets.QLabel()
        bg.setStyleSheet("QLabel{border-radius:2px}")

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)

        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(self.open_icon)
        layout.addWidget(self.icon)
        layout.setContentsMargins(11, 0, 11, 0)

        font = QtGui.QFont()
        font.setBold(True)
        label = QtWidgets.QLineEdit(str(title))
        label.setFont(font)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(label)
        self.addButton = QtWidgets.QPushButton("Add")
        self.removeButton = QtWidgets.QPushButton("Remove")
        hLayout.addWidget(self.addButton)
        hLayout.addWidget(self.removeButton)

        layout.addLayout(hLayout)
        #layout.addWidget(label)
        layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        stacked.addWidget(widget)
        stacked.addWidget(bg)
        bg.setMinimumHeight(layout.sizeHint().height() * 1.5)
        self.textFieldLabel = label

    def expand(self):
        self.content.setVisible(True)
        self.setMaximumHeight(100000)
        self.icon.setPixmap(self.open_icon)

    def collapse(self):
        self.content.setVisible(False)
        self.setMaximumHeight(20)
        self.icon.setPixmap(self.closed_icon)

    def mousePressEvent(self, *args):
        self.expand() if not self.content.isVisible() else self.collapse()


class WidgetContainer(QtWidgets.QWidget):
    titleTextField = None
    header = None

    def __init__(self, name):
        super(WidgetContainer, self).__init__()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget = QtWidgets.QWidget()
        self.header = GroupTitle(name, self.content_widget)
        self.titleTextField = self.header.textFieldLabel
        self._layout.addWidget(self.header)
        self._layout.addWidget(self.content_widget)

        self.collapse = self.header.collapse()
        self.expand = self.header.expand()
        self.toggle = self.header.mousePressEvent()

    @property
    def contentWidget(self):
        return self.content_widget

    @property
    def layout(self):
        return self._layout

    def get_add_button(self):
        return self.header.addButton

    def get_remove_button(self):
        return self.header.removeButton
