from machine import ADC, Pin
import time

ao = ADC(Pin(0))                   # аналоговий вхід AO

while True:
    raw = ao.read_u16()            # 0..65535
    v = raw >> 6                   # зводимо до 0..1023; менше = мокріше
    line = "AO = {}".format(v)

    if v > 800:
        line += "  сухо"
    elif v > 400:
        line += "  волого"
    else:
        line += "  залито"

    print(line)
    time.sleep_ms(300)
