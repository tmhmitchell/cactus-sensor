import logging
import time

import board
import busio
from adafruit_ads1x15 import ads1115, analog_in

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
    if voltage < 0.0:
        return 0.0

    if voltage > 3.3:
        return 3.3

    return voltage


if __name__ == "__main__":
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    adc = ads1115.ADS1115(i2c_bus)
    channel = analog_in.AnalogIn(adc, ads1115.P0)

    while True:
        clamped_voltage = clamp_voltage(channel.voltage)

        print(f"{clamped_voltage}v out of 3.3v")
        time.sleep(0.1)
