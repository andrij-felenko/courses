from machine import ADC, Pin
import time

SENSOR_PIN = 34
ADC_VREF   = 3.3
ADC_MAX    = 4095

adc = ADC(Pin(SENSOR_PIN))
adc.width(ADC.WIDTH_12BIT)   # 0..4095
adc.atten(ADC.ATTN_11DB)     # вхід ~0..3.3 В

def read_sensor_volts(n=16):
    acc = 0
    for _ in range(n):
        acc += adc.read()
    return (acc / n) * (ADC_VREF / ADC_MAX)

while True:
    v = read_sensor_volts()
    d = voltage_to_distance(v)
    print("U=%.3f В  d=%.1f см" % (v, d))
    time.sleep_ms(50)
