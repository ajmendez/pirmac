#!/usr/bin/env python

import os
import sys
import json
from timerasp import flickr

def upload(filename):
    title = ''
    description = ''
    tags = 'timerasp upload'
    
    # attempt to find a information file
    infofile = filename.replace('_video.mp4', '_info.json')
    if os.path.exists(infofile):
        info = json.load(open(infofile, 'r'))
        title = info['title']
        description = info['description']
        tags = info['tags']
    
    tmp = 'Title: {title}\n\nDescription: {description}\n\nTags: {tags}'
    print tmp.format(**locals())
    
    if raw_input('upload? [y/n] ').lower()[0] != 'y':
        print 'Not uploading!'
        return
    
    flickr.upload(filename, title, description, tags)


if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except Exception as e:
        raise ValueError('Pass in a filename')
    if not os.path.exists(filename):
        raise IOError('Missing file: {}'.format(filename))
    
    upload(filename)