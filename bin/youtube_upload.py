#!/usr/bin/env python
'''youtube upload file'''
import sys
from timerasp import youtube

if __name__ == '__main__':
    youtube.upload(sys.argv[1], 'debug', 'debug video', 'debug,timerasp', True)