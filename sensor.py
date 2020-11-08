import logging
import time

import board
import busio
from adafruit_ads1x15 import ads1115, analog_in

MAX_VOLTAGE = 3.3
MIN_VOLTAGE = 0.0

logging.basicConfig(
    filename="HISTORYlistener.log",
    level=logging.DEBUG,
    format="[{asctime}] [{levelname}] {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def clamp_voltage(voltage: float) -> float:
    """It's possible we read a voltage higher than we're supplying.
    Clamp to a maximum of 3.3v to make calculations easier.
    """
    if voltage < MIN_VOLTAGE:
        return MIN_VOLTAGE

    if voltage > MAX_VOLTAGE:
        return MAX_VOLTAGE

    return voltage


def normalise(value, max_value, min_value):
    """Normalise a value to a percentage between max_value and min_value"""
    return abs((value - min_value) / (max_value - min_value))


if __name__ == "__main__":
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    adc = ads1115.ADS1115(i2c_bus)
    channel = analog_in.AnalogIn(adc, ads1115.P0)

    while True:
        percentage_hydration = normalise(
            value=clamp_voltage(channel.voltage),
            # Pass these backwards - open ciruit represents no moisture
            max_value=MIN_VOLTAGE,
            min_value=MAX_VOLTAGE,
        )

        print(f"{percentage_hydration:}")
        time.sleep(0.1)
