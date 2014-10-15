'''
Abstraction of the picamera object
http://picamera.readthedocs.org/en/release-1.8/
'''
import io
# import cv2
import time
import picamera
import picamera.array
import collections
import numpy as np
from PIL import Image
from scipy import interpolate 
from datetime import datetime


# from fractions import Fraction
# picamera.camera.Fraction = Fraction

AUTORESOLUTION = (640,480)
# RESOLUTION = (640,480)
RESOLUTION = (1280, 720)
# RESOLUTION = (1920, 1072)

class Camera(object):
    def __init__(self, preview=False, navg=10):
        '''Start a camera Object'''
        self.cam = picamera.PiCamera()
        self.shutter = collections.deque(maxlen=navg)
        self.red     = collections.deque(maxlen=navg)
        self.blue    = collections.deque(maxlen=navg)
        self.setup(first=True)
        if preview:
            self.cam.start_preview()
            self.cam.preview.fullscreen=True
        
        
    
    def __enter__(self):
        self.setup()
        # print 'wait time for camera: 1 second(s)'
        # time.sleep(1)
        return self
    
    def __exit__(self, type, value, traceback):
        self.cam.close()
    
    def getnext(self, array):
        npts = len(array)
        if npts < 5:
            return 0
        # elif npts < 5:
        #     return array[-1]
        else:
            tmp = interpolate.interp1d(np.arange(npts), array)
            # tmp = interpolate.UnivariateSpline(np.arange(npts), array)
            # tmp = interpolate.InterpolatedUnivariateSpline(np.arange(npts), array)
            out = float(tmp(npts-1))
            return out
    
    def getshutter(self):
        tmp = (self.getnext(self.shutter))
        # print ','.join(map('{:0.1f}'.format, self.shutter)), ': ', tmp
        return int(tmp)
    
    def limitawb(self, val):
        if val < 0:   return 0.0
        elif val > 8: return 8.0
        else:         return val
    
    def getawb(self):
        tmp = map(self.getnext, [self.red, self.blue])
        tmp = map(self.limitawb, tmp)
        return tuple(tmp)
    
    def setup(self, first=False, auto=True):
        if first:
            self.cam.framerate = 24
            self.cam.resolution = RESOLUTION
            self.cam.image_effect = 'none'
            self.cam.iso = 0
            # self.cam.led = False handled by /boot/config.txt
            self.cam.meter_mode = 'average'
            self.cam.image_denoise = True
        
        if auto:
            # self.cam.resolution = AUTORESOLUTION
            self.cam.exposure_mode = 'verylong'
            self.cam.shutter_speed = 0
            self.cam.awb_mode = 'auto'
        else:
            # self.cam.resolution = RESOLUTION
            self.cam.awb_mode = 'off'
            self.cam.awb_gains = self.getawb()
            self.cam.exposure_mode = 'off'
            self.cam.shutter_speed = self.getshutter()
    
    def update(self):
        exp = self.cam.exposure_speed
        r,b = self.cam.awb_gains
        self.red.append(float(r))
        self.blue.append(float(b))
        self.shutter.append(exp)
        
    
    def label(self):
        label='{0:} {1:,} {2[0]:0.2f} {2[1]:0.2f} {3:0.2f} {4:0.2f}'.format(self.cam.iso, 
                                self.cam.exposure_speed, 
                                map(float, self.cam.awb_gains),
                                float(self.cam.analog_gain),
                                float(self.cam.digital_gain))
        self.cam.annotate_text = datetime.now().strftime('%H:%M:%S') + ' '+ label
        self.cam.annotate_frame_num=True
    def smoothcap(self):
        ''' Generate a series of images that have a smooth
        ramping of white balance, and exposure.  Procedure is 
        to take a auto image pull out the measured awb and exposure
        add those to a an array and use the average to then capture
        a good image.  The size of the array will determine how 
        smooth the resulting timelapse will be, and how quickly it
        will respond to changes.'''
        with picamera.array.PiRGBArray(self.cam) as stream:
            while True:
                # Capture test image
                self.setup()
                self._cap(stream)
                self.update()
        
                # capture real image
                self.setup(auto=False)
                self._cap(stream)
                print map(float,self.cam.awb_gains), self.cam.exposure_speed
                yield stream
    
    def smoothcap2(self):
        k = 0
        while True:
            # Capture test image
            self.setup()
            self.capture()
            self.update()
    
            # capture real image
            self.setup(auto=True)
            print k, map(float,self.cam.awb_gains), self.cam.exposure_speed
            filename = '/home/pi/tmp/cap/image_{:04d}.jpg'.format(k)
            image = self.capture(filename=filename, annotate=True)
            yield image
            k += 1
        
    
    def _cap(self, stream):
        self.label()
        self.cam.capture(stream, 'rgb')
        stream.seek(0)
    
    
    def capture(self, filename='/dev/null', annotate=False):
        self.cam.exif_tags['IFD0.Artist'] = 'Mendez'
        self.cam.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2014 timerasp'
        self.cam.exif_tags['EXIF.UserComment'] = ''
        
        
        # self.cam.annotate_bg = True
        # if annotate is not None:
        #     self.cam.annotate_text = '{}: {}'.format(datetime.now().strftime('%H:%M:%S'), annotate)
        if annotate:
            self.label()
        self.cam.capture(filename, format='jpeg')
        # return None
        # stream = io.BytesIO()
        # self.cam.capture(stream, format='jpeg')
        # stream.seek(0)
        # image = Image.open(stream)
        # return image
    
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
        
        
        
        
        
        
        