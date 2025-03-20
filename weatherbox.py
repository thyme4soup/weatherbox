import time
from gpiozero import LED, PWMLED
from weather_helper import get_weather_info
import random
import math


SKYBOX_R = PWMLED("GPIO16")
SKYBOX_G = PWMLED("GPIO20")
SKYBOX_B = PWMLED("GPIO21")

PUMP = LED("GPIO15")
MIST = LED("GPIO14")

# Mist cycle length in seconds
MIST_DUTY_PERIOD = 10

# Pump cycle length in seconds
PUMP_DUTY_PERIOD = 5

# Lightning expected period in seconds
LIGHTNING_EXPECTED_PERIOD = 10


def pump_cycle(weather_info):
    ms = time.time() * 1000
    duty_period_ms = PUMP_DUTY_PERIOD * 1000
    if ms % duty_period_ms < duty_period_ms * weather_info.rain_intensity:
        PUMP.on()
    else:
        PUMP.off()


def mist_cycle(weather_info):
    ms = time.time() * 1000
    duty_period_ms = MIST_DUTY_PERIOD * 1000
    if ms % duty_period_ms < duty_period_ms * weather_info.cloud_intensity:
        MIST.on()
    else:
        MIST.off()


last_skybox_ms = 0
lightning_state = False


def skybox_color(weather_info):
    global lightning_state
    global last_skybox_ms
    if weather_info.lightning:
        if not lightning_state:
            ms = time.time() * 1000
            window = ms - last_skybox_ms
            last_skybox_ms = ms
            # treat lightning as memorlyless distribution
            if random.random() > math.exp(-window / (LIGHTNING_EXPECTED_PERIOD * 1000)):
                print("Lightning!")
                lightning_state = True
            else:
                lightning_state = False
        else:
            # We'll use last_skybox_ms to store the progression of our strike
            # ToDo: make this a continuous function of time -> brightness (min some upside-down quadratics?)
            lightning_ms = time.time() * 1000 - last_skybox_ms
            if lightning_ms < 100:
                SKYBOX_R.value = 1
                SKYBOX_G.value = 1
                SKYBOX_B.value = 1
            elif lightning_ms < 200:
                SKYBOX_R.value = 0
                SKYBOX_G.value = 0
                SKYBOX_B.value = 0
            elif lightning_ms < 300:
                SKYBOX_R.value = 1
                SKYBOX_G.value = 1
                SKYBOX_B.value = 1
            else:
                lightning_state = False
                last_skybox_ms = time.time() * 1000

    SKYBOX_R.value = weather_info.skybox_color[0] / 255
    SKYBOX_G.value = weather_info.skybox_color[1] / 255
    SKYBOX_B.value = weather_info.skybox_color[2] / 255


if __name__ == "__main__":
    while True:
        weather_info = get_weather_info()
        weather_info.lightning = True
        # print(weather_info)
        pump_cycle(weather_info)
        mist_cycle(weather_info)
        skybox_color(weather_info)
        time.sleep(0.1)
