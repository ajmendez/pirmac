#!/usr/bin/env python

import sys
from timerasp import flickr

def upload():
    try:
        filename = sys.argv[1]
    except:
        raise ValueError('Need to specify filename')
    
    
    title = ''
    description = ''
    if len(sys.argv) > 2:
        description = ' '.join(sys.argv[2:])
    
    flickr.upload(filename, title, description, '')


if __name__ == '__main__':
    upload()