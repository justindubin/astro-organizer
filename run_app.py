from PySide2.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    # for i in range(100):
    #     window.print_to_console(f"This is line {i:03}")
    app.exec_()
