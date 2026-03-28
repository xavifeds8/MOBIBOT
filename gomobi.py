import RPi.GPIO as GPIO
import time
import random

IN1, IN2, IN3, IN4 = 23, 24, 25, 8
TRIG, ECHO = 17, 27

GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance(timeout=0.02):
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start = time.time()

    while GPIO.input(ECHO) == 0:
        if time.time() - start > timeout:
            return None
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        if time.time() - start > timeout:
            return None
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    return round(duration * 17150, 2)

def forward():
    GPIO.output([IN1, IN3], 1)
    GPIO.output([IN2, IN4], 0)

def reverse():
    GPIO.output([IN1, IN3], 0)
    GPIO.output([IN2, IN4], 1)

def left():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)

def right():
    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)

def stop():
    GPIO.output([IN1, IN2, IN3, IN4], 0)

try:
    while True:
        dist = get_distance()

        if dist is None:
            print("Sensor timeout")
            stop()
            continue

        print(f"Distance: {dist} cm")

        if dist < 20:
            print("🚨 Obstacle!")

            stop()
            time.sleep(0.2)

            reverse()
            time.sleep(1)

            stop()
            time.sleep(0.2)

            if random.choice([True, False]):
                left()
                print("Turning Left")
            else:
                right()
                print("Turning Right")

            time.sleep(1)

        else:
            forward()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped")

finally:
    GPIO.cleanup()