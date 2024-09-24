import json
import re
import os
from PyQt5 import QtWidgets, QtCore

def sanitize_filename(filename):
        # Define the pattern for invalid characters (Windows reserved characters for file names)
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
class FloatSlider(QtWidgets.QWidget):
    def __init__(self, label, min_value, max_value, default_value, step=0.1):
        super().__init__()

        self.layout = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel(label)
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.spinbox.setRange(min_value, max_value)
        self.spinbox.setValue(default_value)
        self.spinbox.setSingleStep(step)
        self.spinbox.setDecimals(2)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(int(min_value * 100), int(max_value * 100))
        self.slider.setValue(int(default_value * 100))
        self.slider.setTickInterval(int(step * 100))

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

        # Synchronize slider and spinbox
        self.slider.valueChanged.connect(self.slider_changed)
        self.spinbox.valueChanged.connect(self.spinbox_changed)

    def slider_changed(self, value):
        self.spinbox.setValue(value / 100)

    def spinbox_changed(self, value):
        self.slider.setValue(int(value * 100))

    def set_value(self, value):
        """Set both slider and spinbox values programmatically."""
        self.slider.setValue(int(value * 100))
        self.spinbox.setValue(value)

    def value(self):
        """Return the current value."""
        return self.spinbox.value()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, processor, video_manager):
        super().__init__()
        self.processor = processor
        self.video_manager = video_manager
        self.sliders = {}
        self.channel_checkboxes = []
        self.init_ui()
        self.apply_filter_checkbox.stateChanged.connect(self.update_apply_filter)
        self.apply_wordpad_glitch_checkbox.stateChanged.connect(self.update_apply_wordpad_glitch)

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

        self.create_button_layout()
        self.create_preset_widget()
        self.add_widgets_to_layout(self.layout)
        self.create_color_space_dropdown()
        self.create_blending_mode_dropdown()
        self.create_checkbox_layout()

        central_widget.setLayout(self.layout)
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        self.update_channel_checkboxes()

    def load_stylesheet(self, path):
        """Loads the stylesheet from the given file path and applies it to the application."""
        try:
            with open(path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Stylesheet file not found: {path}")

    def create_button_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        self.start_webcam_button = QtWidgets.QPushButton("Start Webcam")
        self.start_webcam_button.setFixedSize(120, 30)
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
    
    def create_preset_widget(self):
        self.preset_layout = QtWidgets.QHBoxLayout()
        
        # Input for preset name
        self.preset_name_input = QtWidgets.QLineEdit()
        self.preset_name_input.setPlaceholderText("Enter preset name")
        self.preset_layout.addWidget(self.preset_name_input)
        
        # Save Preset Button
        self.save_preset_button = QtWidgets.QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        self.preset_layout.addWidget(self.save_preset_button)

        # Load Preset Button
        self.load_preset_button = QtWidgets.QPushButton("Load Preset")
        self.load_preset_button.clicked.connect(self.load_preset)
        self.preset_layout.addWidget(self.load_preset_button)

        self.layout.addLayout(self.preset_layout)

    def add_widgets_to_layout(self, layout):
        layout.setSpacing(2)  # Reduce spacing
        layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins

        self.amplitude_slider = self.create_float_slider("Amplitude", 0, 200, self.processor.default_amplitude)
        self.smoothness_slider = self.create_float_slider("Smoothness", 1, 20, self.processor.default_smoothness, step=0.1)
        self.threshold_slider = self.create_float_slider("Threshold", 0, 100, self.processor.default_threshold)
        self.repeat_slider = self.create_float_slider("Repeat", 1, 4, self.processor.default_repeat)
        self.jpeg_quality_slider = self.create_float_slider("JPEG Quality", 0, 100, self.processor.default_jpeg_quality)
        self.blend_jpeg_quality_slider = self.create_float_slider("Blend JPEG Quality", 0, 100, self.processor.blend_jpeg_quality)
        self.brightness_slider = self.create_float_slider("Brightness", -100, 100, self.processor.default_brightness, step=1)
        self.saturation_slider = self.create_float_slider("Saturation", -100, 100, self.processor.default_saturation, step=1)
        self.contrast_slider = self.create_float_slider("Contrast", -100, 100, self.processor.default_contrast, step=0.1)
        self.base_weight_slider = self.create_float_slider("Base Weight", 0, 10, self.processor.default_base_weight, step=0.1)
        self.blend_weight_slider = self.create_float_slider("Blend Weight", 0, 10, self.processor.default_blend_weight, step=0.1)

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

    def create_color_space_dropdown(self):
        self.color_space_dropdown = self.create_dropdown("Color Space", list(self.processor.color_space_conversion.keys()))
        self.color_space_dropdown.currentTextChanged.connect(self.update_channel_checkboxes)
        self.layout.addWidget(self.color_space_dropdown)

    def create_blending_mode_dropdown(self):
        self.blending_mode_dropdown = self.create_dropdown("Blending Mode", ["None", "Overlay", "Multiply", "Linear Burn", "Screen", "Darken", "Lighten", "Difference", "Exclusion", "Soft Light", "Hard Light", "Dodge", "Burn"])
        self.layout.addWidget(self.blending_mode_dropdown)

    def create_checkbox_layout(self):
        self.apply_filter_checkbox = QtWidgets.QCheckBox("Apply LVN Filter")
        self.apply_filter_checkbox.setChecked(True)
        self.apply_wordpad_glitch_checkbox = QtWidgets.QCheckBox("Apply Wordpad Glitch")
        self.apply_wordpad_glitch_checkbox.setChecked(False)

        self.layout.addWidget(self.apply_filter_checkbox)
        self.layout.addWidget(self.apply_wordpad_glitch_checkbox)

    def create_preset_widget(self):
        self.preset_layout = QtWidgets.QHBoxLayout()
        
        # Input for preset name
        self.preset_name_input = QtWidgets.QLineEdit()
        self.preset_name_input.setPlaceholderText("Enter preset name")
        self.preset_layout.addWidget(self.preset_name_input)
        
        # Save Preset Button
        self.save_preset_button = QtWidgets.QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        self.preset_layout.addWidget(self.save_preset_button)

        # Load Preset Button
        self.load_preset_button = QtWidgets.QPushButton("Load Preset")
        self.load_preset_button.clicked.connect(self.load_preset)
        self.preset_layout.addWidget(self.load_preset_button)

        self.layout.addLayout(self.preset_layout)

    def create_float_slider(self, label, min_value, max_value, default_value, step=0.1):
        float_slider = FloatSlider(label, min_value, max_value, default_value, step)
        
        # Connect the value change event to the processor update method
        float_slider.spinbox.valueChanged.connect(lambda value: self.update_processor(label, value))

        self.sliders[label] = float_slider  # Store reference in sliders dict for consistency

        return float_slider

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

    def update_apply_wordpad_glitch(self, state):
        self.processor.apply_wordpad_glitch = state == QtCore.Qt.Checked

    def start_webcam(self):
        self.video_manager.start_webcam()

    def stop_webcam(self):
        self.video_manager.close()  # Stop the webcam and release resources

    def open_video(self):
        self.stop_webcam()  # Ensure webcam is stopped before opening a video
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            self.video_manager.start_video_file(file_path)

    def reset_defaults(self):
        self.processor.reset_to_defaults()
        
        self.amplitude_slider.set_value(self.processor.default_amplitude)
        self.smoothness_slider.set_value(self.processor.default_smoothness)
        self.threshold_slider.set_value(self.processor.default_threshold)
        self.repeat_slider.set_value(self.processor.default_repeat)
        self.jpeg_quality_slider.set_value(self.processor.default_jpeg_quality)
        self.blend_jpeg_quality_slider.set_value(self.processor.blend_jpeg_quality)
        self.brightness_slider.set_value(self.processor.default_brightness)
        self.saturation_slider.set_value(self.processor.default_saturation)
        self.contrast_slider.set_value(self.processor.default_contrast)
        self.base_weight_slider.set_value(self.processor.default_base_weight)
        self.blend_weight_slider.set_value(self.processor.default_blend_weight)

    def closeEvent(self, event):
        """Override the close event to clean up resources."""
        self.stop_webcam()  # Ensure the webcam is stopped
        event.accept()  # Accept the event to close the window

    def save_preset(self):
        preset_name = self.preset_name_input.text()
        
        if not preset_name:
            QtWidgets.QMessageBox.warning(self, "Error", "Preset name cannot be empty.")
            return

        # Sanitize the preset name to remove invalid characters
        sanitized_preset_name = sanitize_filename(preset_name)
        
        # Ensure the preset name is not empty after sanitization
        if not sanitized_preset_name:
            QtWidgets.QMessageBox.warning(self, "Error", "Preset name is invalid.")
            return

        # Save slider values
        preset = {label: slider.value() for label, slider in self.sliders.items()}

        # Save additional control states
        preset['apply_lvn_filter'] = self.apply_filter_checkbox.isChecked()
        preset['apply_wordpad_glitch'] = self.apply_wordpad_glitch_checkbox.isChecked()
        preset['color_space'] = self.color_space_dropdown.currentText()
        preset['blending_mode'] = self.blending_mode_dropdown.currentText()
        preset['selected_channels'] = [cb.isChecked() for cb in self.channel_checkboxes]

        # Save the preset to a file
        presets_dir = "presets"
        
        if not os.path.exists(presets_dir):
            os.makedirs(presets_dir)

        with open(os.path.join(presets_dir, f"{sanitized_preset_name}.json"), 'w') as f:
            json.dump(preset, f)

    def load_preset(self):
        # Open a file dialog to select a preset file (JSON)
        preset_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Preset", "presets", "Preset Files (*.json)")
        
        if not preset_path:
            return  # No file selected, so return
        
        # Load the preset from the selected file
        try:
            with open(preset_path, 'r') as f:
                preset = json.load(f)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load preset: {str(e)}")
            return

        # Apply the preset values to the sliders
        for label, value in preset.items():
            if label in self.sliders:
                self.sliders[label].set_value(value)

        # Apply additional control states
        if 'apply_lvn_filter' in preset:
            self.apply_filter_checkbox.setChecked(preset['apply_lvn_filter'])

        if 'apply_wordpad_glitch' in preset:
            self.apply_wordpad_glitch_checkbox.setChecked(preset['apply_wordpad_glitch'])

        if 'color_space' in preset:
            index = self.color_space_dropdown.findText(preset['color_space'])
            if index != -1:
                self.color_space_dropdown.setCurrentIndex(index)

        if 'blending_mode' in preset:
            index = self.blending_mode_dropdown.findText(preset['blending_mode'])
            if index != -1:
                self.blending_mode_dropdown.setCurrentIndex(index)

        if 'selected_channels' in preset:
            for i, checked in enumerate(preset['selected_channels']):
                if i < len(self.channel_checkboxes):
                    self.channel_checkboxes[i].setChecked(checked)


            