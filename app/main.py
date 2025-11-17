import sys
import os

os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

from PyQt5.QtWidgets import QApplication
from app.ui import MainWindow


def main():
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
