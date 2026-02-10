# bitaxe-thermostat:
# - connects to a single bitaxe
# - reads its settings
# - keeps a rolling average of the temp
# - tries to keep a target temperature

import requests
import time
import argparse
from collections import deque


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
    temps = deque()
    num_infos = 0
    errors = 0
    window = 15
    while True:
        time.sleep(1)
        info = get_system_info(ip)
        if not info:
            errors += 1
            continue
        temp = info["temp"]
        temps.append(temp)
        num_infos += 1
        if len(temps) > window:
            temps.popleft()
        if num_infos == window:
            num_infos = 0
            avg = sum(temps) / len(temps)
            changed = False
            if target - avg > 0.5:
                freq += 5
                changed = True
            elif target - avg < -0.5:
                freq -= 5
                changed = True
            if errors:
                print(f"unable to fetch system info x{errors}")
                errors = 0
            if changed:
                if not set_system_settings(ip, freq):
                    print(f"tried setting {freq} but failed")
                else:
                    print(f"changed frequency to {freq}")


def autotune(ip, target):
    info = get_system_info(ip)
    if not info:
        print("unable to fetch first system info")
        return
    freq = info["frequency"]
    print(f"first frequency {freq}")
    try:
        loop(ip, target, freq)
    except KeyboardInterrupt:
        print()
        print("bye")
    except Exception as exc:
        print("error", exc)
    finally:
        restore(ip, freq)


def restore(ip, freq):
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
