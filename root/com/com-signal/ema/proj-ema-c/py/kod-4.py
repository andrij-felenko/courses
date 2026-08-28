class Dema:
    def __init__(self, alpha, beta):
        self.alpha = alpha        # α — для рівня
        self.beta = beta          # β — для тренду
        self.level = None         # оцінка рівня
        self.trend = 0.0          # оцінка тренду

    def step(self, x):
        if self.level is None:
            self.level = x
            self.trend = 0.0
            return self.level
        prev = self.level
        self.level += self.alpha * (x - self.level) + self.trend      # рівень + хід тренду
        self.trend += self.beta * ((self.level - prev) - self.trend)  # оновлюємо сам тренд
        return self.level
