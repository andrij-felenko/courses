HEAL_LIMIT = 5    # стільки ДОБРИХ ударів підряд, щоб визнати одужання
                  # (свідомо БІЛЬШЕ за MISS_LIMIT: падати легко, вставати важко)


class Hysteretic:
    def __init__(self, now_ms: int):
        self.base = NodeHealth(now_ms)   # звичайний монітор із MISS_LIMIT
        self.healthy_run = 0             # скільки добрих ударів підряд назбирано
        self.eligible = True             # чи вузол ЗНОВУ придатний бути в ротації
        self.eligible_since_ms = now_ms  # коли ЗНОВУ став придатним (для карантину)

    # Той самий тик, але з РІЗНИМИ порогами вниз і вгору.
    def tick(self, now_ms: int, beat: bool) -> None:
        if beat:
            self.base.on_beat(now_ms)
            if self.healthy_run < HEAL_LIMIT:
                self.healthy_run += 1
        self.base.tick(now_ms)

        if self.base.health is Health.DOWN:
            self.eligible = False        # впав — і придатність знімаємо одразу
            self.healthy_run = 0         # рахунок одужання починаємо з нуля
        elif not self.eligible and self.healthy_run >= HEAL_LIMIT:
            self.eligible = True             # придатний ЛИШЕ після стійкої серії
            self.eligible_since_ms = now_ms  # звідси відлічуємо карантин
