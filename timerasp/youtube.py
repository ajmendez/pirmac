import os
import sys
import time
import ephem
import random
import httplib
import httplib2
import datetime

from apiclient.discovery import build
from oauth2client.file import Storage
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.tools import argparser, run_flow
from oauth2client.client import flow_from_clientsecrets


DIRECTORY = os.path.expanduser('~/.limited')
OAUTH_STORAGEFILE = os.path.join(DIRECTORY, 'youtube_oauth2.json')
OAUTH_SECRETSFILE = os.path.join(DIRECTORY, 'youtube_secrets.json')



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



# The OAUTH_SECRETSFILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets



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
""" % OAUTH_SECRETSFILE

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")



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


class Youtube(object):
    def __init__(self, args=None):
        # DEBUG
        sys.argv.append('--noauth_local_webserver')
        if args is None:
            args = argparser.parse_args()
        self.args = args
        self.youtube = None
    
    def authenticate(self):
        if self.youtube != None:
            print 'Already authenticated'
            return
        
        flow = flow_from_clientsecrets(OAUTH_SECRETSFILE,
                                       scope=YOUTUBE_UPLOAD_SCOPE,
                                       message=MISSING_CLIENT_SECRETS_MESSAGE)
        storage = Storage(OAUTH_STORAGEFILE)
        credentials = storage.get()
        
        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)
        
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, 
                             YOUTUBE_API_VERSION,
                             http=credentials.authorize(httplib2.Http()))
    
    def upload(self, filename, privacy=None, **kwargs):
        '''
        privacy must be one of {privacy} Defaults to public
        channelId:
        https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode={two-character-region}&key={YOUR_API_KEY}
        '''.format(privacy=VALID_PRIVACY_STATUSES)
        if privacy is None:
            privacy = VALID_PRIVACY_STATUSES[0]
        snippet = dict(
            title='',
            description='',
            tags='timelapse,baltimore,raspberrypi,noir', # 'tag1, tag2'
            channelId='UCBR8-60-B28hp2BmDPdntcQ',
        )
        snippet.update(kwargs)
        body = dict(
            snippet=snippet
            status=dict(privacyStatus=privacy)
        )
        media_body = MediaFileUpload(filename, chunksize=-1, resumable=True)
        
        videos = self.youtube.videos()
        request = videos.insert(part=",".join(body.keys()),
                                body=body,
                                media_body=media_body)
        resumable_upload(request)


def upload(filename, title, description, public=False):
    # youtube upload
    valid_index = 0 if public else 1
    try:
        youtube = Youtube()
        youtube.upload(filename, 
                       title=title, 
                       description=description,
                       privacy=VALID_PRIVACY_STATUSES[valid_index])
    except HttpError as e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
      raise
    