#!/usr/bin/python

import os
import sys
import time
import json
import ephem
import random
import socket
import httplib
import httplib2
import datetime
import calendar
from timerasp import gmail, flickr

from apiclient.discovery import build
from oauth2client.file import Storage
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.tools import argparser, run_flow
from oauth2client.client import flow_from_clientsecrets



# ephem, httplib2, flickrapi, exifread, poster, apiclient, urllib3

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = os.path.expanduser("~/.limited/client_secrets.json")

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://cloud.google.com/console

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

H264_FILENAME = os.path.expanduser("~/tmp/timelapse/todays_video.h264")

MP4_FILENAME = os.path.expanduser("~/tmp/timelapse/todays_video.mp4")

DAILY_FILENAME = os.path.expanduser("~/tmp/timelapse/%d.mp4"%calendar.timegm(time.gmtime()))


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage(os.path.expanduser('~/.limited/youtube-oauth2.json'))
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options, title, description):
  tags = None

  body=dict(
    snippet=dict(
      title=title,
      description=description,
      tags="timelapse,maryland",
      categoryId=""
    ),
    status=dict(
      privacyStatus=VALID_PRIVACY_STATUSES[0]
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(MP4_FILENAME, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      status, response = insert_request.next_chunk()
      if 'id' in response:
        print "Video id '%s' was successfully uploaded." % response['id']
      else:
        exit("The upload failed with an unexpected response: %s" % response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)


openmax_dir = os.path.expanduser('~/tmp/timelapse/rpi-openmax-demos-master')


def utc_mktime(utc_tuple):
    """Returns number of seconds elapsed since epoch

    Note that no timezone are taken into consideration.

    utc tuple must be: (year, month, day, hour, minute, second)

    """

    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))

def datetime_to_timestamp(dt):
    """Converts a datetime object to UTC timestamp"""

    return int(utc_mktime(dt.timetuple()))

# if __name__ == '__main__':
#   # exiftool exifread flickrapi
#   from scintillate.api import Upload
#   flickr = Upload()
#   now = datetime.datetime.today()
#   flickr.push(filename='output.mp4',
#               title='{:d} : {}'.format(datetime_to_timestamp(now), now.strftime("%Y-%m-%d")),
#               description='Raspberry Pi IR camera',
#               tags =['IR','timelapse', 'movie'],
#               ispublic=True)

def getarg(item):
    ISITEM = (item in sys.argv)
    if ISITEM:
        sys.argv.pop(sys.argv.index(item))
    return ISITEM


if __name__ == '__main__':
  START = getarg('start')
  DEBUG = getarg('debug')
  OFFLINE = getarg('offline')
  HOUR = getarg('hour')
  FRAME = getarg('frame')
  NIGHT = getarg('night')
  
  # Parse everything else
  sys.argv.append('--noauth_local_webserver')
  args = argparser.parse_args()

  
  
  now = datetime.datetime.now()
  here = ephem.Observer()
  here.lon, here.lat = '-76.623434', '39.331628'
  sunrise = here.next_rising(ephem.Sun())
  sunset = here.next_setting(ephem.Sun())

  time_before = datetime.timedelta(minutes=60)
  time_after = datetime.timedelta(minutes=60)
  sunrise = ephem.localtime(sunrise) - time_before
  if START:
    sunrise = now
  else:
    if sunrise > ephem.localtime(sunset):
      sunrise = now
  sunset = ephem.localtime(sunset) + time_after
  
  if HOUR:
    sunset = sunrise + datetime.timedelta(minutes=60)
  
  if NIGHT:
      sunrise = datetime.datetime(now.year, now.month, now.day, 20)
      sunset = sunrise + datetime.timedelta(hours=6)
      if sunrise < now:
          sunrise = now
  

  video_length = (sunset - sunrise).total_seconds() * 1000
  total_frames = 120 * 60
  frame_time = video_length / total_frames
  if FRAME:
      frame_time = 25
  sleep_time = (sunrise - now).total_seconds()
  
  
  title = 'Optical '+datetime.datetime.today().strftime("%Y-%m-%d")
  hostname = socket.gethostname()
  description='''Optical timelapse from a Raspberry PI
  
  Hostname: {hostname}
  Sunrise: {sunrise}
  Sunset: {sunset}
  delta: {frame_time:0.2f} seconds
  '''.format(sunrise=sunrise, sunset=sunset, frame_time=frame_time/1000, hostname=hostname)
  
  
  output = dict(
      sunrise='%s'%sunrise,
      sunset='%s'%sunset,
      runtime=calendar.timegm(time.gmtime()),
      frame_time=frame_time/1000.0,
      video_length=video_length,
      sleep_time=sleep_time,
      title=title,
      description=description,
      hostname=hostname,
  )
  json.dump(output, open(DAILY_FILENAME.replace('.mp4','.json'),'a'), indent=2)
  
  
  
  if DEBUG:
      sleep_time = 2
      frame_time = 3 # every 3 seconds -- simple and quick
      video_length = 16*1000 # for 13 seconds
  
  if NIGHT:
      extra = '-ss 20000000 -ISO 1600 -ex verylong'
  else:
      extra = ''
  
  #-awb auto -ex verylong
  RECORD_COMMAND = "raspiyuv %(extra)s -h 1072 -w 1920 -t %(length)d -tl %(slice)d -o - | %(dir)s/rpi-encode-yuv > %(file)s"
  cmd = RECORD_COMMAND % {"length": video_length,
                          "slice": frame_time,
                          "file": H264_FILENAME,'dir':openmax_dir,"extra":extra}
  CONVERT_COMMAND = "MP4Box -fps 24 -add %(in_file)s %(out_file)s"
  cmd2 = CONVERT_COMMAND % {"in_file": H264_FILENAME, "out_file": MP4_FILENAME}
  RSYNC_COMMAND = 'rsync -ravpP %(in_file)s %(out_file)s'
  cmd3 = RSYNC_COMMAND % {'in_file':MP4_FILENAME, 'out_file':DAILY_FILENAME}
  
  print('Record Command:\n {}'.format(cmd))
  print("  Sleeping for %d seconds" % sleep_time)
  print("  Video Description: {}".format(description))
  
  
  if not OFFLINE:
      try:
          gmail.send_email(hostname+' : Start in {}'.format(sleep_time),
                          'Time-lapse \n {}'.format(description))
      except:
          print 'Failed to email'
  
  time.sleep(sleep_time)
  if not OFFLINE:
      try:
          gmail.send_email(hostname+' : Timelapse',
                      'Starting time-lapse \n {}'.format(description))
      except:
          print 'failed to email'
    
  os.system(cmd)
  os.system(cmd2)
  os.system(cmd3)
  
  if DEBUG:
      sys.exit()
  
  
  if not OFFLINE:
      if not os.path.exists(MP4_FILENAME):
        exit("No video to upload")
        gmail.send_email(hostname+' : Timelapse Failure',
                         'Failed to find Mp4')
  
      # youtube upload
      youtube = get_authenticated_service(args)
      try:
        initialize_upload(youtube, args, title, description)
      except HttpError as e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
        gmail.send_email(hostname+' : Timelapse Failure',
                         'Failed to upload to youtube:\n{}'.format(e))
 
      # flickr upload
      try:
        print flickr.upload(MP4_FILENAME, title, description, 
                            '"Raspberry Pi" IR timelapse timerasp JHU Baltimore Maryland',
                            public=True)
      except Exception as e:
        gmail.send_email(hostname+' : Timelapse Failure',
                         'Failed to upload to flickr:\n{}'.format(e))
  
  # clean up
  os.remove(H264_FILENAME)
  # os.remove(MP4_FILENAME)
  os.rename(MP4_FILENAME, MP4_FILENAME.replace('todays','previous'))
  if not OFFLINE:
    gmail.send_email(hostname+' : Timelapse Success!','Everything is good!')
