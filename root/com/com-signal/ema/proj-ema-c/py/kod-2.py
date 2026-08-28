EMA_Q = 8                            # стільки дробових біт тримає acc

class EmaFx:
    def __init__(self, a_num):       # напр. a_num=26 ≈ α 0.1
        self.a_num = a_num           # α = a_num / 256
        self.acc = None              # оцінка у форматі з фіксованою комою (<<Q)

    def step(self, x):
        if self.acc is None:
            self.acc = x << EMA_Q                    # старт першим відліком
        else:
            err = (x << EMA_Q) - self.acc            # різниця у тому ж масштабі
            self.acc += (self.a_num * err) >> 8      # + α·(x − y), знаменник 256
        return self.acc >> EMA_Q                     # назовні — звичайне число
