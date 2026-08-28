from machine import Pin, PWM

# ESP32: PWM на майже будь-якому GPIO; частота 1 кГц, 8-бітна шкала 0…255
r = PWM(Pin(25), freq=1000, duty_u16=0)
g = PWM(Pin(26), freq=1000, duty_u16=0)
b = PWM(Pin(27), freq=1000, duty_u16=0)

def set_color(cr, cg, cb):
    r.duty_u16(cr * 257)      # 0…255 → 0…65535 (257 = 65535/255)
    g.duty_u16(cg * 257)
    b.duty_u16(cb * 257)

set_color(255, 90, 0)         # помаранчевий
