#!/usr/bin/env python
import sys
from timerasp import gmail


gmail.send_email('notify.py: IP:{}'.format(' '.join(sys.argv[1:])),
		 'Notify was run and is telling you something')
