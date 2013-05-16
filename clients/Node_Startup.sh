#!/bin/bash
# Start_Node.sh
# Created: 4/25/13
# Last Modified: 5/16/13
# Author: Ryan Blais

# Description:
# Script to start node server.
# The LabRAD manager should already be started.

LABRAD_ACTIVATE="/home/resonator/.virtualenvs/labrad/bin/activate" # virtualenv activate script
VIRTUALENV_ERR=111 # error accessing virtualenv

# Check if node server is already running
ps cx | grep twistd > /dev/null
if [ $? -eq 0 ]; then
    echo "The node server is already running."
    printf "Press ENTER to close"; read close
    exit 0;
fi

# Activate the labrad virtualenv
if [ -f $LABRAD_ACTIVATE ]; then
    source $LABRAD_ACTIVATE
else
    echo "Error: Could not activate the labrad virtual environment."
    printf "Press ENTER to close"; read close
    exit $VIRTUALENV_ERR
fi

# Start the node server through twistd
twistd -n labradnode
