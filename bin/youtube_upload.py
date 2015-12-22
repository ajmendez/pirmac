#!/usr/bin/env python
'''youtube upload file'''
import os
import sys
import json
from timerasp import youtube

def upload(filename):
    '''Upload to youtube'''
    params = dict(
        title='debug',
        description='debug video',
        tags='debug, timerasp',
        private=True,
    )
    infofile = filename.replace('_video.mp4', '_info.json')
    if os.path.exists(infofile) & (infofile != filename):
        print "loading info from: {}".format(infofile)
        with open(infofile,'r') as f:
            tmp = json.load(f)
        for key in ['title', 'description', 'tags']:
            params[key] = tmp[key]
    
    tmp = 'Title: {title}\n\nDescription: {description}\n\nTags: {tags}'
    print tmp.format(**params)
    
    if raw_input('upload? [y/n] ').lower()[0] != 'y':
        print 'Not uploading!'
        return
    
    youtube.upload(filename, **params)

if __name__ == '__main__':
    upload(sys.argv[1])