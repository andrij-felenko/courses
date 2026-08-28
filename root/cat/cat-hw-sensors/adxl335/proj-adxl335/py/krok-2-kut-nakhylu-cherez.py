import math
import time

# Кути нахилу (градуси) з трьох прискорень у g.
def tilt_angles(ax, ay, az):
    pitch = math.degrees(math.atan2(ax, math.hypot(ay, az)))
    roll  = math.degrees(math.atan2(ay, math.hypot(ax, az)))
    return pitch, roll

while True:
    ax = read_g(0, 0)
    ay = read_g(1, 1)
    az = read_g(2, 2)

    pitch, roll = tilt_angles(ax, ay, az)

    print("pitch={:.1f}  roll={:.1f}".format(pitch, roll))
    time.sleep(0.05)
