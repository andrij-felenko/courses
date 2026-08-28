class RateLimiter:
    """Пропускає дію не частіше, ніж раз на period секунд."""
    def __init__(self, hz):
        self.period = 1.0 / hz
        self.last = 0.0

    def ready(self):
        now = time.time()
        if now - self.last >= self.period:
            self.last = now
            return True
        return False


# приклад: слати навігаційну уставку не частіше 5 разів на секунду
setpoint_rate = RateLimiter(hz=5)

def maybe_send_setpoint(m, state):
    if not state.link_alive():
        return                       # мертва лінія — не шлемо нічого
    if not setpoint_rate.ready():
        return                       # ще рано — цей такт пропускаємо
    # …тут пакуємо й шлемо навігаційну команду рівно 5 разів на секунду…
