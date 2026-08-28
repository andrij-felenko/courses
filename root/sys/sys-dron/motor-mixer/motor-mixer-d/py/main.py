def mix_quad_x(throttle, roll, pitch, yaw):
    """вхід: throttle 0..1 (спільна тяга), roll/pitch/yaw — моменти (можуть бути ±)
    вихід: список m[0..3] у діапазоні 0..1, далі — на ESC"""

    # 1) сирий розклад за матрицею мікшера квадро-X
    m = [
        throttle + roll + pitch + yaw,   # передній правий, CW
        throttle + roll - pitch - yaw,   # задній правий,  CCW
        throttle - roll + pitch - yaw,   # передній лівий, CCW
        throttle - roll - pitch + yaw,   # задній лівий,   CW
    ]

    # 2) знайти найбільше й найменше серед чотирьох
    lo, hi = min(m), max(m)

    # 3) нормування зсувом УСІХ команд (зберігаємо різниці = моменти)
    if hi > 1.0:            # хтось пробив стелю — опустити пакет
        over = hi - 1.0
        m = [x - over for x in m]
    elif lo < 0.0:          # хтось пірнув під нуль — підняти пакет
        under = -lo
        m = [x + under for x in m]

    # 4) запобіжник на крайній випадок (моменти такі великі,
    #    що навіть після зсуву не влізають у коридор 0..1)
    return [min(1.0, max(0.0, x)) for x in m]
