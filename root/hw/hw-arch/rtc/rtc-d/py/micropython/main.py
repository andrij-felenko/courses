from machine import Pin, I2C
import time

DS3231_ADDR = 0x68
i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # свої ноги шини

def dec_to_bcd(v):  return (v // 10) << 4 | (v % 10)   # число → BCD
def bcd_to_dec(b):  return (b >> 4) * 10 + (b & 0x0F)  # BCD → число

# виставити час один раз: 2026-06-11, 14:30:00, середа (день тижня 1..7)
def set_time():
    payload = bytes(dec_to_bcd(x) for x in (0, 30, 14, 4, 11, 6, 26))
    #                                   сек хв год дт  чис міс рік
    i2c.writeto_mem(DS3231_ADDR, 0x00, payload)  # запис від регістра 0x00

# set_time()   # розкоментувати ОДИН раз, щоб завести годинник

while True:
    # прочитати 7 байтів від регістра 0x00 (авто-інкремент усередині)
    d = i2c.readfrom_mem(DS3231_ADDR, 0x00, 7)
    ss  = bcd_to_dec(d[0] & 0x7F)   # лишаємо 7 бітів цифр секунд
    mm  = bcd_to_dec(d[1])
    hh  = bcd_to_dec(d[2] & 0x3F)   # 24-год. режим: біти 6..0
    # d[3] — день тижня, пропускаємо
    day = bcd_to_dec(d[4])
    mon = bcd_to_dec(d[5])
    yr  = bcd_to_dec(d[6])

    print("20%02u-%02u-%02u %02u:%02u:%02u" % (yr, mon, day, hh, mm, ss))
    time.sleep(1)
