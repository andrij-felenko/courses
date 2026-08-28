# Термінація Li-ion за спадом струму у фазі сталої напруги.
CAP_MAH    = 2000            # ємність комірки, мА·год
I_TERM_MA  = CAP_MAH // 10   # поріг C/10 = 200 мА
V_CV_MV    = 4200            # стеля напруги фази CV
DEBOUNCE_N = 3               # скільки вимірів поспіль під порогом

_below_cnt = 0               # стан між викликами

def charge_done(vcell_mv, icharge_ma):
    """Повертає True, коли заряд треба зупинити."""
    global _below_cnt
    # Термінація за струмом чинна ЛИШЕ у фазі CV: напруга вже на стелі.
    if vcell_mv < V_CV_MV - 20:          # ще у фазі CC — рано
        return False
    if icharge_ma < I_TERM_MA:
        _below_cnt += 1
        if _below_cnt >= DEBOUNCE_N:     # стабільно нижче порога
            return True                  # → повна, вимикаємо
    else:
        _below_cnt = 0                   # струм підскочив — лічильник назад
    return False
