import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.default_amplitude = 100  
        self.default_smoothness = 5 
        self.default_threshold = 0 
        self.default_repeat = 1  
        self.default_jpeg_quality = 100  
        self.default_blend_jpeg_quality = 75 
        self.default_base_weight = 0.5 
        self.default_blend_weight = 0.5 
        self.default_apply_filter = True 
        self.default_color_space = "RGB" 
        self.default_blending_mode = "None" 
        self.default_selected_channels = [1, 1, 1] 

        self.amplitude = self.default_amplitude
        self.smoothness = self.default_smoothness
        self.threshold = self.default_threshold
        self.repeat = self.default_repeat
        self.jpeg_quality = self.default_jpeg_quality
        self.blend_jpeg_quality = self.default_blend_jpeg_quality
        self.base_weight = self.default_base_weight
        self.blend_weight = self.default_blend_weight
        self.apply_filter = self.default_apply_filter
        self.selected_color_space = self.default_color_space
        self.selected_blending_mode = self.default_blending_mode
        self.selected_channels = [1, 1, 1]

        self.color_space_conversion = {
            "RGB": None,
            "HSV": cv2.COLOR_RGB2HSV,
            "HLS": cv2.COLOR_RGB2HLS,
            "LAB": cv2.COLOR_RGB2LAB,
            "LUV": cv2.COLOR_RGB2LUV,
            "XYZ": cv2.COLOR_RGB2XYZ,
            "YCrCb": cv2.COLOR_RGB2YCrCb,
            "YUV": cv2.COLOR_RGB2YUV,
        }
    
    def reset_to_defaults(self):
        self.amplitude = self.default_amplitude
        self.smoothness = self.default_smoothness
        self.threshold = self.default_threshold
        self.repeat = self.default_repeat
        self.jpeg_quality = self.default_jpeg_quality
        self.blend_jpeg_quality = self.default_blend_jpeg_quality
        self.base_weight = self.default_base_weight
        self.blend_weight = self.default_blend_weight
        self.apply_filter = self.default_apply_filter
        self.selected_color_space = self.default_color_space
        self.selected_blending_mode = self.default_blending_mode
        self.selected_channels = self.default_selected_channels

    def encode_jpeg(self, frame, quality):
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)

        success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if success:
            jpeg_image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            return jpeg_image
        return frame

    def apply_local_variance_normalization(self, img):
        img = img.astype(np.float32)
        
        kernel_size = max(1, int(self.smoothness) * 2 + 1)
        min_threshold = max(0.01, self.threshold)
        repeat = int(round(self.repeat))
        num_channels = img.shape[2]

        def normalize_once(img):
            output_img = np.zeros_like(img)
            for c in range(num_channels):
                if c >= len(self.selected_channels) or self.selected_channels[c] == 0:
                    output_img[:, :, c] = img[:, :, c]
                    continue
                
                mean = cv2.GaussianBlur(img[:, :, c], (kernel_size, kernel_size), 0)
                variance = cv2.GaussianBlur((img[:, :, c] - mean) ** 2, (kernel_size, kernel_size), 0)
                std_dev = np.sqrt(variance + min_threshold)
                alpha = self.amplitude
                normalized_channel = (img[:, :, c] - mean) / std_dev
                normalized_channel *= alpha
                normalized_channel += mean
                output_img[:, :, c] = np.clip(normalized_channel, 0, 255)
            
            return output_img

        for _ in range(repeat):
            img = normalize_once(img)
        
        return img.astype(np.uint8)

    def convert_color_space(self, frame):
        conversion_code = self.color_space_conversion.get(self.selected_color_space)
        if conversion_code is not None:
            if conversion_code:
                converted_frame = cv2.cvtColor(frame, conversion_code)
            else:
                converted_frame = frame
        else:
            converted_frame = frame
        return converted_frame

    def blend_images(self, base_img, blend_img):
        base_weight = self.base_weight
        blend_weight = self.blend_weight

        if base_img.shape != blend_img.shape:
            blend_img = cv2.resize(blend_img, (base_img.shape[1], base_img.shape[0]))

        mode = self.selected_blending_mode
        if mode == "Overlay":
            blended = cv2.addWeighted(base_img, base_weight, blend_img, blend_weight, 0)
        elif mode == "Multiply":
            blended = cv2.multiply(base_img, blend_img)
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        elif mode == "Linear Burn":
            blended = base_img + blend_img - 255
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        elif mode == "Screen":
            blended = cv2.addWeighted(base_img, base_weight, 255 - blend_img, blend_weight, 0)
        elif mode == "Darken":
            blended = cv2.min(base_img, blend_img)
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        elif mode == "Lighten":
            blended = cv2.max(base_img, blend_img)
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        elif mode == "Difference":
            blended = cv2.absdiff(base_img, blend_img)
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        elif mode == "Exclusion":
            blended = base_img + blend_img - 2 * cv2.multiply(base_img, blend_img)
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        elif mode == "Soft Light":
            blended = cv2.addWeighted(base_img, base_weight, blend_img, blend_weight, 0)
        elif mode == "Hard Light":
            blended = cv2.addWeighted(base_img, base_weight, blend_img, -blend_weight, 0)
        elif mode == "Dodge":
            blended = cv2.divide(base_img, 255 - blend_img)
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        elif mode == "Burn":
            blended = 255 - cv2.divide(255 - base_img, blend_img)
            blended = cv2.addWeighted(blended, blend_weight, base_img, base_weight, 0)
        else:
            blended = base_img

        blended = np.clip(blended, 0, 255).astype(np.uint8)
        return blended

    def process_frame(self, frame):
        base_frame = self.encode_jpeg(frame, self.blend_jpeg_quality)
        lvn_frame = base_frame.copy()

        if self.apply_filter:
            lvn_frame = self.apply_local_variance_normalization(lvn_frame)

        lvn_frame = self.convert_color_space(lvn_frame)

        if self.apply_blending:
            blended_frame = self.blend_images(base_frame, lvn_frame)
        else:
            blended_frame = lvn_frame

        return self.encode_jpeg(blended_frame, self.jpeg_quality)

