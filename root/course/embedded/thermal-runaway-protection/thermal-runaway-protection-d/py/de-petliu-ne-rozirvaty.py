# Тепловий захист комірки: спрацьовує за абсолютним рівнем АБО за крутизною.
# t_c10 — температура найгарячішої комірки в десятих градуса (372 = 37.2 °C),
# dt_ms — період між викликами в мілісекундах. Ціла арифметика, без float.

T_TRIP_C10 = 600    # 60.0 °C — абсолютна аварія
RATE_TRIP  = 20     # 2.0 °C/с — крута втеча (десятих °C за секунду)

class ThermalGuard:
    def __init__(self):
        self._prev = None            # попередній замір

    def fault(self, t_c10: int, dt_ms: int) -> bool:
        fault = False

        if t_c10 >= T_TRIP_C10:
            fault = True             # рубіж за рівнем
        if self._prev is not None and dt_ms > 0:
            # швидкість у десятих °C за секунду: (Δ десятих) * 1000 // Δмс
            rate = (t_c10 - self._prev) * 1000 // dt_ms
            if rate >= RATE_TRIP:
                fault = True         # рубіж за швидкістю — ловить раніше

        self._prev = t_c10
        return fault
