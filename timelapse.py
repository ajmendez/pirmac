"""
timelapse.py -- do a timelapse 
Code partially from https://github.com/dwiel/gphoto2-timelapse
"""

import os
import re
import time
import subprocess
from datetime import datetime, timedelta

# the time between photos
DELTA = timedelta(minutes = 5)
DIRECTORY = '/Users/user/tmp/test/'



def parse_int(s) :
  try :
    return int(s)
  except ValueError:
    return None
  except TypeError:
    return None

def get_prefix() :
  """
  look at the filenames already in the picture folder and look for files with a prefix.  Find the biggest prefix 
  and make the new prefix 1 larger.  This is so that even if the clock gets reset (as it does if the raspberrypi
  looses power), the pictures can still be reassembled in the order that they were taken
  """
  
  import glob
  filenames = glob.glob(picture_folder+'*.jpg')
  max_prefix = 0
  for filename in filenames :
    parts = filenames.split('_')
    if len(parts) > 1 :
      possible_prefix = parse_int(parts[0])
      if possible_prefix > max_prefix :
        max_prefix = possible_prefix
  
  max_prefix += 1
  return '%04d' % max_prefix

prefix = get_prefix()
# or if you prefer no prefix, uncomment the following line
# prefix = ''

def log(message) :
  print datetime.utcnow(), message

def run(cmd) :
  reset_nikon()
  
  # try running the command once and if it fails, reset_nikon
  # and then try once more
  for i in range(2) :
    log("running %s" % cmd)
    
    p = subprocess.Popen(
      # 'sudo ' + 
      cmd,
      shell=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    )
    (stdout, stderr) = p.communicate()
    ret = p.returncode
    
    if stdout.strip() != '' or DEBUG :
      if stdout[-1] == '\n' :
        stdout = stdout[:-1]
      print 'stdout'
      print '>> '+stdout.replace('\n', '\n>> ')
      print 'end stdout'
    if stderr.strip() != '' or DEBUG :
      if stderr[-1] == '\n' :
        stderr = stderr[:-1]
      print 'stderr'
      print '>> '+stderr.replace('\n', '\n>> ')
      print 'end stderr'
    if DEBUG :
      print 'ret', ret
    
    if ret == 0 :
      return ret, stdout, stderr
    elif ret == 1 :
      if 'No camera found' in stderr :
        print '#### no camera found'
        print 'TODO: reboot?'
        print 'TODO: reset power on camera via GP IO?'
        return ret, stdout, stderr
      else :
        # other error like tried to delete a file where there was none, etc
        return ret, stdout, stderr
    else :
      reset_nikon()
  
  return ret, stdout, stderr


def list_files() :
  folder = ''
  files = []
  
  ret, stdout, _ = run('gphoto2 --list-files')
  for line in stdout.split('\n') :
    if not line : continue
    
    if line[0] == '#' :
      files.append((folder, line.split()[0][1:], line.split()[1]))
    else :
      m = re.match(".*'(.*)'", line)
      if m :
        folder = m.group(1)
        if folder[-1] != '/' :
          folder += '/'
      else :
        log('warning, unkown output of --list-files: ' + line)
  
  return files

workaround = False
def take_picture(filename = None) :
  if not filename :
    filename = prefix + '_' + datetime.utcnow().strftime("%Y%m%d-%H%M%S.jpg")
  
  log('taking picture')
  if workaround :
    # this works around --capture-image-and-download not working
    # get rid of any existing files on the card
    for folder, number, _ in list_files() :
      delete_picture(from_folder = folder)
    
    # take the picture
    run("gphoto2 --capture-image")
    
    # copy the picture from the camera to local disk
    run("gphoto2 --get-file=1 --filename=%s/%s" % (picture_folder, filename))
    
    ## delete file off of camera
    #delete_picture()
  else :
    return run("gphoto2 --capture-image-and-download --filename %s/%s" % (picture_folder, filename))

def delete_picture(from_folder = None) :
  log('deleting picture')
  
  if from_folder :
    print 'from_folder', from_folder
    ret, stdout, stderr = run("gphoto2 --delete-file=1 --folder=%s" % from_folder)
    if 'There are no files in folder' in stdout :
      return ret
  
  # try deleting from all 3 known folders, in the order of most likely
  ret, stdout, stderr = run("gphoto2 --delete-file=1 --folder=/store_00010001")
  if 'There are no files in folder' in stderr :
    ret, stdout, stderr = run("gphoto2 --delete-file=1 --folder=/store_00010001/DCIM/100NIKON")
    if 'There are no files in folder' in stderr :
      ret, stdout, stderr = run("gphoto2 --delete-file=1 --folder=/")
  
  return ret

def reset_settings() :
  log('reseting settings')
  run("gphoto2 --set-config /main/capturesettings/flashmode=0")
  run("gphoto2 --set-config /main/capturesettings/focusmode=1")


class Camera(object):
    def __init__(self):
        '''start the camera up and get some nice variables'''
        self.setup()
    
    def setup(self):
        '''setup the camera so that there are some standards'''
    
    def capture(self):
        '''Take a picture, return the filename'''
    
    def getbrightness(self):
        '''get the current brightness'''
    
    





def main():
    '''the main image capture loop'''
    try:
        t_pic = datetime.utcnow()
        camera = Camera()
        while True:
            # if sun.is_light(t) or ignore_sun:
            camera.picture()
            while datetime.utcnow() < t_pic + DELTA:
                time.sleep(1)
    except KeyboardInterrupt as e:
        print 'User canceled'
    except Exception as e:
        raise


if __name__ == '__main__':
    main()



