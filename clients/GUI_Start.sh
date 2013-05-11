#!/bin/bash
# GUI_Start.sh
# Created: 4/25/13
# Modified: 5/10/13
# Author: Ryan Blais

# Description:
# Starts the experimental control gui. 
# Redirects output/errors from gui to GUI_LOG.

LABRAD_ACTIVATE="~/.virtualenvs/labrad/bin/activate" # virtualenv activate script
GUI_SCRIPT="~/labrad/resonator/clients/ResonatorGUI.py" # script that starts the gui (from python)
GUI_LOG="shortcut_logs/gui.log" # log of gui output/error info
GUI_START_ERR=129 # could not start the gui

# Activate the labrad virtualenv
if [ -f $LABRAD_ACTIVATE ]; then
    source $LABRAD_ACTIVATE
else;
    echo "Error: Could not activate the labrad virtual environment."
    exit $VIRTUALENV_ERR
fi

# Start the gui
if [ -f $GUI_SCRIPT ]; then
    nohup python $GUI_SCRIPT >> $GUI_LOG 2>&1
else
    echo "Error: Could not find the gui startup script: $GUI_SCRIPT"
    exit $GUI_START_ERR
fi
