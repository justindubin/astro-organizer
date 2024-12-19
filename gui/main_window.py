import functools
import os

from PySide2 import QtWidgets, QtCore, QtGui

from gui.thread_worker import Worker
from src.file_manager import FileManager


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Astro File Organizer")
        self.setFixedSize(950, 330)

        # Create a QThreadPool for threading operations
        self.threadpool = QtCore.QThreadPool()

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
        self.ent_source.setFixedWidth(420)
        self.ent_source.setReadOnly(True)
        self.ent_destination = QtWidgets.QLineEdit(self.fm.destination_path)
        self.ent_destination.setFixedWidth(420)
        self.ent_destination.setReadOnly(True)
        directory_form.addRow(QtWidgets.QLabel("Source:"), self.ent_source)
        directory_form.addRow(QtWidgets.QLabel("Destination:"), self.ent_destination)
        directory_form.setContentsMargins(0, 10, 0, 0)
        self.inputs_layout.addLayout(directory_form)

        # Add Widgets - Inputs - Directory Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_source = QtWidgets.QPushButton("Change Source")
        self.btn_source.clicked.connect(self.update_source)
        self.btn_destination = QtWidgets.QPushButton("Change Destination")
        self.btn_destination.clicked.connect(self.update_destination)
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
        self.btn_execute.clicked.connect(self.transfer_files)
        self.inputs_layout.addWidget(self.btn_execute)

        # Add Widgets - Outputs
        self.output_console = QtWidgets.QTextEdit()
        self.output_console.setTextColor(QtGui.QColor('#68ff68'))
        self.output_console.setReadOnly(True)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedWidth(370)
        scroll_area.setFixedHeight(300)
        scroll_area.setWidget(self.output_console)
        self.outputs_layout.addWidget(scroll_area)

    @staticmethod
    def validate_inputs(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            error_message = ''
            self.fm.recall_paths()
            dir_tuples = [('source', self.fm.source_path), ('destination', self.fm.destination_path)]
            for dir_name, dir_path in dir_tuples:

                # 1. Check that both directories were specified
                if dir_path == '':
                    error_message = f'No {dir_name} directory specified!'
                    break

                # 2. Verify that the specified source directory exists
                elif dir_name == 'source':
                    if not os.path.isdir(dir_path):
                        error_message = f'The specified source directory does not exist!'
                        break

                    # 3. Verify the source directory contains required folders
                    for folder_name in self.fm.FOLDER_MAP.keys():
                        check_path = os.path.join(dir_path, folder_name)
                        if not os.path.isdir(check_path):
                            error_message = f'The source directory is missing a required folder: "{folder_name}"'
                            break

            if not error_message:
                func(self, *args, **kwargs)
            else:
                dlg = QtWidgets.QMessageBox(self)
                dlg.setText(error_message)
                dlg.setIcon(QtWidgets.QMessageBox.Critical)
                dlg.exec_()
            return
        return wrapper

    def print_to_console(self, text: str) -> None:
        self.output_console.append(text)

    def update_source(self) -> None:
        directory = self.select_directory('source')
        self.fm.update_paths(source_path=directory)
        self.ent_source.setText(directory)
        self.print_to_console(f"Source directory updated:\n  -> {directory}\n")

    def update_destination(self) -> None:
        directory = self.select_directory('destination')
        self.fm.update_paths(destination_path=directory)
        self.ent_destination.setText(directory)
        self.print_to_console(f"Destination directory updated:\n  -> {directory}\n")

    def select_directory(self, dir_type: str) -> str:
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, f"Select the {dir_type} directory")
        return directory

    def throw_script_error(self, error_msg: str) -> None:
        # Update the console
        self.output_console.setTextColor(QtGui.QColor('#fc3d21'))
        self.print_to_console("\nPROCESS FAILED\n")
        self.output_console.setTextColor(QtGui.QColor('#68ff68'))

        # Throw error window
        dlg = QtWidgets.QMessageBox(self)
        dlg.setText(error_msg)
        dlg.setIcon(QtWidgets.QMessageBox.Critical)
        dlg.exec_()

    @validate_inputs
    def transfer_files(self):
        target_name = self.ent_target.text()
        shoot_date = self.ent_date.text()
        cut_paste = self.chk_delete.isChecked()

        worker = Worker(self.fm.transfer_files, target_name, shoot_date, cut_paste)
        worker.signals.progress.connect(self.print_to_console)
        worker.signals.error.connect(self.throw_script_error)
        self.threadpool.start(worker)
