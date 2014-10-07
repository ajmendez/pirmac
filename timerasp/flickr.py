#!/usr/bin/env python

import os
import urllib2
import flickrapi
from scintillate import api
from cStringIO import StringIO
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers


class Progress(object):
    def __init__(self):
        self._seen = 0.0

    def update(self, total, size, name):
        self._seen += size
        pct = (self._seen / total) * 100.0
        if (pct%10) == 0:
            print '%s progress: %.2f' % (name, pct)

class file_with_callback(file):
    def __init__(self, path, mode, callback, *args):
        file.__init__(self, path, mode)
        self.seek(0, os.SEEK_END)
        self._total = self.tell()
        self.seek(0)
        self._callback = callback
        self._args = args

    def __len__(self):
        return self._total

    def read(self, size):
        data = file.read(self, size)
        self._callback(self._total, len(data), *self._args)
        return data



def upload(filename, title, description, tags, public=False):
    x = api.Flickr().flickr
    arguments = {'auth_token': x.token_cache.token, 
                 'api_key': x.api_key,
                 'title':title,
                 'description':description,
                 'tags':tags,
                 'is_public':'1' if public else '0'}
    kwargs = flickrapi.make_utf8(arguments)
    kwargs['api_sig'] = x.sign(kwargs)
    url = "https://%s%s" % (x.flickr_host, x.flickr_upload_form)


    register_openers()  
    progress = Progress()
    fh = file_with_callback(filename, 'rb',progress.update, os.path.basename(filename))
    body2 = {"photo": fh}
    body2.update(kwargs)
    datagen, headers = multipart_encode(body2)
    request = urllib2.Request(url, datagen, headers)
    return urllib2.urlopen(request).read()

