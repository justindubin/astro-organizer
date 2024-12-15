from PySide2 import QtWidgets, QtCore, QtGui
from src.file_manager import FileManager


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Astro File Organizer")
        self.setFixedSize(950, 330)

        # Create a file manager
        self.fm = FileManager()

        # Define basic layout
        self.root_window = QtWidgets.QWidget()
        self.base_layout = QtWidgets.QHBoxLayout()
        self.inputs_layout = QtWidgets.QVBoxLayout()
        self.inputs_layout.setSpacing(10)
        self.inputs_layout.setContentsMargins(5, 5, 5, 5)
        self.outputs_layout = QtWidgets.QVBoxLayout()
        self.outputs_layout.setContentsMargins(5, 5, 5, 5)
        self.base_layout.addLayout(self.inputs_layout)
        self.base_layout.addLayout(self.outputs_layout)
        self.root_window.setLayout(self.base_layout)
        self.setCentralWidget(self.root_window)

        # Add Widgets - Inputs - Directory Form
        directory_form = QtWidgets.QFormLayout()
        self.ent_source = QtWidgets.QLineEdit(self.fm.source_path)
        self.ent_source.setFixedWidth(400)
        self.ent_source.setReadOnly(True)
        self.ent_destination = QtWidgets.QLineEdit(self.fm.destination_path)
        self.ent_destination.setFixedWidth(400)
        self.ent_destination.setReadOnly(True)
        directory_form.addRow(QtWidgets.QLabel("Source:"), self.ent_source)
        directory_form.addRow(QtWidgets.QLabel("Destination:"), self.ent_destination)
        directory_form.setContentsMargins(0, 10, 0, 0)
        self.inputs_layout.addLayout(directory_form)

        # Add Widgets - Inputs - Directory Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_source = QtWidgets.QPushButton("Change Source")
        self.btn_destination = QtWidgets.QPushButton("Change Destination")
        btn_layout.addWidget(self.btn_source)
        btn_layout.addWidget(self.btn_destination)
        btn_layout.setContentsMargins(0, 0, 0, 20)
        self.inputs_layout.addLayout(btn_layout)

        # Add Widgets - Inputs - Target Form
        target_form = QtWidgets.QFormLayout()
        self.ent_target = QtWidgets.QLineEdit()
        self.ent_target.setFixedWidth(200)
        self.ent_date = QtWidgets.QLineEdit()
        self.ent_date.setFixedWidth(200)
        self.ent_date.setPlaceholderText("YYMMDD")
        target_form.addRow("Target Name:", self.ent_target)
        target_form.addRow("Shoot Date:", self.ent_date)
        target_form.setContentsMargins(0, 5, 0, 0)
        self.inputs_layout.addLayout(target_form)

        # Add Widgets - Inputs - Delete From Source Toggle
        self.chk_delete = QtWidgets.QCheckBox(text="Delete from Source? (Cut/Paste)")
        self.chk_delete.setChecked(True)
        self.inputs_layout.addWidget(self.chk_delete)

        # Add Widgets - Inputs - Execute Button
        self.btn_execute = QtWidgets.QPushButton("Transfer Files")
        self.inputs_layout.addWidget(self.btn_execute)

        # Add Widgets - Outputs
        self.output_console = QtWidgets.QTextEdit()
        self.output_console.setReadOnly(True)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(400)
        scroll_area.setFixedHeight(300)
        scroll_area.setWidget(self.output_console)
        self.outputs_layout.addWidget(scroll_area)

    def print_to_console(self, text: str) -> None:
        self.output_console.append(text)

    def clear_console(self) -> None:
        # TODO
        pass
