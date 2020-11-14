"""sensor - measure soil hydration percentage"""

import logging
import os
import sys
import time

import board
import busio
import requests
from adafruit_ads1x15 import ads1115, analog_in

MIN_VOLTAGE = 0.0
MAX_VOLTAGE = 3.3

# Voltages read by the probbe in given environments
VOLTAGE_WHEN_WATER = 1.2
VOLTAGE_WHEN_AIR = 3.2


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between a minimum and maximum"""
    if value < min_value:
        return min_value

    if value > max_value:
        return max_value

    return value


def normalise(value, max_value: float, min_value: float) -> float:
    """Normalise a value to a percentage between max_value and min_value"""
    return abs((value - min_value) / (max_value - min_value))


if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    api_token = os.environ["CACTUS_API_TOKEN"]
    api_endpoint = os.environ["CACTUS_API_ENDPOINT"]

    i2c_bus = busio.I2C(board.SCL, board.SDA)
    adc = ads1115.ADS1115(i2c_bus)
    channel = analog_in.AnalogIn(adc, ads1115.P0)

    while True:
        # Read the raw voltage from the sensor and ensure it's in a range
        # we expected. The adc can report more tha 3.3v, despite that
        # being all the voltage it's supplied with... Magic!
        clamped_voltage = clamp(channel.voltage, MIN_VOLTAGE, MAX_VOLTAGE)

        # The max voltage voltage I read with the sensor in open air was about
        # VOLTAGE_WHEN_AIR, and VOLTAGE_WHEN_WATER when fully submerged in water.
        # We interpolate a value from the voltage we read that's somewhere
        # between these two, as will be the case with damp soil - not air, nor water.
        percentage_hydration = normalise(
            clamped_voltage, VOLTAGE_WHEN_WATER, VOLTAGE_WHEN_AIR
        )

        requests.post(
            api_endpoint,
            json={"hydration": percentage_hydration},
            headers={"X-Cactus-Auth": api_token},
        )
        logging.info("Sent a hydration of %.1f to the API", percentage_hydration)

        time.sleep(1)
