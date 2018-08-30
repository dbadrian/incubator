#!/usr/bin/env python
import wiringpi
import time


class Fan():
    def __init__(self, pin_onoff, pin_rpm, rpm_measurement_time=0.5):
        self.pin_onoff = pin_onoff
        self.pin_control = 1
        self.pin_rpm = pin_rpm
        self.rpm_counter = 0
        self.rpm_measurement_time = rpm_measurement_time
        self.speed = 1

        # setup on/off pin
        wiringpi.pinMode(self.pin_onoff, wiringpi.GPIO.OUTPUT)

        # setup rpm pin
        wiringpi.pinMode(self.pin_rpm, wiringpi.GPIO.INPUT)
        wiringpi.pullUpDnControl(self.pin_rpm, wiringpi.GPIO.PUD_UP)
        wiringpi.wiringPiISR(self.pin_rpm, wiringpi.GPIO.INT_EDGE_BOTH, self.__rpm_callback)

       # setup control pin
        wiringpi.pwmSetMode(0) # PWM_MODE_MS = 0
        wiringpi.pinMode(self.pin_control, wiringpi.GPIO.PWM_OUTPUT)      # pwm only works on GPIO port 18/1
        wiringpi.pwmSetClock(6)     # this parameters correspond to 25kHz
        wiringpi.pwmSetRange(128)

    def on(self):
        wiringpi.digitalWrite(self.pin_onoff, 1)

    def off(self):
        wiringpi.digitalWrite(self.pin_onoff, 0)

    def set_speed(self, speed):
        #todo: should be a property
        # self.speed = int(128 - speed * 0.64)
        # print("new speed", self.speed)
        wiringpi.pwmWrite(self.pin_control, self.speed)

    def rpm(self):
        self.rpm_counter = 0
        wiringpi.delay(int(self.rpm_measurement_time * 1000))
        return self.rpm_counter * (60.0/self.rpm_measurement_time) / 4.0 # divide by 2 as to senses per revolution

    def __rpm_callback(self):
        self.rpm_counter += 1


def main():
    print("setup")
    # wiringpi.pwmSetMode(0) # PWM_MODE_MS = 0
    wiringpi.wiringPiSetup()

    print()

    fan = Fan(0, 2)

    # stop fan
    print("resetting fan...")
    fan.off()
    time.sleep(1)

    print("starting fan...")
    fan.on()
    time.sleep(2)

    print("set minimum speed")
    fan.set_speed(0)
    time.sleep(1)

    for _ in range(5):
        print("RPM: ", fan.rpm())

    print("set maximum speed")
    fan.set_speed(100)
    time.sleep(1)

    for _ in range(5):
        print("RPM: ", fan.rpm())

    print("set minimum speed")
    fan.set_speed(0)
    time.sleep(1)

    for _ in range(5):
        print("RPM: ", fan.rpm())



    print("...and turning everything off again")
    fan.off()

if __name__ == "__main__":
    main()