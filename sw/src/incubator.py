import json
import logging
import logging.config
import os
import sys
from argparse import ArgumentParser
import time

import wiringpi

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
    wiringpi.pwmSetMode(0)  # PWM_MODE_MS = 0 # TODO: maybe this should be


def interpolate(left, right, p):
    return (1-p) * left + p * right

def get_setpoint(mode, name, time_passed):
    line = mode[name]

    next_time_trsh = 0
    for idx in range(len(line)):
        next_time_trsh += line[idx][1]

        if next_time_trsh < time_passed:
            continue

        old_timestamp = 0 if idx == 0 else line[idx-1][1]
        old_val = line[idx][0] if idx == 0 else line[idx-1][0]

        p = (time_passed - old_timestamp) / (next_time_trsh - old_timestamp)
        return interpolate(old_val, line[idx][0], p)

    return -1 # program finished
    # if cfg["switch_off_time"] == -1;
    #     return -1
    # else:
    #     return cfg["switch_off_time"]

def load_config():
    # should so some validation that gpio are not clashing etc,
    # make nice print outs...dunno
    return {}

def load_mode(path):
    if os.path.isfile(path):
        with open(path, "r") as f:
            cfg = json.load(f)

            cfg["desired_temperature"] = [(val, t * 3600) for val, t in cfg["desired_temperature"]]
            cfg["desired_humidity"] = [(val, t * 3600) for val, t in cfg["desired_humidity"]]

        return cfg
    else:
        raise FileNotFoundError

def run(args):
    # system setup
    cfg = load_config()
    # setup_system()

    # load recipe
    mode = load_mode(args.mode)
    print(mode)

    # preparation for control loop
    time_passed = args.start_time * 3600
    time_start = time.time() - time_passed # pretend time has already passed
    time_prev_it = time_start

    # control loop # TODO:limit Hz
    while True:
        # update time stamps
        time_current = time.time()
        total_dt = time_current - time_prev_it
        time_passed += 600 #total_dt

        # get_current setpoints
        sp_temp = get_setpoint(mode, "desired_temperature", time_passed)
        sp_hmd = get_setpoint(mode, "desired_humidity", time_passed)

        # get current measurements
        ambient_temperatures =

        #PID

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
    run_cmd.add_argument('--start_time', '-st', type=int, default=0, required=False,
                         help="Name of model.")

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
        try:
            opt.func(opt)
        except: # if there are any exceptions
            safety_shutdown()
            exit(1)

