# lvndr

Python script that applies glitchy artifacts to JPEG-encoded images from a video file or webcam input using Local Variance Normalisation, Wordpad glitch effect, image/colorspace controls and blending options.

The Local Variance Normalisation implementation is based off the [G'MIC filter](https://github.com/jboulanger/jboulanger-gmic/blob/1bec092d6ddf0ac4f49ac7169016bb3f7a3b8d75/jboulanger.gmic#L734) by `jboulanger`, and the Wordpad glitch effect is based off the [batch_wordpad_glitch](https://github.com/stepsal/batch_wordpad_glitch/blob/master/wordpad_glitch.py) by `stepsal`.

## Setup (Windows only)

1. Clone repository or download ZIP and extract to target directory
2. Install requirements via `pip install -r requirements.txt` 
3. Run the `lvndr.py` file in your IDE or by opening a command line in the main directory and running `python lvndr.py`

## Usage

Click on `Start Webcam` to start a video feed from your webcam or click on `Open Video File` to open a dialog and select a video file.

Tweak parameters, switch colorspaces, select channels and select blending modes to your heart's desire. 

To close, close the controls window and click on the image feed window and press `q`.

## Examples

![Example image](./resources/example%20(2).png)
![Example image](./resources/example%20(3).png)
![Example image](./resources/example%20(4).png)
![Example image](./resources/example%20(5).png)
![Example image](./resources/example%20(1).png)




