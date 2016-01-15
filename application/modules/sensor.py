import RPi.GPIO as GPIO


class WaterSensor:

    def __init__(self, name, sensor_pin, servo_pins):
        self.name = name
        self.sensor_pin = sensor_pin
        self.servo_pins = servo_pins

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sensor_pin, GPIO.IN)

        for pin in self.servo_pins:
            GPIO.set(pin, GPIO.OUT)

        GPIO.add_event_detect(self.sensor_pin,  GPIO.BOTH, callback=self.sensor_callback)

    def sensor_callback(self, channel):
        print "{} CALLALALALAL".format(self.name)

    def __del__(self):
        GPIO.cleanup()



