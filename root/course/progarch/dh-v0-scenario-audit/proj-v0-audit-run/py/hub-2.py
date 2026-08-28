# hub.py — той самий v0, лише крок відділено від вічного циклу
import time

THRESHOLD = 20.0

def read_sensor():
    with open("/dev/therm0") as f:
        return float(f.read())

def heater_on():
    with open("/dev/relay0", "w") as f:
        f.write("1")

def heater_off():
    with open("/dev/relay0", "w") as f:
        f.write("0")

def step():                      # рівно одна ітерація старого циклу
    t = read_sensor()
    if t < THRESHOLD:
        heater_on()
    else:
        heater_off()

def run():                       # те, що було while True
    while True:
        step()
        time.sleep(30)

if __name__ == "__main__":
    run()
