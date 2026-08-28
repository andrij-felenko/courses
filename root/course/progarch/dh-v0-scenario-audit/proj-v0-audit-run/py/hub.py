# hub.py — v0, як він є
import time

THRESHOLD = 20.0                 # поріг зашитий у код

def read_sensor():               # драйвер конкретного давача → °C (локальний, без мережі)
    with open("/dev/therm0") as f:
        return float(f.read())

def heater_on():                 # драйвер конкретної розетки
    with open("/dev/relay0", "w") as f:
        f.write("1")

def heater_off():
    with open("/dev/relay0", "w") as f:
        f.write("0")

while True:
    t = read_sensor()
    if t < THRESHOLD:
        heater_on()
    else:
        heater_off()
    time.sleep(30)
