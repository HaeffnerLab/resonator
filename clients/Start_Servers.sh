#!/bin/bash
# Start_Servers.sh
# Created: 4/25/13
# Modified:
# Author: Ryan Blais

# Start commonly used servers. The node server should be running.

source ~/.virtualenvs/labrad/bin/activate
python ~/labrad/resonator/clients/NodeClient-control-start.py
sleep 1
