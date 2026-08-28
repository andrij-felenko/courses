from machine import ADC, Pin

# 12-бітний АЦП ESP32; read_u16() масштабує результат до 0…65535
ADC_MAX = 65535
pot = ADC(Pin(POT_PIN))
pot.atten(ADC.ATTN_11DB)          # повний діапазон входу ~0…3.3 В

# очікуваний код АЦП для середини шкали без навантаження
expected = ADC_MAX // 2           # = 32767
measured = pot.read_u16()

# велике розходження = повзунок навантажений, треба буфер
if abs(measured - expected) > 3200:
    pass                          # ставимо ОП-повторювач або беремо пот меншого опору
