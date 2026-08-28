from machine import I2C, Pin
import struct
import time

ADDR = 0x68          # AD0 на землі
PWR_MGMT_1 = 0x6B
ACCEL_XOUT = 0x3B

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

def write_reg(reg, val):
    i2c.writeto_mem(ADDR, reg, bytes([val]))

# Розбудити: скинути біт SLEEP у PWR_MGMT_1 (0 = працювати).
# При старті чип спить — без цього рядка даних не буде.
write_reg(PWR_MGMT_1, 0x00)
time.sleep_ms(100)

while True:
    # Один пакет: 14 байтів поспіль від ACCEL_XOUT_H.
    # Драйвер сам робить repeated start між адресою регістра й читанням.
    raw = i2c.readfrom_mem(ADDR, ACCEL_XOUT, 14)

    # Кожна вісь — два байти, СТАРШИЙ приходить першим (big-endian).
    # struct '>' розбирає big-endian, 'h' — 16-бітне ціле зі знаком.
    ax, ay, az, t, gx, gy, gz = struct.unpack('>hhhhhhh', raw)

    # Сире число → фізична величина (діапазони за замовчуванням ±2g, ±250°/s)
    acc_x = ax / 16384.0          # g
    gyr_x = gx / 131.0            # °/s

    print(acc_x, gyr_x, sep='\t')
    time.sleep_ms(50)
