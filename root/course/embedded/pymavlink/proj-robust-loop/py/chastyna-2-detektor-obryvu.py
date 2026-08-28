LINK_TIMEOUT_S = 3.0     # тиша довша за це = лінію втрачено (≈3 пропущені heartbeat)


class LinkState:
    """Усе, що ми знаємо про лінію й апарат. Одне місце — одна правда."""
    def __init__(self):
        self.last_heartbeat = None   # None = heartbeat ще НЕ приходив жодного разу
        self.armed = False           # презумпція: роззброєно, поки не почули інше
        self.alt_m = 0.0
        self.lat = self.lon = 0.0
        self.batt_v = 0.0

    def link_alive(self):
        """True лише якщо heartbeat приходив І не замовк довше за поріг."""
        if self.last_heartbeat is None:
            return False             # ще жодного heartbeat — лінія НЕ жива
        return (time.time() - self.last_heartbeat) < LINK_TIMEOUT_S
