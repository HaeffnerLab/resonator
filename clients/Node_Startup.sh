#!/bin/bash
# Start_Node.sh
# Created: 4/25/13
# Modified: 5/9/13
# Author: Ryan Blais

# Description:
# Script to start node server.
# The LabRAD manager should already be started.
# Node server output and errors redirected to NODE_LOG.

LABRAD_ACTIVATE="~/.virtualenvs/labrad/bin/activate" # virtualenv activate script
NODE_LOG="shortcut_logs/node.log" # log file for node server output/errors
VIRTUALENV_ERR=111 # error accessing virtualenv

# Activate the labrad virtualenv
if [ -f ~/.virtualenvs/labrad/bin/activate ]; then
    source $LABRAD_ACTIVATE
else;
    echo "Error: Could not activate the labrad virtual environment."
    exit $VIRTUALENV_ERR
fi

# Start the node server through twistd
# Runs in background and doesn't hangup
nohup twistd -n labradnode & >> $NODE_LOG 2>&1
