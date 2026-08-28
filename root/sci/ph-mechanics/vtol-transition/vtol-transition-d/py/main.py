# стан переходу: викликається щотакту керування (напр. 400 Гц)
# airspeed_mps — повітряна швидкість із давача (не land speed!)
V_TRANS     = 15.0    # поріг, за яким крило надійно несе, м/с
SPINDOWN_MS = 5000    # за скільки прибрати газ висіння

def transition_fwd_update(self, airspeed_mps, now_ms):
    self.fwd_throttle = 1.0               # тягнучий гвинт — на розгін

    if airspeed_mps < V_TRANS:
        # ще в «дірі»: крило не несе всю вагу — тримаємо висіння повністю,
        # висотний контур сам додає газу вгору, скільки треба
        self.hover_throttle = self.hover_alt_hold()  # повне утримання висоти
        self.t_reached = 0                           # таймер спуску ще не пущено
    else:
        # швидкість надійно понад звалювання — крило перебрало вагу.
        # прибираємо газ висіння ПЛАВНО, не ривком, за SPINDOWN_MS
        if self.t_reached == 0:
            self.t_reached = now_ms
        k = (now_ms - self.t_reached) / SPINDOWN_MS  # 0 → 1
        if k > 1.0:
            k = 1.0
        self.hover_throttle = self.hover_alt_hold() * (1.0 - k)  # згасання
        if k >= 1.0:
            self.mode = MODE_FIXED_WING              # перехід завершено
