import logging

import wiringpi


class Fan():
    def __init__(self, gpio_pin_power):
        self.gpio_pin_power = gpio_pin_power

        # setup on/off pin
        wiringpi.pinMode(self.gpio_pin_power, wiringpi.GPIO.OUTPUT)
        self.off() # ensure the off state

    def on(self):
        wiringpi.digitalWrite(self.gpio_pin_power, 1)

    def off(self):
        wiringpi.digitalWrite(self.gpio_pin_power, 0)


class FanRPM(Fan):
    def __init__(self, gpio_pin_power, gpio_pin_rpm, rpm_measurement_time=0.5):
        super(Fan, self).__init__(gpio_pin_power)
        self.gpio_pin_rpm = gpio_pin_rpm
        self.rpm_measurement_time = rpm_measurement_time

        # setup rpm pin
        self._rpm_counter = 0
        wiringpi.pinMode(self.gpio_pin_rpm, wiringpi.GPIO.INPUT)
        wiringpi.pullUpDnControl(self.gpio_pin_rpm, wiringpi.GPIO.PUD_UP)
        wiringpi.wiringPiISR(self.gpio_pin_rpm, wiringpi.GPIO.INT_EDGE_BOTH,
                             self.__rpm_callback)

    def rpm(self):
        # Todo: should be the other way around. reset after measuring,
        # with check for minimum passed time and then get a potentially better
        # measurement?
        self._rpm_counter = 0
        wiringpi.delay(int(self.rpm_measurement_time * 1000))
        rpm = self._rpm_counter * (
                60.0 / self.rpm_measurement_time) / 4.0  # 2 RE/revol. but counting both edges..
        return rpm

    def __rpm_callback(self):
        self._rpm_counter += 1


class FanPWM(Fan):
    def __init__(self, gpio_pin_power, gpio_pin_pwm):
        super(Fan).__init__(gpio_pin_power)
        self.gpio_pin_pwm = gpio_pin_pwm

        # setup control pin
        if gpio_pin_pwm:
            # There is a dedicated pwm control of the fan, we don't need to
            # manually switch the fan on/off.
            wiringpi.pwmSetMode(0)  # PWM_MODE_MS = 0
            wiringpi.pinMode(self.gpio_pin_pwm,
                             wiringpi.GPIO.PWM_OUTPUT)  # pwm only works on GPIO port 18/1
            wiringpi.pullUpDnControl(self.gpio_pin_pwm, wiringpi.GPIO.PUD_UP)
            wiringpi.pwmSetClock(6)  # this parameters correspond to 25kHz
            wiringpi.pwmSetRange(128)
            self.speed = 0
            self.set_speed(self.speed)
        else:
            # sorry, im lazy, not implemented
            raise NotImplementedError

    def set_speed(self, speed):
        if speed >= 0 and speed <= 100:
            self.speed = int(128 - speed * 0.64)
            logging.debug("new speed", self.speed)
            self.speed = speed
            wiringpi.pwmWrite(self.gpio_pin_pwm, self.speed)
        else:
            logging.error("Invalid speed level set. Should be between [0, 100], but {} was given!".format(speed))
            return


# class CoolCold(FanRPM, FanPWM):
#     # TODO: Refactor into a base Fan Class and inherit
#     def __init__(self, gpio_pin_onoff, gpio_pin_pwm, gpio_pin_rpm,
#                  rpm_measurement_time=0.5):
#         super(FanPWM, self).__init__(gpio_pin_onoff, gpio_pin_pwm)
#         super(FanRPM, self).__init__(gpio_pin_onoff, gpio_pin_rpm,
#                                      rpm_measurement_time)
#
#     def rpm(self):
#         # cool cold has some weird issues....hence overwrite
#         self._rpm_counter = 0
#         wiringpi.delay(int(self.rpm_measurement_time * 1000))
#         rpm = self._rpm_counter * (
#                 60.0 / self.rpm_measurement_time) / 4.0  # divide by 2 as to senses per revolution
#         return rpm if rpm < 3400 else 3400  # some weird problm with the pwm...truncate..