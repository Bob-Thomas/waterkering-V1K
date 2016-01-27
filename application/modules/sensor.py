import RPi.GPIO as GPIO
import time
import requests

GPIO.setmode(GPIO.BCM)


class GPIOHelper:
    """Class that helps simplyfying the GPIO methods

        Attributes:
            name   Then name of the sensor
            pin    Pin number on the rpi in BCM or RPI mode
            mode   The mode you want the pin to be in [ OUT, IN, IN-RCT, SERVO ] default OUT

        Functions:
            init            Initializes the pin and variables based on the Attributes
            read_rct        Return value of the pin with an RC time method
            create_listener Creates a listener for on a event on the pin for events look ath the RPi.GPIO Docs
            send_signal     Send a signal to the pin [GPIO.HIGH, GPIO.LOW] = 1, 0
            get_input       Return the input on the pin = 1, 0
            turn_servo      Send a pwm signal to the pin with rotational information
    """

    def __init__(self, name, pin, mode='OUT'):
        self.name = ""
        self.name = name
        self.pin = pin
        self.mode = mode
        self.servo_pos = 0
        if mode is 'OUT':
            GPIO.setup(self.pin, GPIO.OUT)
        elif mode is 'IN':
            print self.pin
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        elif mode is "IN-RCT":
            GPIO.setup(self.pin, GPIO.OUT)

        elif mode is 'SERVO':
            GPIO.setup(self.pin, GPIO.OUT)
            self.pwm = GPIO.PWM(self.pin, 100)
            self.pwm.start(5)

    def read_rct(self):
        reading = 0
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.setup(self.pin, GPIO.IN)
        # This takes about 1 millisecond per loop cycle
        while GPIO.input(self.pin) == GPIO.LOW:
            reading += 1
        print reading

    def create_listener(self, event, callback):
        GPIO.add_event_detect(self.pin, event, callback=callback)

    def send_signal(self, signal):
        if "OUT" not in self.mode:
            raise NameError("Mode is not OUT")
        GPIO.output(self.pin, signal)

    def get_input(self):
        return GPIO.input(self.pin)

    def turn_servo(self, rotation):
        if "SERVO" not in self.mode:
            raise NameError("Mode is not SERVO0")
        self.pwm.ChangeDutyCycle(float(self.servo_pos) / 10.0 + 2.5)
        self.servo_pos = rotation

    def __del__(self):
        GPIO.cleanup()


sensor_pins = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13]
water_sensors = []
counter = 0
door_one = GPIOHelper('servo 1', 21, 'SERVO')


door_two = GPIOHelper('servo 2', 12, 'SERVO')


def update_water(channel):
    global water_sensors
    for pin in water_sensors:
        if pin.pin == channel:
            value = int(pin.name)
            if value >= 80 and door_one.servo_pos == 360:
                door_one.turn_servo(0)
                door_two.turn_servo(0)
            elif value < 80 and door_one.servo_pos == 0:
                door_one.turn_servo(360)
                door_two.turn_servo(360)
            print "updating with value {}".format(value)
            requests.post('http://10.0.0.22:5000/sensor/update', data={'value': value})

for pin in sensor_pins:
    counter += 10
    water_sensors.append(GPIOHelper('{}'.format(counter), pin, 'IN'))
for pin in water_sensors:
    pin.create_listener(GPIO.RISING, update_water)

while True:
    pass

"""direction = 0
while True:
    if value >= 100:
        direction = 1
    elif value <= 0:
        direction = 0
    if direction == 1:
        update_sensor('')
    elif direction == 0:
        update_sensor('rise')
    time.sleep(1)
EXAMPLE USAGE

def open_door_and_light_led(channel, led):
    if led.get_input():
        led.send_signal(GPIO.LOW)
        servo.turn_servo(90)
    else:
        servo.turn_servo(0)
        led.send_signal(GPIO.HIGH)

button = GPIOHelper('button', 16, 'IN')
led = GPIOHelper('led', 21, 'OUT')
servo = GPIOHelper('door1', 16, 'SERVO')

button.create_listener(GPIO.RISING, lambda channel: open_door_and_light_led(channel, led))
"""
