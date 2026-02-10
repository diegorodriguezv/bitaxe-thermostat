#!/usr/bin/env bash

# Uninstall bitaxe-thermostat systemd service.

# Make sure only root can run this script
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root: 'sudo ./install.sh <ip> <target>'" 1>&2
    exit 1
fi

# Disable the service
systemctl disable --now bitaxe-thermostat.service
rm /etc/systemd/system/bitaxe-thermostat.service
systemctl daemon-reload
