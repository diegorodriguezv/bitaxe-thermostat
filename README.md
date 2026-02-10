# bitaxe-thermostat

A simple python script to keep your bitaxe running at optimum performance.

- Increases or decreases the frequency if the temperature of the ASIC chip is too high 
or too low
- Does not tries to modify the ASIC voltage
- Useful if ambient temperature changes a lot

This project is inspired by [bitaxe-temp-monitor](https://github.com/Hurllz/bitaxe-temp-monitor.git),
which aims to overclock several bitaxes by using a hashrate vs voltage vs frequency table. 

Since I use the factory cooling I just wanted to gain a little MHz here and there by 
adjusting the temperature. After some days of doing this manually I started to look for
alternatives and this is the solution.

## Installation

This repository includes a bash script to automatically install dependencies and run 
the script at boot time on Linux with systemd. 

```
sudo ./install.sh <ip> <target temperature>
```

You can check if it is running correctly using systemctl:

```
systemctl status bitaxe-thermostat.service
```

If you want to uninstall it just run the uninstall script, which will stop the service
and remove the unit file.

```
sudo ./uninstall.sh
```

## Usage

If you use other operating system just install the `requests` python module and 
run it manually.

``` 
python3 bitaxe-thermostat <ip> <target temperature>
```
You can use the IP address or the hostname.

The target temperature is in Celsius.

For example:
``` 
python3 bitaxe-thermostat bitaxe 69
```

I recommend using your preferred method to start it at boot time.
