#!/usr/bin/env bash

# Run the program using its virtual environment.

# Make sure script is not run by root
if [ "$(id -u)" == "0" ]; then
   echo "This script must NOT be run as root" 1>&2
   exit 1
fi
. ./virtualenv/bin/activate
python3 bitaxe-thermostat.py
