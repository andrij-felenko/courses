# Монітор слухає удари від вузла. Три пропущені підряд = вузол мертвий.
# Тактика купує ВИЯВЛЕННЯ (дізнаємось про смерть за ~1.5 с, а не від
# розлюченого користувача), але платить ТРАФІКОМ і РИЗИКОМ хибної тривоги.
BEAT_PERIOD_MS = 500   # як часто вузол має битися
MISS_LIMIT     = 3     # скільки пропусків терпимо до вироку


class Monitor:
    def __init__(self):
        self.last_beat_ms = 0     # коли прийшов останній удар
        self.missed = 0           # скільки періодів поспіль тиша
        self.alive = True         # наш поточний присуд про вузол


# Викликається раз на BEAT_PERIOD_MS з таймера монітора.
def monitor_tick(m, now_ms):
    if now_ms - m.last_beat_ms < BEAT_PERIOD_MS:
        return                    # удар устиг — усе гаразд

    m.missed += 1                 # період минув, а удару не було
    if m.missed >= MISS_LIMIT and m.alive:
        m.alive = False           # вирок: вузол мертвий
        on_node_down()            # штовхаємо родину оговтання


# Викликається, коли фізично прийшов удар від вузла.
def monitor_on_beat(m, now_ms):
    m.last_beat_ms = now_ms
    m.missed = 0                  # тиша скинута — вузол живий
    m.alive = True
