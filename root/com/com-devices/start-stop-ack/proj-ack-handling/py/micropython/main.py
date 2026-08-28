# MicroPython: machine.I2C ховає дев'ятий такт усередині й піднімає OSError на NACK.
# Драйвер розрізняє гілки за ФАЗОЮ обміну — запис адреси/регістра окремо від читання.
import time
from machine import I2C, Pin

I2C_OK        = 0   # усе підтверджено
I2C_NACK_ADDR = 1   # на адресу ніхто не озвався → пристрою нема
I2C_NACK_DATA = 2   # ведений не прийняв байт даних (зайнятий/збій)
I2C_BUS_TIMEOUT = 3 # лінія завмерла → шина зависла

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100_000)

def _bus_free():                       # SDA і SCL відпущені (обидві високі)?
    return Pin(21, Pin.IN).value() and Pin(22, Pin.IN).value()

# одна спроба: прочитати один байт із регістра reg давача addr7
def i2c_read_reg_once(addr7, reg):
    t0 = time.ticks_us()               # шина вільна впродовж 1 мс?
    while not _bus_free():
        if time.ticks_diff(time.ticks_us(), t0) > 1000:
            return I2C_BUS_TIMEOUT, None   # ні — хтось тримає лінію

    # -- фаза запису: адреса + номер регістра (START, addr+W, reg) --
    try:
        # scan() пінгує саму адресу: є в списку → ведений озвався на addr+W
        if addr7 not in i2c.scan():
            return I2C_NACK_ADDR, None     # ніхто не озвався → пристрою нема
        i2c.writeto(addr7, bytes([reg]), stop=False)  # номер регістра БЕЗ STOP: далі йтиме Sr, а не новий СТАРТ; NACK → OSError
    except OSError:
        return I2C_NACK_DATA, None         # ведений зайнятий/збій → варто повторити

    # -- повторний СТАРТ, фаза читання (Sr, addr+R, байт, NACK+STOP) --
    try:
        data = i2c.readfrom(addr7, 1)      # драйвер сам дає NACK на останній байт
    except OSError:
        return I2C_NACK_ADDR, None
    return I2C_OK, data[0]

# обгортка з повтором: тимчасові збої — повторюємо, сталі — ні
def i2c_read_reg(addr7, reg):
    st, out = I2C_OK, None
    for _ in range(3):
        st, out = i2c_read_reg_once(addr7, reg)
        if st == I2C_OK or st == I2C_NACK_ADDR:
            return st, out             # успіх або «пристрою нема» — повтор не поможе
        time.sleep_us(200)             # NACK на даних / таймаут — даємо отямитися
    return st, out                     # вичерпали спроби — повертаємо останню причину
