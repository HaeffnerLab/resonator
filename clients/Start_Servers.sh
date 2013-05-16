#!/bin/bash
# Start_Servers.sh
# Created: 4/25/13
# Last Modified: 5/16/13
# Author: Ryan Blais

# Description:
# Start commonly used servers. The node server should be running.

LABRAD_ACTIVATE="/home/resonator/.virtualenvs/labrad/bin/activate" # virtualenv activate script
STARTUP_SCRIPT="/home/resonator/labrad/resonator/clients/NodeClient-control-start.py"
                                        # script to start servers through node
VIRTUALENV_ERR=111 # error accessing virtualenv
NODE_ERR=131 # node server not running
STARTUP_ERR=132 # problem starting servers

# Check that node server is running
ps cx | grep twistd > /dev/null
if [ $? -ne 0 ]; then
    echo "Error: The node server is not running. Start the node server first."
    printf "Press ENTER to close"; read close
    exit $NODE_ERR;
fi

# Activate the labrad virtualenv
if [ -f $LABRAD_ACTIVATE ]; then
    source $LABRAD_ACTIVATE
else
    echo "Error: Could not activate the labrad virtual environment."
    printf "Press ENTER to close"; read close
    exit $VIRTUALENV_ERR
fi

# Start servers through node server
if [ -f $STARTUP_SCRIPT ]; then
    python $STARTUP_SCRIPT
else
    echo "Error: Could not find server startup script: $STARTUP_SCRIPT"
    printf "Press ENTER to close"; read close
    exit $STARTUP_ERR
fi

# Prompt to close terminal
printf "Press ENTER to close"; read close
exit 0
