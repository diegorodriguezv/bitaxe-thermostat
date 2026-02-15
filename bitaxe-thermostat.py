# bitaxe-thermostat:
# - connects to a single bitaxe
# - reads its settings
# - keeps a rolling average of the temp
# - tries to keep a target temperature

import requests
import time
import argparse
from collections import deque
import signal
import json
import os


CONFIG_FILE = "config.json"


def get_system_info(bitaxe_ip):
    try:
        response = requests.get(f"http://{bitaxe_ip}/api/system/info", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def set_system_settings(bitaxe_ip, frequency):
    settings = {"frequency": frequency}
    try:
        response = requests.patch(
            f"http://{bitaxe_ip}/api/system", json=settings, timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def loop(ip, target, freq):
    last_config_refresh = 0
    config = load_config()
    temps = deque()
    num_infos = 0
    errors = 0
    while True:
        if time.time() - last_config_refresh > 5:
            config = load_config()
            last_config_refresh = time.time()
        frequency_step = config["frequency_step"]
        max_frequency = config["max_frequency"]
        min_frequency = config["min_frequency"]
        monitor_interval = config["monitor_interval"]
        refresh_interval = config["refresh_interval"]
        temp_tolerance = config["temp_tolerance"]
        time.sleep(refresh_interval)
        info = get_system_info(ip)
        if not info:
            errors += 1
            continue
        temp = info["temp"]
        temps.append(temp)
        num_infos += 1
        if len(temps) > monitor_interval:
            temps.popleft()
        if num_infos == monitor_interval:
            num_infos = 0
            avg = sum(temps) / len(temps)
            changed = False
            if (
                freq < min_frequency
                or target - avg > temp_tolerance
                and freq < max_frequency
            ):
                freq += frequency_step
                changed = True
            elif (
                freq > max_frequency
                or target - avg < -temp_tolerance
                and freq > min_frequency
            ):
                freq -= frequency_step
                changed = True
            if errors:
                print(f"unable to fetch system info x{errors}")
                errors = 0
            if changed:
                if not set_system_settings(ip, freq):
                    print(f"tried setting {freq} but failed")
                else:
                    print(f"changed frequency to {freq}")


def get_default_config():
    return {
        "frequency_step": 5,
        "max_frequency": 650,
        "min_frequency": 525,
        "monitor_interval": 15,
        "refresh_interval": 1,
        "temp_tolerance": 0.5,
    }


def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(get_default_config())
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        save_config(get_default_config())
        return get_default_config()


def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


def autotune(ip, target):
    info = get_system_info(ip)
    if not info:
        print("unable to fetch first system info")
        return
    freq = info["frequency"]
    print(f"first frequency {freq}")

    def handle_signal(signum, frame):
        print(f"terminated with signal {signum}")
        restore(ip, freq)
        exit()

    signal.signal(signal.SIGTERM, handle_signal)
    try:
        loop(ip, target, freq)
    except KeyboardInterrupt:
        print()
        print("bye")
    except Exception as exc:
        print("error", exc)
    finally:
        restore(ip, freq)


is_running = True


def restore(ip, freq):
    global is_running
    if not is_running:
        return
    is_running = False
    print("restoring original settings")
    tries = 0
    succeeded = False
    while not succeeded or tries > 60:
        if tries > 0:
            print("retrying...")
        succeeded = set_system_settings(ip, freq)
        tries += 1
        time.sleep(1)
    suffix = "ies" if tries > 1 else "y"
    prefix = "changed to" if succeeded else "unable to change to"
    if succeeded:
        print(f"{prefix} original frequency ({freq}) in {tries} tr{suffix}")
    else:
        print(f"{prefix} original frequency ({freq}) in {tries} tr{suffix}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="tries to keep the temperature of a bitaxe at a certain target by \
        increasing or decreasing the frequency"
    )
    parser.add_argument("ip", help="ip or hostname of the bitaxe")
    parser.add_argument("target", help="target temperature", type=int)
    args = parser.parse_args()
    autotune(args.ip, args.target)
