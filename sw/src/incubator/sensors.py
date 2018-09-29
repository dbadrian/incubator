import os

import Adafruit_DHT


class DHT():
    sensor_types = {'11': Adafruit_DHT.DHT11,
                    '22': Adafruit_DHT.DHT22,
                    '2302': Adafruit_DHT.AM2302}

    def __init__(self, type_id, gpio_data):
        self.gpio_data = gpio_data
        if type_id in self.sensor_types:
            self.sensor_type = self.sensor_types[type_id]
        else:
            raise ValueError("Specified sensor type does not exist!")

    def read(self):
        hmd, tmp = Adafruit_DHT.read_retry(self.sensor_type, self.gpio_data)
        results = {
            "humidity": hmd,
            "tmp": tmp
        }
        return results


class DS18S20():
    def __init__(self, ):
        self.sensors = []
        try:
            # gather all available sensor on 1w gpio. we kinda assume there is nothing else
            for x in os.listdir("/sys/bus/w1/devices"):
                if (x.split("-")[0] == "28") or (x.split("-")[0] == "10"):
                    self.sensors.append(x)
        except:
            raise Exception  # TODO: Make a new exception here

    def read(self):
        results = {}

        try:
            # 1-wire Slave Dateien gem. der ermittelten Anzahl auslesen
            for sensor in self.sensors:
                fn = "/sys/bus/w1/devices/{}/w1_slave".format(sensor)
                with open(fn, 'r') as f:
                    data = f.read()
                    strval = data.split("\n")[1].split(" ")[9]
                    val = float(strval[2:]) / 1000
                    results[sensor] = val

            return results
        except:
            return results
