#!/usr/bin/env python
## Stacking IR fun



# sudo pip install https://github.com/ashtons/picam/zipball/master#egg=picam
# http://kjordahl.net/blog/?p=115
# http://onlyjus-photopy.blogspot.com/2012/09/image-stacking.html
# http://stackoverflow.com/questions/9251580/stacking-astronomy-images-with-python
# https://github.com/ashtons/picam
# sudo idle3


import picam
from PIL import Image, ImageChops


picam.config.awbMode = picam.MMAL_PARAM_AWBMODE_OFF
picam.config.exposure = picam.MMAL_PARAM_EXPOSUREMODE_VERYLONG
picam.config.shutterSpeed = 20000         # 0 = auto, otherwise the shutter speed in ms
picam.config.ISO = 100

for i in range(10):
    im = picam.takePhoto()
    im = im.resize((640,480),Image.ANTIALIAS)
    if i == 0:
        out = im
    else:
        out = ImageChops.lighter(out, im)
#print type(i)
out.save('/tmp/test.jpg')




