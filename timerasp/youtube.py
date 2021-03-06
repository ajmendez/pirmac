
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

try:
    from apiclient.discovery import build
    from apiclient.errors import HttpError
    from apiclient.http import MediaFileUpload
except:
    # WTF!
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    
    
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from oauth2client.client import flow_from_clientsecrets



CLIENT_SECRETS_FILE = os.path.expanduser("~/.limited/youtube_client.json")
STORAGE_FILE = os.path.expanduser('~/.limited/youtube_oauth2.json')





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
#  https://developers.google.com/api-client-library/python/guide/aaa_client_secrets


# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """ WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   {clientsecret}
with information from the Developers Console
https://cloud.google.com/console

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""".format(clientsecret=CLIENT_SECRETS_FILE)

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")



def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage(STORAGE_FILE)
  try:
      credentials = storage.get()
  except:
      # not sure why I had to wrap this
      credentials = None
  
  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def setup():
    '''Attempt to setup a nice youtube objeect'''
    # do not actually parse arguments
    args = argparser.parse_args(args=[])
    args.noauth_local_webserver=True
    youtube = get_authenticated_service(args)
    return youtube






def resumable_upload(insert_request):
  '''This method implements an exponential backoff strategy to resume a
  failed upload. Rather than exit throw an error.'''
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      status, response = insert_request.next_chunk()
      if 'id' in response:
        print "Video id '%s' was successfully uploaded." % response['id']
        return response['id']
      else:
        # exit("The upload failed with an unexpected response: %s" % response)
        raise ValueError("The upload failed with an unexpected response: %s" % response)
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
        # exit("No longer attempting to retry.")
        raise ValueError('No longer attempting to retry.')

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)



def initialize_upload(youtube, filename, private=True, **kwargs):
  '''start the upload
  kwargs handles title, desctiption, tags
  
  '''
  
  # ensure that we have some sane privacy things
  if isinstance(private, str):
      privacy = private
      assert private in VALID_PRIVACY_STATUSES
  elif private:
      privacy = VALID_PRIVACY_STATUSES[1]
  else:
      privacy = VALID_PRIVACY_STATUSES[0]
  tags = None
  
  
  # build the body
  body=dict(
    snippet=dict(
      title='title',
      description='description',
      tags='timerasp',
      categoryId="1", # arts
    ),
    status=dict(
      privacyStatus=privacy,
    )
  )
  body['snippet'].update(kwargs)

  # build the media 
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
  media_body = MediaFileUpload(filename, chunksize=-1, resumable=True)
  
  
  
  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=media_body,
  )

  return resumable_upload(insert_request)






def upload(filename, title, description, tags, private=True):
    '''Uploads a video to youtube'''
    tmp = dict(
        title=title, 
        description=description,
        tags=tags,
        private=private,
    )
    try:
        api = setup()
        youtube_ident = initialize_upload(api, filename, **tmp)
        return youtube_ident
    except HttpError as e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
      raise
    



if __name__ == "__main__":
    if len(sys.argv) == 1:
        print setup()
    else:
        print upload(sys.argv[1], 'debug', 'debug video', 'debug,timerasp', True)