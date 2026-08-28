from machine import I2C, Pin
from time import ticks_us, ticks_diff
from struct import unpack_from
from math import atan2, sqrt, pi

MPU = 0x68
ACCEL_XOUT = 0x3B

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

roll = 0.0
pitch = 0.0
gyro_bias_x = 0.0
gyro_bias_y = 0.0     # нуль гіроскопа (з калібрування)

ALPHA = 0.98          # вага гіроскопа у злитті

def read6():
    b = i2c.readfrom_mem(MPU, ACCEL_XOUT, 14)
    ax, ay, az = unpack_from(">hhh", b, 0)
    gx, gy, gz = unpack_from(">hhh", b, 8)
    return ax, ay, az, gx, gy, gz

calibrate_gyro()          # виміряти нуль гіроскопа (див. нижче)
t_prev = ticks_us()

while True:
    ax, ay, az, gx, gy, gz = read6()

    # Реальний крок часу в секундах (ticks_us() — мікросекунди).
    now = ticks_us()
    dt = ticks_diff(now, t_prev) * 1e-6
    t_prev = now

    # --- кут з акселерометра (абсолютний, шумний) ---
    axg, ayg, azg = ax / 16384.0, ay / 16384.0, az / 16384.0
    roll_acc  = atan2(ayg, azg) * 180.0 / pi
    pitch_acc = atan2(-axg, sqrt(ayg*ayg + azg*azg)) * 180.0 / pi

    # --- кутова швидкість з гіроскопа, з відрахованим нулем (°/s) ---
    rate_x = (gx - gyro_bias_x) / 131.0
    rate_y = (gy - gyro_bias_y) / 131.0

    # --- комплементарне злиття ---
    roll  = ALPHA * (roll  + rate_x * dt) + (1.0 - ALPHA) * roll_acc
    pitch = ALPHA * (pitch + rate_y * dt) + (1.0 - ALPHA) * pitch_acc

    print("roll", round(roll, 1), " pitch", round(pitch, 1))
    # БЕЗ sleep: точність фільтра залежить від частого, рівного циклу.
