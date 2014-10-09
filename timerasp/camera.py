'''
Abstraction of the picamera object
http://picamera.readthedocs.org/en/release-1.8/
'''
import io
import cv2
import time
import picamera
import collections
import numpy as np
from PIL import Image
from scipy import interpolate 


RESOLUTION = (1280, 720)

class Camera(object):
    def __init__(self, navg=20):
        '''Start a camera Object'''
        self.cam = picamera.PiCamera()
        self.setup()
        self.shutter = collections.deque(maxlen=navg)
        self.red     = collections.deque(maxlen=navg)
        self.blue    = collections.deque(maxlen=navg)
        
        
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.cam.close()
    
    def getnext(self, array):
        npts = len(array)
        tmp = interpolate.UnivariateSpline(np.arange(npts), array)
        return tmp(npts+1)
    
    def getshutter(self):
        return getnext(self.shutter)
    
    def getawb(self):
        return map(getnext, [self.red, self.blue])
    
    def setup(self, auto=False):
        self.cam.resolution = RESOLUTION
        self.cam.image_effect = 'none'
        self.cam.iso = 100
        self.cam.led = False
        self.cam.meter_mode = 'average'
        self.cam.image_denoise = True
        if auto:
            self.cam.exposure_mode = 'auto'
            self.cam.shutter_speed = 0
            self.cam.awb_mode = 'auto'
        else:
            self.cam.awb_mode = 'off'
            self.cam.awb_gains = self.getawb()
            self.cam.exposure_mode = 'off'
            self.cam.shutter_speed = self.getshutter()
    
    def update(self, img):
        exp = camera.exposure_speed
        r,b = self.cam.awb_gains
        self.red.append(r)
        self.blue.append(b)
        self.shutter.append(exp)
        
    
    
    def smoothcap(self):
        ''' Generate a series of images that have a smooth
        ramping of white balance, and exposure.  Procedure is 
        to take a auto image pull out the measured awb and exposure
        add those to a an array and use the average to then capture
        a good image.  The size of the array will determine how 
        smooth the resulting timelapse will be, and how quickly it
        will respond to changes.'''
        
        while True:
            # Capture test image
            self.setup(auto=True)
            time.sleep(1)
            tmp = self.capture()
            self.update(tmp)
        
            # capture real image
            self.setup()
            image = self.capture()
            yield image
    
    
    
    
    
    
    def capture(self, annotate):
        self.cam.exif_tags['IFD0.Artist'] = 'Mendez'
        self.cam.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2014 timerasp'
        self.cam.exif_tags['EXIF.UserComment'] = ''
        
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
        
        
        
        
        
        
        