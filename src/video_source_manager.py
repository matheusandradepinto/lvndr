import cv2
import threading

class VideoSourceManager:
    def __init__(self, processor):
        self.processor = processor
        self.capture = None
        self.running = False
        self.lock = threading.Lock()
        self.thread = None
        self.window_name = "Processed Video"

    def start_webcam(self):
        self.stop()  # Stop any ongoing capture before starting a new one
        self.capture = cv2.VideoCapture(0)  
        if not self.capture.isOpened():
            print("Error: Could not open webcam.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.start()

    def start_video_file(self, file_path):
        self.stop()  # Stop any ongoing capture before starting a new one
        self.capture = cv2.VideoCapture(file_path)  
        if not self.capture.isOpened():
            print("Error: Could not open video file.")
            return

        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, args=(True, width, height)) 
        self.thread.start()

    def stop(self):
        with self.lock:
            if self.running:
                self.running = False  # Set running to False to stop the loop
                # Release the capture device if it's open
                if self.capture is not None:
                    if self.capture.isOpened():
                        self.capture.release()  
                    self.capture = None  

                # Wait for the thread to finish
                if self.thread is not None:
                    self.thread.join()  
                    self.thread = None  # Reset the thread reference

                cv2.destroyAllWindows()  

    def _capture_loop(self, loop_video=False, width=640, height=480):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)  
        cv2.resizeWindow(self.window_name, width, height)  

        while True:
            with self.lock:
                if not self.running:
                    break
                if not self.capture or not self.capture.isOpened():
                    break

            ret, frame = self.capture.read()

            if not ret:
                if loop_video and self.running:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  
                    continue
                else:
                    break

            processed_frame = self.processor.process_frame(frame)
            cv2.imshow(self.window_name, processed_frame)

            # Check for 'q' key to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Instead of stopping immediately, set running to False
                with self.lock:
                    self.running = False
                break

        # Clean up after exiting the loop
        self.clean_up()

    def clean_up(self):
        """Ensure everything is cleaned up properly."""
        with self.lock:
            if self.capture is not None:
                self.capture.release()  # Release the webcam
                self.capture = None  # Reset capture
        cv2.destroyAllWindows()  # Close any OpenCV windows

    def close(self):
        self.stop()  # Ensure the resources are released when closing
