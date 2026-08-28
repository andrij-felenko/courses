from machine import I2C, Pin

MUX_ADDR = 0x70                # власна 7-бітна адреса мультиплексора

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Увімкнути рівно одну гілку (0…7), решту вимкнути.
def mux_select(channel):
    if channel > 7:
        return
    i2c.writeto(MUX_ADDR, bytes([1 << channel]))  # один біт = одна гілка

def read_sensor_on(channel):
    mux_select(channel)        # крок 1: вибрати гілку
    # крок 2: далі — звичайна робота з давачем 0x68 на ЦІЙ гілці
    #         напр., адреса регістра даних 0x3B, забрати 6 байт
    data = i2c.readfrom_mem(0x68, 0x3B, 6)  # запис регістра + повторний старт
    # ... використати data ...
