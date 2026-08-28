# Виявити «застряглий» вихід ОП (ознака перевороту/защіпки) і скинути вузол.
# Якщо АЦП довго стоїть у крайньому коді — фізичний сигнал так не поводиться.

ADC_MAX     = 4095   # 12-бітний АЦП
RAIL_GUARD  = 20     # «крайня» зона: ≤20 або ≥4075
STUCK_LIMIT = 50     # стільки поспіль вибірок у рейці = підозра

_stuck_count = 0

def power_cycle_analog() -> None:   # зняти/подати живлення аналогового вузла
    ...

def opamp_latched(adc: int) -> bool:
    global _stuck_count
    at_rail = adc <= RAIL_GUARD or adc >= ADC_MAX - RAIL_GUARD
    _stuck_count = _stuck_count + 1 if at_rail else 0

    if _stuck_count >= STUCK_LIMIT:
        power_cycle_analog()        # струсонути тракт — вибити защіпку
        _stuck_count = 0
        return True                 # повідомити верхньому рівню: був збій
    return False
