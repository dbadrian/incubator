import time

class PID:
    def __init__(self, Kp, Ki=0.0, Kd=0.0, i_windup_max=10.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.i_windup_max = i_windup_max
        self.reset()

    def reset(self):
        self.last_error = 0.0
        self.last_time = None

        self.p = 0.0
        self.i = 0.0
        self.d = 0.0

    def update(self, error):
        if not self.last_time:
            self.last_time = time.time()
            return


        current_time = time.time()
        dt = current_time - self.last_time
        de = error - self.last_error

        self.p = self.Kp * error
        self.i += error * dt

        self.d = 0.0
        if dt > 0:
            self.d = de / dt

        self.last_time = current_time
        self.last_error = error

        # calc output
        self.output = self.p + (self.Ki * self.i) + (self.Kd * self.d)
        return self.output