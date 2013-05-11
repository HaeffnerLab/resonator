#!/bin/bash
# Node_Shutdown.sh
# Created: 4/25/13
# Modified: 5/9/13
# Author: Ryan Blais

# Description:
# Stop all the LabRAD servers running through the node and kill the node server.
# Output/errors from (python) server shutdown script redirected to SERVER_LOG.
# Node server output/errors (should be) already redirected (see Node_Startup.sh)

LABRAD_ACTIVATE="~/.virtualenvs/labrad/bin/activate" # virtualenv activate script
SHUTDOWN_SCRIPT="~/labrad/resonator/clients/NodeClient-control-stop.py"
                                # script to shutdown servers through node server
SERVER_LOG="shortcut_logs/servers.log" # log of server start/stop info
VIRTUALENV_ERR=111 # error accessing virtualenv
SHUTDOWN_ERR=112 # error running server shutdown script


# Check that node server is running
ps cx | grep twistd > /dev/null
if [ $? -ne 0 ]; then
    echo "The node server is not running. No need to shutdown."
    exit 0;
fi

# Activate the labrad virtualenv
if [ -f ~/.virtualenvs/labrad/bin/activate ]; then
    source $LABRAD_ACTIVATE
else;
    echo "Error: Could not activate the labrad virtual environment."
    exit $VIRTUALENV_ERR
fi

# Close connections to servers through node server
if [ -f $SHUTDOWN_SCRIPT ]; then
    python $SHUTDOWN_SCRIPT >> $SERVER_LOG 2>&1
else;
    echo "Error: Could not find node shutdown script: $SHUTDOWN_SCRIPT"
    exit $SHUTDOWN_ERR
fi

# Kill the node server
killall -9 twistd
