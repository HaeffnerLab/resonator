#!/bin/bash
# GUI_Start.sh
# Created: 4/25/13
# Modified:
# Author: Ryan Blais

# Start the gui
source ~/.virtualenvs/labrad/bin/activate
nohup python ~/labrad/resonator/clients/ResonatorGUI.py
sleep 2
