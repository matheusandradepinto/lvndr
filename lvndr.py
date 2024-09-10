from src.image_processor import ImageProcessor
from src.video_source_manager import VideoSourceManager
from src.gui_manager import GUIManager

def main():
    processor = ImageProcessor()
    video_manager = VideoSourceManager(processor)
    GUIManager(processor, video_manager)

if __name__ == "__main__":
    main()
