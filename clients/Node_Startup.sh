#!/bin/bash
# Start_Node.sh
# Created: 4/25/13
# Modified:
# Author: Ryan Blais

# Script to start node server.
# The LabRAD manager should already be started.

# Start the node server
source ~/.virtualenvs/labrad/bin/activate
nohup twistd -n labradnode &
sleep 1
