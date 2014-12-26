#!/usr/bin/env python
import sys
from timerasp import gmail


if __name__ == '__main__':
    gmail.send_email('notify.py: IP:{}'.format(' '.join(sys.argv[1:])),
                     'Notify was run and is telling you something')
