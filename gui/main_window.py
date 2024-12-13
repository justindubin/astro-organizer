from PySide2 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Astro File Organizer")

        # Define basic layout
        self.root_window = QtWidgets.QWidget()
        self.base_layout = QtWidgets.QHBoxLayout()
        self.inputs_layout = QtWidgets.QVBoxLayout()
        self.outputs_layout = QtWidgets.QVBoxLayout()
        self.base_layout.addLayout(self.inputs_layout)
        self.base_layout.addLayout(self.outputs_layout)
        self.root_window.setLayout(self.base_layout)
        self.setCentralWidget(self.root_window)

        # Add Widgets - Inputs
        lbl_top = QtWidgets.QLabel("File Transfer Directories")
        self.inputs_layout.addWidget(lbl_top)
        self.directory_form = QtWidgets.QFormLayout()
        self.directory_form.addRow(QtWidgets.QLabel("Source Directory"), QtWidgets.QLineEdit())
        self.directory_form.addRow(QtWidgets.QLabel("Destination Directory"), QtWidgets.QLineEdit())
        self.inputs_layout.addLayout(self.directory_form)

        # Add Widgets - Outputs
        self.output_console = QtWidgets.QTextEdit()
        self.output_console.setReadOnly(True)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.output_console)
        self.outputs_layout.addWidget(scroll_area)

    def print_to_console(self, text: str) -> None:
        self.output_console.append(text)

    def clear_console(self) -> None:
        # TODO
        pass
