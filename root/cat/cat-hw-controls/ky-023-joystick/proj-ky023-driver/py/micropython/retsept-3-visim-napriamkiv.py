# Напрямки як прості константи (IntEnum на MicroPython зайвий).
DIR_NONE, DIR_N, DIR_NE, DIR_E, DIR_SE = 0, 1, 2, 3, 4
DIR_S, DIR_SW, DIR_W, DIR_NW = 5, 6, 7, 8

# Звести вісь до знака −1/0/+1 за порогом (частка від повного ходу).
def sign3(v, threshold=40):
    if v >  threshold: return  1
    if v < -threshold: return -1
    return 0

def read_dir():
    hx = sign3(read_axis(horizontal))       # −1, 0, +1  (захід … схід)
    hy = sign3(read_axis(vertical))         # −1, 0, +1  (південь … північ)

    if hx == 0 and hy == 0:
        return DIR_NONE

    # 3×3 → напрямок; вважаємо +Y = північ (вгору), +X = схід (вправо)
    if hy ==  1:
        return DIR_NW if hx == -1 else DIR_NE if hx == 1 else DIR_N
    if hy == -1:
        return DIR_SW if hx == -1 else DIR_SE if hx == 1 else DIR_S
    return DIR_W if hx == -1 else DIR_E     # hy == 0, hx ≠ 0
