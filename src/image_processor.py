import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        # Default values for various settings
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

        # Defaults for brightness, contrast, and saturation
        self.default_brightness = 1.0  # Brightness multiplier (1.0 = no change)
        self.default_contrast = 1.0  # Contrast multiplier (1.0 = no change)
        self.default_saturation = 1.0  # Saturation multiplier (1.0 = no change)

        # Current values for all settings
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

        # Current values for brightness, contrast, and saturation
        self.brightness = self.default_brightness
        self.contrast = self.default_contrast
        self.saturation = self.default_saturation

        # Color space conversion mappings
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
        """Reset all processing settings to their default values."""
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

        # Reset brightness, contrast, and saturation
        self.brightness = self.default_brightness
        self.contrast = self.default_contrast
        self.saturation = self.default_saturation

    def encode_jpeg(self, frame, quality):
        """Encodes the frame into JPEG with specified quality."""
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)

        success, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if success:
            jpeg_image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            return jpeg_image
        return frame

    def apply_local_variance_normalization(self, img):
        """Applies local variance normalization (LVN) to the image."""
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
        """Converts the color space of the frame based on the selected color space."""
        conversion_code = self.color_space_conversion.get(self.selected_color_space)
        if conversion_code is not None:
            if conversion_code:
                converted_frame = cv2.cvtColor(frame, conversion_code)
            else:
                converted_frame = frame
        else:
            converted_frame = frame
        return converted_frame

    def adjust_brightness_contrast(self, img):
        """Adjusts brightness and contrast of the image."""
        # Normalize the brightness range from the slider (-100 to 100) to (0.0 to 2.0)
        normalized_brightness = (self.brightness + 100) / 100.0  # Maps [-100, 100] to [0.0, 2.0]
        
        # Apply contrast and normalized brightness
        if self.contrast != 1.0 or normalized_brightness != 1.0:
            img = cv2.convertScaleAbs(img, alpha=self.contrast, beta=(normalized_brightness - 1.0) * 255)
        return img

    def adjust_saturation(self, img):
        """Adjusts saturation based on the selected color space."""
        if self.saturation == 1.0:
            return img  # No change in saturation

        color_space = self.selected_color_space
        if color_space == "RGB":
            # Adjust saturation in the RGB color space by scaling the distance from the gray axis
            img = self.adjust_saturation_rgb(img)
        elif color_space == "HSV":
            img = self.adjust_saturation_hsv(img)
        elif color_space == "HLS":
            img = self.adjust_saturation_hls(img)
        elif color_space == "LAB":
            img = self.adjust_saturation_lab(img)
        elif color_space == "LUV":
            img = self.adjust_saturation_luv(img)
        elif color_space == "XYZ":
            img = self.adjust_saturation_xyz(img)
        elif color_space == "YCrCb":
            img = self.adjust_saturation_ycrcb(img)
        elif color_space == "YUV":
            img = self.adjust_saturation_yuv(img)
        return img

    def adjust_saturation_rgb(self, img):
        """Adjust saturation in the RGB color space by scaling the chromatic intensity."""
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = img.astype(np.float32)
        gray = gray[:, :, None].astype(np.float32)
        img = gray + self.saturation * (img - gray)  # Scale chromaticity
        return np.clip(img, 0, 255).astype(np.uint8)

    def adjust_saturation_hsv(self, img):
        """Adjust saturation in the HSV color space."""
        hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv_img[:, :, 1] *= self.saturation  # Adjust the saturation channel
        hsv_img[:, :, 1] = np.clip(hsv_img[:, :, 1], 0, 255)
        return cv2.cvtColor(hsv_img.astype(np.uint8), cv2.COLOR_HSV2RGB)

    def adjust_saturation_hls(self, img):
        """Adjust saturation in the HLS color space."""
        hls_img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS).astype(np.float32)
        hls_img[:, :, 2] *= self.saturation  # Adjust the saturation channel
        hls_img[:, :, 2] = np.clip(hls_img[:, :, 2], 0, 255)
        return cv2.cvtColor(hls_img.astype(np.uint8), cv2.COLOR_HLS2RGB)

    def adjust_saturation_lab(self, img):
        """Adjust saturation in the LAB color space."""
        lab_img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab_img[:, :, 1:3] *= self.saturation  # Scale chromaticity channels (a and b)
        lab_img[:, :, 1:3] = np.clip(lab_img[:, :, 1:3], 0, 255)
        return cv2.cvtColor(lab_img.astype(np.uint8), cv2.COLOR_LAB2RGB)

    def adjust_saturation_luv(self, img):
        """Adjust saturation in the LUV color space."""
        luv_img = cv2.cvtColor(img, cv2.COLOR_RGB2LUV).astype(np.float32)
        luv_img[:, :, 1:3] *= self.saturation  # Adjust U and V channels
        luv_img[:, :, 1:3] = np.clip(luv_img[:, :, 1:3], 0, 255)
        return cv2.cvtColor(luv_img.astype(np.uint8), cv2.COLOR_LUV2RGB)

    def adjust_saturation_xyz(self, img):
        """Adjust saturation in the XYZ color space (affect chromaticity)."""
        xyz_img = cv2.cvtColor(img, cv2.COLOR_RGB2XYZ).astype(np.float32)
        xyz_img[:, :, 1:3] *= self.saturation  # Adjust Y and Z channels for chroma
        xyz_img[:, :, 1:3] = np.clip(xyz_img[:, :, 1:3], 0, 255)
        return cv2.cvtColor(xyz_img.astype(np.uint8), cv2.COLOR_XYZ2RGB)

    def adjust_saturation_ycrcb(self, img):
        """Adjust saturation in the YCrCb color space."""
        ycrcb_img = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb).astype(np.float32)
        ycrcb_img[:, :, 1:3] *= self.saturation  # Adjust Cr and Cb channels
        ycrcb_img[:, :, 1:3] = np.clip(ycrcb_img[:, :, 1:3], 0, 255)
        return cv2.cvtColor(ycrcb_img.astype(np.uint8), cv2.COLOR_YCrCb2RGB)

    def adjust_saturation_yuv(self, img):
        """Adjust saturation in the YUV color space."""
        yuv_img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV).astype(np.float32)
        yuv_img[:, :, 1:3] *= self.saturation  # Adjust U and V channels
        yuv_img[:, :, 1:3] = np.clip(yuv_img[:, :, 1:3], 0, 255)
        return cv2.cvtColor(yuv_img.astype(np.uint8), cv2.COLOR_YUV2RGB)

    def blend_images(self, base_img, blend_img):
        """Blends two images based on the selected blending mode."""
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
        """Main method to process a video frame."""
        # Adjust brightness and contrast first
        frame = self.adjust_brightness_contrast(frame)

        # Adjust saturation
        frame = self.adjust_saturation(frame)

        # Convert to JPEG with blend JPEG quality
        base_frame = self.encode_jpeg(frame, self.blend_jpeg_quality)
        lvn_frame = base_frame.copy()

        # Apply Local Variance Normalization (LVN) if enabled
        if self.apply_filter:
            lvn_frame = self.apply_local_variance_normalization(lvn_frame)

        # Convert color space
        lvn_frame = self.convert_color_space(lvn_frame)

        # Apply blending if enabled
        if self.apply_blending:
            blended_frame = self.blend_images(base_frame, lvn_frame)
        else:
            blended_frame = lvn_frame

        # Convert final output back to JPEG
        return self.encode_jpeg(blended_frame, self.jpeg_quality)
