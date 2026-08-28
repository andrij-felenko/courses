NSTAGE = 6                 # щаблів «1.5 біта»
NBITS  = NSTAGE + 2        # повний код = 8 розрядів (6 щаблів + 2-бітний хвіст)
LAT    = NSTAGE - 1        # затримка вирівнювання, тактів (найглибша черга)

# Один щабель «1.5 біта»: пороги ±Vref/4, три цифри D∈{0,1,2}.
# Повертає (цифру, залишок), де залишок = 2·Vвх − (D−1)·Vref (той самий формат Q15).
def stage_15bit(vin_q15, offset_q15):
    VREF = 1 << 15                             # 1.0 у Q15
    t_lo = -(VREF >> 2) + offset_q15           # −Vref/4 (+ зсув компаратора)
    t_hi =  (VREF >> 2) + offset_q15           # +Vref/4
    d = 0 if vin_q15 < t_lo else 1 if vin_q15 < t_hi else 2
    vres_q15 = 2 * vin_q15 - (d - 1) * VREF     # −Vref, 0 або +Vref, тоді ×2
    return d, vres_q15
