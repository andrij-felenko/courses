from machine import I2C, Pin
import struct, time

ADDR = 0x6B                     # адреса LSM6DS33 (0x6A, якщо SA0 до землі)
WHO_AM_I, CTRL1_XL, CTRL2_G, OUTX_L_G = 0x0F, 0x10, 0x11, 0x22

i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # підніми свою шину зі своїми ніжками

def init():                     # знайти чип; False = його на шині немає
    return ADDR in i2c.scan() and i2c.readfrom_mem(ADDR, WHO_AM_I, 1)[0] == 0x69

def enable_default():           # акселерометр (±2 g) і гіроскоп (±245 °/с)
    i2c.writeto_mem(ADDR, CTRL1_XL, b'\x80')   # 1.66 кГц, ±2 g
    i2c.writeto_mem(ADDR, CTRL2_G,  b'\x80')   # 1.66 кГц, ±245 °/с

def read():                     # свіжі виміри обох давачів; вертає (g, a) як int16
    raw = i2c.readfrom_mem(ADDR, OUTX_L_G | 0x80, 12)  # гіро + аксель, 6 int16 LE
    return struct.unpack('<6h', raw)           # gx,gy,gz, ax,ay,az

if not init():                  # знайти чип; False = його на шині немає
    raise SystemExit("LSM6DS33 не знайдено — перевір дроти, живлення, підтяжки")
enable_default()                # увімкнути акселерометр і гіроскоп

while True:
    gx, gy, gz, ax, ay, az = read()  # оновити відліки руху
    # {:6d} — шестизнакове поле, щоб стовпчики не «стрибали»
    print("A: {:6d} {:6d} {:6d}   G: {:6d} {:6d} {:6d}".format(ax, ay, az, gx, gy, gz))
    time.sleep_ms(100)          # 10 разів на секунду — вистачить, щоб дивитись очима
