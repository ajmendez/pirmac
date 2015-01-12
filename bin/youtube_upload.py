#!/usr/bin/env python
'''youtube upload file'''
import os
import sys
import json
from timerasp import youtube

if __name__ == '__main__':
    params = dict(
        title='debug',
        description='debug video',
        tags='debug, timerasp',
        private=True,
    )
    infofile = sys.argv[1].replace('.mp4', '.json')
    if os.path.exists(infofile):
        print "loading info from: {}".format(infofile)
        with open(infofile,'r') as f:
            tmp = json.load(f)
        for key in ['title', 'description', 'tags']:
            params[key] = tmp[key]
    
    youtube.upload(sys.argv[1], **params)