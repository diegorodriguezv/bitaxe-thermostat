#!/usr/bin/env bash

# Run the program using its virtual environment.

# Make sure script is not run by root
if [ "$(id -u)" == "0" ]; then
   echo "This script must NOT be run as root" 1>&2
   exit 1
fi

. ./venv/bin/activate

# Replace the shell with the python process so the service can stop it correctly
exec python3 -u bitaxe-thermostat.py $@
