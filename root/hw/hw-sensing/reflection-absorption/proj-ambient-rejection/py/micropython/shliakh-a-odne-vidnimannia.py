from machine import Pin, ADC
import time

LED_PIN    = 25          # ІЧ-світлодіод через струмообмежувальний резистор
SENSOR_PIN = 34          # фотоприймач на вхід АЦП
SETTLE_US  = 200         # пауза на встановлення світлодіода й приймача, мкс

led = Pin(LED_PIN, Pin.OUT)
adc = ADC(Pin(SENSOR_PIN))
adc.atten(ADC.ATTN_11DB)     # вхід ~0..3.3 В
adc.width(ADC.WIDTH_12BIT)   # 0..4095
led.value(0)

# Повертає очищений від тла відбиток (коди АЦП; може бути від'ємним за шуму).
def read_reflection():
    led.value(0)                     # 1) тло без власного світла
    time.sleep_us(SETTLE_US)
    dark = adc.read()

    led.value(1)                     # 2) тло + відбиток
    time.sleep_us(SETTLE_US)
    lit = adc.read()

    led.value(0)                     # лишаємо світлодіод вимкненим
    return lit - dark                # тло скорочується

while True:
    signal = read_reflection()
    obstacle = signal > 120          # поріг — за калібруванням, див. нижче
    print("відбиток={}  перешкода={}".format(signal, int(obstacle)))
    time.sleep_ms(20)
