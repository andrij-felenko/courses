from machine import Pin, ADC
import time

power = Pin(7, Pin.OUT)          # цифрова ніжка живить давач (+ HW-038)
power.value(0)                   # за замовчуванням давач знеструмлений
signal = ADC(Pin(26))            # аналоговий вхід ← S (OUT) давача

def read_water_level():
    power.value(1)               # подали живлення на гребінку
    time.sleep_ms(10)            # ~10 мс, щоб сигнал усталився
    value = signal.read_u16()    # 0..65535 на 16-бітному АЦП
    power.value(0)               # одразу знеструмили — менше корозії
    return value

while True:
    level = read_water_level()

    # Пороги ПІД СВОЮ воду — визнач їх дослідом, не бери чужі!
    if level < 3200:             # ~50/1023 у масштабі 0..65535
        print("сухо")
    elif level < 25600:          # ~400/1023 у масштабі 0..65535
        print("трохи води")
    else:
        print("багато води")

    time.sleep(1)                # раз на секунду досить; давач і так не живимо постійно
