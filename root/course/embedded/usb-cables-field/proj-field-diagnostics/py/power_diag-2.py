# power_diag.py (продовження)

# --- Апаратні гачки: реалізуються під конкретну плату ---
# Один сирий відлік АЦП на дільнику VBUS, у мілівольтах ВЖЕ на вході.
def hw_adc_vbus_mv_raw() -> int:
    raise NotImplementedError   # плата підставляє свою реалізацію
# Оцінка струму заряду в мА: шунт+підсилювач АБО регістр зарядника.
def hw_charge_current_ma() -> int:
    raise NotImplementedError

# Усереднення VBUS: беремо 2^log2 сирих відліків і ДІЛИМО (просте середнє).
# Це давить випадковий шум АЦП у sqrt(N) разів — рівно те, що треба
# перед порівнянням із порогом, який теж у десятках мВ.
def vbus_averaged(log2n: int) -> int:
    n = 1 << log2n
    acc = sum(hw_adc_vbus_mv_raw() for _ in range(n))
    return acc >> log2n            # ділення на 2^log2n = зсув
