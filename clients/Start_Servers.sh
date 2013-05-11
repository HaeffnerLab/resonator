#!/bin/bash
# Start_Servers.sh
# Created: 4/25/13
# Modified: 5/9/13
# Author: Ryan Blais

# Description:
# Start commonly used servers. The node server should be running.
# Output/errors from (python) server startup script redirected to SERVER_LOG.

LABRAD_ACTIVATE="~/.virtualenvs/labrad/bin/activate" # virtualenv activate script
STARTUP_SCRIPT="~/labrad/resonator/clients/NodeClient-control-start.py"
                                        # script to start servers through node
SERVER_LOG="shortcut_logs/servers.log" # log of server start/stop info
VIRTUALENV_ERR=111 # error accessing virtualenv
NODE_ERR=131 # node server not running
STARTUP_ERR=132 # problem starting servers

# Check that node server is running
ps cx | grep twistd > /dev/null
if [ $? -ne 0 ]; then
    echo "The node server is not running. Start the node server first."
    exit $NODE_ERR;
fi

# Activate the labrad virtualenv
if [ -f $LABRAD_ACTIVATE ]; then
    source $LABRAD_ACTIVATE
else;
    echo "Error: Could not activate the labrad virtual environment."
    exit $VIRTUALENV_ERR
fi

# Start servers through node server
if [ -f $STARTUP_SCRIPT ]; then
    python $STARTUP_SCRIPT >> SERVER_LOG 2>&1
else;
    echo "Error: Could not find server startup script: $STARTUP_SCRIPT"
    exit $STARTUP_ERR
fi
