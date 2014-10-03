'''
Abstraction of the picamera object
http://picamera.readthedocs.org/en/release-1.8/
'''
import io
import cv2
import time
import picamera
import numpy as np
from PIL import Image


RESOLUTION = (1280, 720)

class Camera(object):
    def __init__(self):
        '''Start a camera Object'''
        self.cam = picamera.PiCamera()
        self.setup()
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.cam.close()
    
    def setup(self):
        self.cam.resolution = RESOLUTION
        self.cam.exposure_mode = 'off'
        self.cam.meter_mode = ''
        self.cam.image_effect = ''
        self.cam.shutter_speed = 0
        self.cam.iso = '100'
        self.cam.awb_mode = 'off'
        self.cam.awb_gains = (r,b)
        self.cam.led = False
        
    def capture(self, annotate):
        self.cam.exif_tags['IFD0.Artist'] = ''
        self.cam.exif_tags['IFD0.Copyright'] = ''
        self.cam.annotate_bg = True
        self.cam.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.cam.capture()
    
    def stream(self):
        with picamera.array.PiRGBArray(self.cam) as stream:
            self.cam.capture(stream, 'rgb')
            return stream
    
    def image(self):
        stream = io.BytesIO()
        self.cam.capture(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream)
    
    def opencv(self):
        stream = io.BytesIO()
        self.cam.capture(stream, format='jpeg') # bgr
        data = np.fromstream(stream.getvalue(), dtype=np.uint8)
        return cv2.imducode(data, 1)[:, :, ::-1]
        
        
        
        
        
        
        