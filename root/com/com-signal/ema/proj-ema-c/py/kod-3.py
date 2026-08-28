EMA_SHIFT = 3                        # α = 1/2^SHIFT (SHIFT=3 → α = 1/8)
EMA_Q     = 8                        # стільки дробових біт тримає acc

class EmaPow2:
    def __init__(self):
        self.acc = None              # оцінка у форматі з фіксованою комою (<<Q)

    def step(self, x):
        if self.acc is None:
            self.acc = x << EMA_Q                    # старт першим відліком
        else:
            err = (x << EMA_Q) - self.acc            # різниця у тому ж масштабі
            self.acc += err >> EMA_SHIFT             # α·(x − y) — самий зсув, без множення
        return self.acc >> EMA_Q                     # назовні — звичайне число
