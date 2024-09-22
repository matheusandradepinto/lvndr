from PyQt5 import QtWidgets, QtCore

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, processor, video_manager):
        super().__init__()
        self.processor = processor
        self.video_manager = video_manager
        self.sliders = {}
        self.channel_checkboxes = []
        self.init_ui()
        self.apply_filter_checkbox.stateChanged.connect(self.update_apply_filter)

    def init_ui(self):
        self.setWindowTitle("Image Processor")
        self.setGeometry(100, 100, 500, 500)
        self.setMinimumSize(500, 900)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.load_stylesheet(".\\src\\style.css")
        central_widget.setStyleSheet("background-color: #000;")

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.layout = QtWidgets.QVBoxLayout()

        button_layout = QtWidgets.QHBoxLayout()
        self.start_webcam_button = QtWidgets.QPushButton("Start Webcam")
        self.start_webcam_button.setFixedSize(120, 30)  # Set fixed size for buttons
        self.start_webcam_button.clicked.connect(self.start_webcam)
        button_layout.addWidget(self.start_webcam_button)

        self.open_video_button = QtWidgets.QPushButton("Open Video")
        self.open_video_button.setFixedSize(120, 30)
        self.open_video_button.clicked.connect(self.open_video)
        button_layout.addWidget(self.open_video_button)

        self.reset_button = QtWidgets.QPushButton("Reset to Defaults")
        self.reset_button.setFixedSize(120, 30)
        self.reset_button.clicked.connect(self.reset_defaults)
        button_layout.addWidget(self.reset_button)

        self.layout.addLayout(button_layout)

        self.amplitude_slider = self.create_slider("Amplitude", 0, 200, self.processor.default_amplitude)
        self.smoothness_slider = self.create_slider("Smoothness", 1, 20, self.processor.default_smoothness)
        self.threshold_slider = self.create_slider("Threshold", 0, 100, self.processor.default_threshold)
        self.repeat_slider = self.create_slider("Repeat", 1, 4, self.processor.default_repeat)
        self.jpeg_quality_slider = self.create_slider("JPEG Quality", 0, 100, self.processor.default_jpeg_quality)
        self.blend_jpeg_quality_slider = self.create_slider("Blend JPEG Quality", 0, 100, self.processor.blend_jpeg_quality)
        self.brightness_slider = self.create_slider("Brightness", -100, 100, self.processor.default_brightness)
        self.saturation_slider = self.create_slider("Saturation", -100, 100, self.processor.default_saturation)
        self.contrast_slider = self.create_slider("Contrast", -100, 100, self.processor.default_contrast, decimal=True)
        self.base_weight_slider = self.create_slider("Base Weight", 0, 10, self.processor.default_base_weight, decimal=True)
        self.blend_weight_slider = self.create_slider("Blend Weight", 0, 10, self.processor.default_blend_weight, decimal=True)

        self.add_widgets_to_layout(self.layout)

        self.color_space_dropdown = self.create_dropdown("Color Space", list(self.processor.color_space_conversion.keys()))
        self.color_space_dropdown.currentTextChanged.connect(self.update_channel_checkboxes)

        self.blending_mode_dropdown = self.create_dropdown("Blending Mode", ["None", "Overlay", "Multiply", "Linear Burn", "Screen", "Darken", "Lighten", "Difference", "Exclusion", "Soft Light", "Hard Light", "Dodge", "Burn"])

        self.apply_filter_checkbox = QtWidgets.QCheckBox("Apply Filter")
        self.apply_filter_checkbox.setChecked(True)

        self.layout.addWidget(self.color_space_dropdown)
        self.layout.addWidget(self.blending_mode_dropdown)
        self.layout.addWidget(self.apply_filter_checkbox)

        central_widget.setLayout(self.layout)

        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        self.update_channel_checkboxes()

    def load_stylesheet(self, filename):
        with open(filename, "r") as file:
            style = file.read()
            self.setStyleSheet(style)

    def add_widgets_to_layout(self, layout):
        layout.setSpacing(2)  # Reduce spacing
        layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins

        layout.addWidget(self.amplitude_slider)
        layout.addWidget(self.smoothness_slider)
        layout.addWidget(self.threshold_slider)
        layout.addWidget(self.repeat_slider)
        layout.addWidget(self.jpeg_quality_slider)
        layout.addWidget(self.blend_jpeg_quality_slider)
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.saturation_slider)
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.base_weight_slider)
        layout.addWidget(self.blend_weight_slider)

    def create_slider(self, label, min_value, max_value, default_value, decimal=False):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(int(default_value) if not decimal else int(default_value * 10))
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider.setTickInterval(1)
        slider.setFixedHeight(20)  # Set fixed height for sliders

        slider.valueChanged.connect(lambda value: self.update_processor(label, value / 10.0 if decimal else value))

        slider_label = QtWidgets.QLabel(label)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(slider_label)
        layout.addWidget(slider)

        self.sliders[label] = slider

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def create_dropdown(self, label, options):
        dropdown = QtWidgets.QComboBox()
        dropdown.addItems(options)

        dropdown.currentTextChanged.connect(lambda value: self.update_processor(label, value))

        dropdown_label = QtWidgets.QLabel(label)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(dropdown_label)
        layout.addWidget(dropdown)

        dropdown.setFixedHeight(30)  # Set fixed height for dropdowns

        return dropdown

    def update_channel_checkboxes(self):
        for cb in self.channel_checkboxes:
            cb.setParent(None)

        self.channel_checkboxes.clear()

        color_space = self.color_space_dropdown.currentText()
        channel_names = {
            "RGB": ["R", "G", "B"],
            "HSV": ["H", "S", "V"],
            "HLS": ["H", "L", "S"],
            "LAB": ["L", "A", "B"],
            "LUV": ["L", "U", "V"],
            "XYZ": ["X", "Y", "Z"],
            "YCrCb": ["Y", "Cr", "Cb"],
            "YUV": ["Y", "U", "V"]
        }

        num_channels = len(channel_names.get(color_space, []))

        checkbox_layout = QtWidgets.QHBoxLayout()

        for i in range(num_channels):
            cb = QtWidgets.QCheckBox(channel_names[color_space][i])
            cb.setChecked(True)
            cb.stateChanged.connect(lambda state, index=i: self.update_selected_channels(index, state))
            self.channel_checkboxes.append(cb)
            checkbox_layout.addWidget(cb)

        self.layout.addLayout(checkbox_layout)

    def update_selected_channels(self, index, state):
        self.processor.selected_channels[index] = 1 if state == QtCore.Qt.Checked else 0

    def update_processor(self, label, value):
        if label == "Amplitude":
            self.processor.amplitude = value
        elif label == "Smoothness":
            self.processor.smoothness = value
        elif label == "Threshold":
            self.processor.threshold = value
        elif label == "Repeat":
            self.processor.repeat = value
        elif label == "JPEG Quality":
            self.processor.jpeg_quality = value
        elif label == "Blend JPEG Quality":
            self.processor.blend_jpeg_quality = value    
        elif label == "Brightness":
            self.processor.brightness = value
        elif label == "Saturation":
            self.processor.saturation = value
        elif label == "Contrast":
            self.processor.contrast = value
        elif label == "Base Weight":
            self.processor.base_weight = value
        elif label == "Blend Weight":
            self.processor.blend_weight = value
        elif label == "Color Space":
            self.processor.selected_color_space = value
        elif label == "Blending Mode":
            self.processor.selected_blending_mode = value
            self.processor.apply_blending = value != "None"

    def update_apply_filter(self, state):
        self.processor.apply_filter = state == QtCore.Qt.Checked

    def start_webcam(self):
        self.video_manager.start_webcam()

    def open_video(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            self.video_manager.start_video_file(file_path)

    def reset_defaults(self):
        self.processor.reset_to_defaults()
        
        self.sliders["Amplitude"].setValue(int(self.processor.default_amplitude))
        self.sliders["Smoothness"].setValue(int(self.processor.default_smoothness))
        self.sliders["Threshold"].setValue(int(self.processor.default_threshold))
        self.sliders["Repeat"].setValue(int(self.processor.default_repeat))
        self.sliders["JPEG Quality"].setValue(int(self.processor.default_jpeg_quality))
        self.sliders["Blend JPEG Quality"].setValue(int(self.processor.blend_jpeg_quality))
        self.sliders["Brightness"].setValue(int(self.processor.default_brightness))
        self.sliders["Saturation"].setValue(int(self.processor.default_saturation))
        self.sliders["Contrast"].setValue(int(self.processor.default_contrast * 10))
        self.sliders["Base Weight"].setValue(int(self.processor.default_base_weight * 10))
        self.sliders["Blend Weight"].setValue(int(self.processor.default_blend_weight * 10))
