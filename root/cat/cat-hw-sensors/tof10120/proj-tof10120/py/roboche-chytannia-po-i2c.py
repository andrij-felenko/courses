from machine import I2C, Pin
from time import sleep_ms

TOF_ADDR = 0x52     # 7-бітна адреса (байт 0xA4 → 0x52)
REG_RAW  = 0x00     # миттєва (сира) відстань, 2 байти MSB-first
REG_FILT = 0x04     # згладжена відстань, 2 байти MSB-first

i2c = I2C(0, scl=Pin(22), sda=Pin(21))     # ніжки — під свою плату

# Повертає відстань у мм (0..~1993) або -1, якщо модуль не відповів як слід.
def tof_read_reg(reg):
    try:
        # readfrom_mem сам робить repeated-start: пише регістр і зразу читає 2 байти
        b = i2c.readfrom_mem(TOF_ADDR, reg, 2)
    except OSError:
        return -1                          # ніхто не підтвердив адресу → нема модуля
    return (b[0] << 8) | b[1]              # старший, молодший → 16-бітне число, мм

sleep_ms(10)
while True:
    mm = tof_read_reg(REG_FILT)            # згладжена; для сирої — REG_RAW
    if mm < 0:
        print("TOF: нема відповіді")
    elif mm == 0:
        print("TOF: 0 (ціль надто близько / поза діапазоном?)")
    else:
        print(mm, "мм")
    sleep_ms(100)
