from machine import I2C, Pin
import struct, time

IMU, MAG = 0x6B, 0x1E
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Чутливості для налаштувань за замовчуванням enable_default():
ACC_G     = 0.000061      # g на відлік        (±2 g)
GYRO_DPS  = 0.00875       # °/с на відлік      (±245 °/с)
MAG_GAUSS = 1.0 / 6842    # гаус на відлік     (±4 гауси)

def imu_read():
    return struct.unpack('<6h', i2c.readfrom_mem(IMU, 0x22 | 0x80, 12))
def mag_read():
    return struct.unpack('<3h', i2c.readfrom_mem(MAG, 0x28 | 0x80, 6))

if IMU not in i2c.scan() or MAG not in i2c.scan():
    raise SystemExit("давач не знайдено — перевір I2C")
i2c.writeto_mem(IMU, 0x10, b'\x80'); i2c.writeto_mem(IMU, 0x11, b'\x80')
i2c.writeto_mem(MAG, 0x20, b'\x70'); i2c.writeto_mem(MAG, 0x23, b'\x0C')

while True:
    gx, gy, gz, ax, ay, az = imu_read()
    mx, my, mz = mag_read()

    # сире (int16) → фізичне (float), кожну вісь на свою чутливість:
    ax, ay, az = ax * ACC_G,    ay * ACC_G,    az * ACC_G
    gx, gy, gz = gx * GYRO_DPS, gy * GYRO_DPS, gz * GYRO_DPS
    mx, my, mz = mx * MAG_GAUSS, my * MAG_GAUSS, mz * MAG_GAUSS

    print("a[g]: {:.2f} {:.2f} {:.2f}".format(ax, ay, az), end='')
    print("   g[dps]: {:.1f} {:.1f} {:.1f}".format(gx, gy, gz), end='')
    print("   m[Gs]: {:.3f} {:.3f} {:.3f}".format(mx, my, mz))

    time.sleep_ms(100)
