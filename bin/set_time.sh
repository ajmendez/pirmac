#!/bin/bash
# set the time by passing in a hostname
ssh $1 "sudo date --set \"$(date)\""