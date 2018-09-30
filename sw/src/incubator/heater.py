#!/usr/bin/env python
import logging

import wiringpi
from .fan import Fan

logger = logging.getLogger(__name__)

class Haljia5V8W():
    # TODO: Refactor into a base Heater Class and inherit

    def __init__(self, gpio_pin_heater, gpio_pin_fan):
        self.gpio_pin_heater = gpio_pin_heater
        self.fan = Fan(gpio_pin_fan)

        self.heater_state = 0
        wiringpi.pinMode(self.gpio_pin_heater, wiringpi.GPIO.OUTPUT)
        wiringpi.softPwmCreate(self.gpio_pin_heater, 0, 100)

        #put everything in a sane state...just in case
        self.heater_off()

    def heater_on(self, heat_level):

        heat_level = max(0, min(100, heat_level))
        self.heater_state = int(heat_level)

        # we always switch on the fan, this way we can have the fan running
        # even if the set the heat_level to zero (no heating)
        if heat_level > 10 and heat_level <= 100:
            logger.debug("Switching heater on@{}%".format(heat_level))
            self.fan.on()
            # self.heater_state = int(heat_level * 4096 / 100)
            wiringpi.softPwmWrite(self.gpio_pin_heater, self.heater_state)
        elif heat_level >= 0 and heat_level <= 10:
            logger.debug("Switching heater off by thresholding")
            self.fan.off()
            self.heater_off()


    def heater_off(self):
        # todo: should be a property
        self.heater_state = 0
        wiringpi.softPwmWrite(self.gpio_pin_heater, self.heater_state)
        self.fan.off()