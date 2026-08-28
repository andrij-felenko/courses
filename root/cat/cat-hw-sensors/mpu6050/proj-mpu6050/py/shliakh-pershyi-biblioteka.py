from machine import I2C, Pin
from time import sleep_ms
from struct import unpack_from

MPU = 0x68          # адреса за замовчуванням (AD0 на землі)
PWR_MGMT_1 = 0x6B
WHO_AM_I   = 0x75
ACCEL_XOUT = 0x3B   # звідси йдуть 14 байтів: 6 акс + 2 темп + 6 гіро

i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # ніжки — під свою плату

def setup():
    i2c.writeto_mem(MPU, PWR_MGMT_1, b'\x00')   # розбудити (зняти біт SLEEP)
    sleep_ms(100)
    # Перше, що робимо ЗАВЖДИ — питаємо, чи це взагалі наш чип.
    if i2c.readfrom_mem(MPU, WHO_AM_I, 1)[0] == 0x68:
        print("MPU-6050 на місці")
    else:
        raise RuntimeError("MPU-6050 НЕ відповідає — перевір пайку/адресу/клон")

def loop():
    # Одне читання забирає всі шість осей одним пакетом по I2C.
    b = i2c.readfrom_mem(MPU, ACCEL_XOUT, 14)
    # >hhh h hhh — big-endian int16: ax,ay,az, temp, gx,gy,gz
    ax, ay, az = unpack_from(">hhh", b, 0)
    gx, gy, gz = unpack_from(">hhh", b, 8)

    acc_x = ax / 16384.0    # g   (при діапазоні ±2g)
    gyr_x = gx / 131.0      # °/s (при діапазоні ±250°/s)
    print(acc_x, gyr_x)
    sleep_ms(20)

setup()
while True:
    loop()
