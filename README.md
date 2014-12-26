timerasp
========

Rebranded Raspberry pi camera with python.
http://www.raspberrypi.org/forums/viewtopic.php?f=43&t=70105&p=657575

  * # Setup ssh on different port
  * # Setup ssh-keys
  * sudo apt-get install python-setuptools
  * sudo easy_install pip
  * sudo apt-get install python2.7-dev
  * # Setup rmate
  curl -Lo ~/bin/rmate https://raw.github.com/textmate/rmate/master/bin/rmate
  chmod a+x ~/bin/rmate
  * # Setup bashrc
  * git clone git@github.com:ajmendez/templog.git
  * git clone git@github.com:ajmendez/timerasp.git
  * sudo pip install -I flickrapi==1.4.5
  * sudo pip install picamera
  *  sudo pip install --allow-unverified pil --allow-external pil pil
  sudo apt-get install python-imaging python-scipy python-skimage 
  sudo pip install ephem
  sudo pip install --upgrade google-api-python-client pyephem httplib2
  wget https://github.com/tjormola/rpi-openmax-demos/archive/master.zip
  >> scintillate, pymendez_basic
  sudo pip install poster