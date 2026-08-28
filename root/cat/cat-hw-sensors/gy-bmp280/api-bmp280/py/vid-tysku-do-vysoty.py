p0_ref = 1013.25    # опорний тиск «нуля висоти»

# Викликати на землі перед злетом: зробити поточне місце нульовою висотою.
def bmp280_set_zero_here():
    global p0_ref
    p0_ref = bmp280_pressure_hpa()   # «тут і зараз» = 0 метрів

# Висота ВІДНОСНО запам'ятованого нуля (надійна, не залежить від погоди).
def bmp280_relative_altitude():
    return bmp280_altitude(bmp280_pressure_hpa(), p0_ref)
