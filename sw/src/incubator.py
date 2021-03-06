import json
import logging
import logging.config
import os
import sys
from argparse import ArgumentParser
import time

import numpy as np

import wiringpi

from incubator.common import get_setpoint
from incubator.sensors import DHT, DS18S20
from incubator.pid import PID
from incubator.heater import Haljia5V8W

def setup_logging(
        path='logger.json',
        level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration"""
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)

setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setup_wiringpi():
    wiringpi.wiringPiSetup()
    wiringpi.pwmSetMode(0)  # PWM_MODE_MS = 0 # TODO: maybe this should be


def load_config(path):
    # should so some validation that gpio are not clashing etc,
    # make nice print outs...dunno\
    if os.path.isfile(path):
        with open(path, 'r') as f:
            cfg = json.load(f)
        return cfg
    else:
        raise FileNotFoundError

def load_mode(path):
    if os.path.isfile(path):
        with open(path, "r") as f:
            cfg = json.load(f)

            cfg["desired_temperature"] = [(val, t * 3600) for val, t in cfg["desired_temperature"]]
            cfg["desired_humidity"] = [(val, t * 3600) for val, t in cfg["desired_humidity"]]

        return cfg
    else:
        raise FileNotFoundError

def getSensorMeasurements(ambient_sensors, food_sensors):
    res = {}

    # food sensors
    fds = food_sensors.read()
    logger.debug("FS-TMP (raw): {}".format(fds))
    res["food_temp_mean"] = np.mean([tmp for _, tmp in fds.items()])
    logger.debug("FS-TMP (mean): {}".format(res["food_temp_mean"]))

    # ambient sensors
    ambs = [s.read() for s in ambient_sensors]
    ambs = [ms for ms in ambs if ms["tmp"] is not None]
    if ambs:
        logger.debug("AMB-TMP (raw): {}".format(ambs))
        res["ambient_temp_mean"] = np.mean([sensor["tmp"] for sensor in ambs if sensor["tmp"] is not None])
        logger.debug("AMB-TMP (mean): {}".format(res["ambient_temp_mean"]))

        logger.debug("AMB-HMD (raw): {}".format(ambs))
        res["ambient_hmd_mean"] = np.mean([sensor["humidity"] for sensor in ambs if sensor["humidity"] is not None])
        logger.debug("AMB-HMD (mean): {}".format(res["ambient_hmd_mean"]))
    else:
        res["ambient_temp_mean"] = -1.0
        res["ambient_hmd_mean"]= -1.0
        print("Cant reach ambient sensors")

    return res

def control_loop(desired_control_frequency):
    def control_loop_decorator(func):
        def func_wrapper(*args, **kwargs):
            control_loop_start = time.time()

            res = func(*args, **kwargs)

            diff = time.time() - control_loop_start
            if diff > (1.0/desired_control_frequency):
                logger.debug("Missed desired control frequecy (%f) = %f", desired_control_frequency, 1.0/diff)
            else:
                sleep_time = np.abs((1.0/desired_control_frequency) - diff)
                logger.debug("Faster than desired control frequency - going to sleep: %f", sleep_time)
                time.sleep(sleep_time)

            return res
        return func_wrapper
    return control_loop_decorator

def run(args):
    logger.debug(args)
    # system setup
    print(":: Loading Config")
    cfg = load_config(args.cfg)
    logger.debug(cfg)

    # load recipe
    print(":: Loading Mode")
    mode = load_mode(args.mode)
    logger.debug(mode)

    print(":: Setting Up WiringPi")

    setup_wiringpi()

    # todo: hardcoded, make agnostic
    print(":: Setting Up Sensors")
    ambient_sensors = [DHT(s["type_id"], s['gpio_data']) for s in cfg["ambient_sensors"]]
    logger.debug(ambient_sensors)
    food_sensors = DS18S20()

    # preparation for control loop
    time_passed = args.start_time * 3600
    time_start = time.time() - time_passed # pretend time has already passed
    time_prev_it = time_start

    print(":: Setting Up Heater")
    heater = Haljia5V8W(cfg["heater"][0]["gpio_pin_heater"], cfg["heater"][0]["gpio_pin_fan"])
    hPID = PID(args.kp, args.ki, args.kd)

    # control loop # TODO:limit Hz
    while True:
        # # update time stamps
        time_current = time.time()
        total_dt = time_current - time_prev_it
        time_passed += total_dt * args.time_scale
        time_prev_it = time_current

        # get_current setpoints
        sp_temp = get_setpoint(mode, "desired_temperature", time_passed)
        sp_hmd = get_setpoint(mode, "desired_humidity", time_passed)
        logger.debug("Setpoints@{} :: HMD={} TMP={}".format(time_passed, sp_hmd, sp_temp))

        # Get updated measurements
        res = getSensorMeasurements(ambient_sensors, food_sensors)

        # error
        err_hmd = sp_hmd - res['ambient_hmd_mean']
        print("TEMP USED FOR ERROR:", sp_temp - res['food_temp_mean'])
        # err_tmp = sp_temp - np.mean([res['food_temp_mean'], res['ambient_temp_mean']])
        err_tmp = sp_temp - res['food_temp_mean']
        logger.debug("Error@{} :: HMD={} TMP={}".format(time_passed, err_hmd, err_tmp))

        heater_feedback = hPID.update(err_tmp)
        logger.debug("Feedback Heater: {}".format(heater_feedback))
        if heater_feedback and heater_feedback > 0 and res['ambient_temp_mean'] < 40:
            heater.heater_on(heater_feedback)
        else:
            heater.heater_off()
            # switch on fans?

        time.sleep(2)



def configurate(args):
    pass

def safety_shutdown():
    # mail and send text message
    pass


if __name__ == "__main__":
    parser = ArgumentParser(prog='incubator',
                            description="Temperature and Humdity Control for Incubation of なに")
    subparsers = parser.add_subparsers()

    # Training Mode
    run_cmd = subparsers.add_parser(name="run",
                                    help="Execute a 'recipe'")
    run_cmd.set_defaults(func=run)

    run_cmd.add_argument('--mode', '-m', type=str, required=True, help="Name of model.")
    run_cmd.add_argument('--cfg', '-c', type=str, required=True, help="Path to config file.")
    run_cmd.add_argument('--start_time', '-st', type=int, default=0, required=False,
                         help="Name of model.")
    run_cmd.add_argument('--time_scale', '-ts', type=int, default=1, required=False,
                         help="Play back faster...for debugging")
    run_cmd.add_argument('--kp', type=float, default=60,
                         required=False)
    run_cmd.add_argument('--ki', type=float, default=0.01,
                         required=False)
    run_cmd.add_argument('--kd', type=float, default=10.0,
                         required=False)

    # Testing Mode
    cfg_cmd = subparsers.add_parser(name="configurate",
                                    help="Configure the Incubators sensors etc.")
    cfg_cmd.set_defaults(func=configurate)


    # Parse command-line arguments and run subroutines
    opt = parser.parse_args()

    # No arguments passed? Print help and quit, otherwise call subroutine
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)
    else:
        # try:
        opt.func(opt)
        # except: # if there are any exceptions
        #     safety_shutdown()
        #     exit(1)

