from PySide6.QtWidgets import QApplication
from src.MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication()

    main_window = MainWindow()

    main_window.resize(700, 800)
    main_window.show()
    app.exec()