#!/usr/bin/env bash

# Install bitaxe-thermostat as a systemd service so it runs at boot time.

# Make sure that there are two arguments
if [ $# != 2 ]; then
    echo "You must provide two arguments: 'sudo ./install.sh <ip> <target>'" 1>&2
    exit 1
fi

# Make sure only root can run this script
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root: 'sudo ./install.sh <ip> <target>'" 1>&2
    exit 1
fi

# The user that started the command (since sudo was used, root is the active user)
user=$(logname)

# Configure python dependencies as a normal user
sudo -u $user ./configure.sh

# Create the service unit file
cat << _contents > /etc/systemd/system/bitaxe-thermostat.service
[Unit]
Description=A simple python script to keep your bitaxe running at optimum performance.
After=network-online.target

[Service]
Type=simple
Restart=always
User=$(logname)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/run.sh $1 $2

[Install]
WantedBy=default.target
_contents

# Stop in case it is running
systemctl daemon-reload
systemctl stop bitaxe-thermostat.service

# Enable and start the service
systemctl daemon-reload
systemctl enable --now bitaxe-thermostat.service
