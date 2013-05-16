#!/bin/bash
# Node_Shutdown.sh
# Created: 4/25/13
# Last Modified: 5/16/13
# Author: Ryan Blais

# Description:
# Stop all the LabRAD servers running through the node and kill the node server.

LABRAD_ACTIVATE="/home/resonator/.virtualenvs/labrad/bin/activate" # virtualenv activate script
SHUTDOWN_SCRIPT="/home/resonator/labrad/resonator/clients/NodeClient-control-stop.py"
                                # script to shutdown servers through node server
VIRTUALENV_ERR=111 # error accessing virtualenv
SHUTDOWN_ERR=112 # error running server shutdown script


# Check that node server is running
ps cx | grep twistd > /dev/null
if [ $? -ne 0 ]; then
    echo "The node server is not running. No need to shutdown."
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

# Close connections to servers through node server
if [ -f $SHUTDOWN_SCRIPT ]; then
    python $SHUTDOWN_SCRIPT
else
    echo "Error: Could not find node shutdown script: $SHUTDOWN_SCRIPT"
    printf "Press ENTER to close"; read close
    exit $SHUTDOWN_ERR
fi

# Kill the node server
sleep 1
killall -9 twistd

# Prompt to close terminal
printf "Press ENTER to close"; read close
exit 0
