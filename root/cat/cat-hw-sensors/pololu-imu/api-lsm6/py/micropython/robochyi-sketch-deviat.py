from machine import I2C, Pin
import struct, time

IMU = 0x6B                      # LSM6DS33: акселерометр + гіроскоп
MAG = 0x1E                      # LIS3MDL:  магнетометр — інший чип, інша адреса

i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # одна шина на обидва чипи

def imu_init():
    return IMU in i2c.scan() and i2c.readfrom_mem(IMU, 0x0F, 1)[0] == 0x69
def imu_enable():               # аксель (±2 g) + гіро (±245 °/с)
    i2c.writeto_mem(IMU, 0x10, b'\x80')
    i2c.writeto_mem(IMU, 0x11, b'\x80')
def imu_read():                 # (gx,gy,gz, ax,ay,az) — рух
    return struct.unpack('<6h', i2c.readfrom_mem(IMU, 0x22 | 0x80, 12))

def mag_init():
    return MAG in i2c.scan() and i2c.readfrom_mem(MAG, 0x0F, 1)[0] == 0x3D
def mag_enable():               # магнетометр: висока якість, 10 Гц, ±4 гауси
    i2c.writeto_mem(MAG, 0x20, b'\x70')
    i2c.writeto_mem(MAG, 0x21, b'\x00')
    i2c.writeto_mem(MAG, 0x22, b'\x00')
    i2c.writeto_mem(MAG, 0x23, b'\x0C')
def mag_read():                 # (mx,my,mz) — поле
    return struct.unpack('<3h', i2c.readfrom_mem(MAG, 0x28 | 0x80, 6))

if not imu_init():
    raise SystemExit("LSM6DS33 не знайдено")
imu_enable()

if not mag_init():
    raise SystemExit("LIS3MDL не знайдено")
mag_enable()

while True:
    gx, gy, gz, ax, ay, az = imu_read()   # a.* та g.* — рух
    mx, my, mz = mag_read()               # m.*        — поле
    print("A:{:6d} {:6d} {:6d}  G:{:6d} {:6d} {:6d}  M:{:6d} {:6d} {:6d}".format(
          ax, ay, az, gx, gy, gz, mx, my, mz))
    time.sleep_ms(100)
