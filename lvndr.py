from src.image_processor import ImageProcessor
from src.video_source_manager import VideoSourceManager
from PyQt5 import QtWidgets, QtCore
from src.gui_manager import MainWindow
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    processor = ImageProcessor()
    video_manager = VideoSourceManager(processor)
    gui = MainWindow(processor, video_manager)
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
