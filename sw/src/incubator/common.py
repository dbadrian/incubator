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