#!/bin/bash

sudo service ntp stop
sudo ntpd -gq
sudo ntpdate time.nist.gov
sudo service ntp start