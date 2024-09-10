from tkinter import filedialog, Tk, Scale, HORIZONTAL, StringVar, OptionMenu, Label, Frame, Canvas, Scrollbar, Checkbutton, IntVar, Button
from src.image_processor import ImageProcessor
from src.video_source_manager import VideoSourceManager
import threading

class GUIManager:
    def __init__(self, processor, video_manager):
        self.processor = processor
        self.video_manager = video_manager
        self.root = Tk()
        self.root.title("Controls")
        self.root.geometry("640x860") 
        self.channel_vars = []  
        self.channel_checkboxes = []

        self.setup_gui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def start_webcam(self):
        self.video_manager.start_webcam()

    def open_video_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
        if file_path:
            self.video_manager.start_video_file(file_path)

    def setup_gui(self):
        control_frame = Frame(self.root, bg='#000000')
        control_frame.pack(fill='both', expand=True)

        
        canvas = Canvas(control_frame, bg='#000000')
        scrollbar = Scrollbar(control_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='#000000')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)
      
        button_frame = Frame(scrollable_frame, bg='#000000')
        button_frame.pack(fill='x', pady=5)

        start_webcam_button = Button(button_frame, text="Start Webcam", command=self.start_webcam, bg='#000000', fg='#00FF00', font=("Courier", 12), highlightbackground='#00FF00')
        start_webcam_button.pack(side='left', padx=5)

        open_video_file_button = Button(button_frame, text="Open Video File", command=self.open_video_file, bg='#000000', fg='#00FF00', font=("Courier", 12), highlightbackground='#00FF00')
        open_video_file_button.pack(side='left', padx=5)

        reset_button = Button(button_frame, text="Reset to Default", command=self.reset_to_default, bg='#000000', fg='#00FF00', font=("Courier", 12), highlightbackground='#00FF00')
        reset_button.pack(side='left', padx=5)

        self.amplitude_slider = self.add_slider(scrollable_frame, "Amplitude", 0, 100, self.processor.amplitude, ("Courier", 14, "bold"), ("Courier", 10), 0.1)
        self.smoothness_slider = self.add_slider(scrollable_frame, "Smoothness", 1, 20, self.processor.smoothness, ("Courier", 14, "bold"), ("Courier", 10), 0.1)
        self.threshold_slider = self.add_slider(scrollable_frame, "Threshold", 0, 100, self.processor.threshold, ("Courier", 14, "bold"), ("Courier", 10), 0.1)
        self.repeat_slider = self.add_slider(scrollable_frame, "Repeat", 1, 4, self.processor.repeat, ("Courier", 14, "bold"), ("Courier", 10), 0.1)
        self.jpeg_quality_slider = self.add_slider(scrollable_frame, "JPEG Quality", 0, 100, self.processor.jpeg_quality, ("Courier", 14, "bold"), ("Courier", 10), 1)
        self.blend_jpeg_quality_slider = self.add_slider(scrollable_frame, "Blend JPEG Quality", 0, 100, self.processor.blend_jpeg_quality, ("Courier", 14, "bold"), ("Courier", 10), 1)
        
        self.base_weight_slider = self.add_slider(scrollable_frame, "Base Weight", 0.0, 1.0, self.processor.base_weight, ("Courier", 14, "bold"), ("Courier", 10), 0.01)
        self.blend_weight_slider = self.add_slider(scrollable_frame, "Blend Weight", 0.0, 1.0, self.processor.blend_weight, ("Courier", 14, "bold"), ("Courier", 10), 0.01)
        self.base_weight_slider.pack(fill='x', pady=5)
        self.blend_weight_slider.pack(fill='x', pady=5)
        
        self.color_space_var = StringVar(self.root)
        self.color_space_var.set(self.processor.selected_color_space)
        self.add_option_menu(scrollable_frame, "Colorspace:", self.processor.color_space_conversion.keys(), self.color_space_var)
        
        self.filter_var = StringVar(self.root)
        self.filter_var.set("Yes" if self.processor.apply_filter else "No")
        self.add_option_menu(scrollable_frame, "Apply Filter:", ["Yes", "No"], self.filter_var)
   
        self.blending_mode_var = StringVar(self.root)
        self.blending_mode_var.set(self.processor.selected_blending_mode)
        self.add_option_menu(scrollable_frame, "Blending Mode:", ["None", "Overlay", "Multiply", "Linear Burn", "Screen", "Darken", "Lighten", "Difference", "Exclusion", "Soft Light", "Hard Light", "Dodge", "Burn"], self.blending_mode_var)
        
        self.channel_frame = Frame(scrollable_frame, bg='#000000')
        self.channel_frame.pack(fill='x', pady=5)
        self.update_channel_checkboxes()  
        
        self.color_space_var.trace_add('write', self.update_channel_checkboxes)
        
        self.blending_mode_var.trace_add('write', self.update_blending_mode_gui)
        
        self.update_blending_mode_gui()

    def add_slider(self, parent, label, from_, to_, default_value, title_font, slider_font, resolution):
        frame = Frame(parent, bg='#000000')
        frame.pack(fill='x', pady=5)

        Label(frame, text=label, fg='#00FF00', bg='#000000', font=title_font).pack(side='left', padx=10)

        slider = Scale(frame, from_=from_, to_=to_, orient=HORIZONTAL, length=300, sliderlength=20, tickinterval=(to_ - from_) / 5, bg='#000000', fg='#00FF00', troughcolor='#004d00', font=slider_font, resolution=resolution, command=self.update_parameters_from_slider)
        slider.set(default_value)
        slider.pack(side='left', fill='x', expand=True)
        
        return slider
    
    def add_option_menu(self, parent, label, options, variable):
        frame = Frame(parent, bg='#000000')
        frame.pack(fill='x', pady=5)

        Label(frame, text=label, fg='#00FF00', bg='#000000', font=("Courier", 12)).pack(side='left', padx=10)

        menu = OptionMenu(frame, variable, *options, command=self.update_blending_mode)
        menu.config(bg='#000000', fg='#00FF00', font=("Courier", 12), highlightbackground='#00FF00')
        menu.pack(side='left', fill='x', expand=True)

    def update_parameters_from_slider(self, *args):
        self.update_parameters()

    def update_channel_checkboxes(self, *args):       
        for checkbox in self.channel_checkboxes:
            checkbox.destroy()
        self.channel_checkboxes.clear()
        self.channel_vars.clear()
        
        color_space = self.color_space_var.get()
        if color_space == 'RGB':
            channels = ['R', 'G', 'B']
        elif color_space == 'HSV':
            channels = ['H', 'S', 'V']
        elif color_space == 'HLS':
            channels = ['H', 'L', 'S']
        elif color_space == 'LAB':
            channels = ['L', 'A', 'B']
        elif color_space == 'LUV':
            channels = ['L', 'U', 'V']
        elif color_space == 'YCrCb':
            channels = ['Y', 'Cr', 'Cb']
        elif color_space == 'XYZ':
            channels = ['X', 'Y', 'Z']
        elif color_space == 'YUV':
            channels = ['Y', 'U', 'V']
     
        self.processor.selected_channels = [1] * len(channels)  
        
        for i, channel in enumerate(channels):
            var = IntVar(value=self.processor.selected_channels[i])  
            cb = Checkbutton(self.channel_frame, text=channel, variable=var, onvalue=1, offvalue=0,
                             fg='#00FF00', bg='#000000', selectcolor='#004d00', command=self.update_channel_selection)
            cb.pack(side='left', padx=5)
            self.channel_vars.append(var)
            self.channel_checkboxes.append(cb)
        
        self.root.update_idletasks()

    def update_channel_selection(self):      
        self.processor.selected_channels = [var.get() for var in self.channel_vars]

    def update_blending_mode_gui(self, *args):        
        mode = self.blending_mode_var.get()

        if mode == "None":
            self.base_weight_slider.pack_forget()
            self.blend_weight_slider.pack_forget()
        else:
            self.base_weight_slider.pack(fill='x', pady=5)
            self.blend_weight_slider.pack(fill='x', pady=5)

        self.update_parameters()

    def update_blending_mode(self, value):
        self.processor.selected_blending_mode = value
        self.update_blending_mode_gui()

    def update_parameters(self):       
        self.processor.amplitude = self.amplitude_slider.get()
        self.processor.smoothness = self.smoothness_slider.get()
        self.processor.threshold = self.threshold_slider.get()
        self.processor.repeat = self.repeat_slider.get()
        self.processor.jpeg_quality = self.jpeg_quality_slider.get()
        self.processor.blend_jpeg_quality = self.blend_jpeg_quality_slider.get()
        self.processor.base_weight = self.base_weight_slider.get()
        self.processor.blend_weight = self.blend_weight_slider.get()
        self.processor.apply_filter = self.filter_var.get() == "Yes"         
        self.processor.apply_blending = self.blending_mode_var.get() != "None"  
        self.processor.selected_color_space = self.color_space_var.get()
        self.processor.selected_blending_mode = self.blending_mode_var.get()

    def reset_to_default(self):
        self.amplitude_slider.set(self.processor.default_amplitude)
        self.smoothness_slider.set(self.processor.default_smoothness)
        self.threshold_slider.set(self.processor.default_threshold)
        self.repeat_slider.set(self.processor.default_repeat)
        self.jpeg_quality_slider.set(self.processor.default_jpeg_quality)
        self.blend_jpeg_quality_slider.set(self.processor.default_blend_jpeg_quality)
        self.base_weight_slider.set(self.processor.default_base_weight)
        self.blend_weight_slider.set(self.processor.default_blend_weight)
        self.color_space_var.set(self.processor.default_color_space)
        self.filter_var.set("Yes" if self.processor.default_apply_filter else "No")
        self.blending_mode_var.set(self.processor.default_blending_mode)
        self.update_channel_checkboxes()

    def on_closing(self):    
        self.root.destroy()
