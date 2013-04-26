#!/bin/bash
# Start_Node.sh
# Created: 4/25/13
# Modified:
# Author: Ryan Blais

# Script to start node server and use it to start commonly used servers.
# The LabRAD manager should already be started.

# Start the node server
source ~/.virtualenvs/labrad/bin/activate
nohup twistd -n labradnode &
sleep 2

# Start commonly used servers and/or clients
nohup python ~/labrad/resonator/clients/NodeClient-control-start.py
sleep 2
