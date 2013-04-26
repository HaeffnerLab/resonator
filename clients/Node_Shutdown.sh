#!/bin/bash
# Node_Shutdown.sh
# Created: 4/25/13
# Modified:
# Author: Ryan Blais

# Stop all the LabRAD servers running through the node.
# Kill the node server.

# Close connections to servers
source ~/.virtualenvs/labrad/bin/activate
python ~/labrad/resonator/clients/NodeClient-control-stop.py
sleep 2

# Kill the node server
killall -9 twistd
sleep 2
