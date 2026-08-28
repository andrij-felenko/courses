# hub.py — увесь «розумний дім» v0
THRESHOLD = 20.0                 # поріг зашитий у код

while True:
    t = read_sensor()            # один давач температури
    if t < THRESHOLD:
        heater_on()
    else:
        heater_off()
    sleep(30)
