#!/usr/bin/env python
import logging

import wiringpi
from fan import Fan


class Haljia5V8W():
    # TODO: Refactor into a base Heater Class and inherit

    # pwmFrequency in Hz = 1.2e6Hz / pwmClock / pwmRange
    # Here: 1.144 Hz
    PWM_CLOCK = 4095
    PWM_RANGE = 4096

    def __init__(self, gpio_pin_heater, gpio_pin_fan):
        self.gpio_pin_heater = gpio_pin_heater
        self.fan = Fan(gpio_pin_fan)

        self.heater_state = 0
        wiringpi.pinMode(self.gpio_pin_heater, wiringpi.GPIO.OUTPUT)
        wiringpi.softPwmCreate(self.gpio_pin_heater ,0, 100)
        wiringpi.pullUpDnControl(self.gpio_pin_heater, wiringpi.GPIO.PUD_DOWN)
        # Set to slowest possible level
        # wiringpi.pwmSetClock(self.PWM_CLOCK)
        # wiringpi.pwmSetRange(self.PWM_RANGE)

        #put everything in a sane state...just in case
        self.heater_off()

    def heater_on(self, heat_level):
        # we always switch on the fan, this way we can have the fan running
        # even if the set the heat_level to zero (no heating)
        self.fan.on()

        if heat_level >= 0 and heat_level <= 100:
            # self.heater_state = int(heat_level * 4096 / 100)
            wiringpi.softPwmWrite(self.gpio_pin_heater, self.heater_state)

    def heater_off(self):
        # todo: should be a property
        self.heater_state = 0
        wiringpi.softPwmWrite(self.gpio_pin_heater, self.heater_state)
        self.fan.off()