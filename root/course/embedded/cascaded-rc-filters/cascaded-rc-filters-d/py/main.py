# Одна цифрова RC-ланка нижніх частот (експоненційний згладжувач).
# alpha = dt / (RC + dt), 0 < alpha < 1; менше alpha — повільніше, сильніше згладжує.
class RcStage:
    def __init__(self, alpha):
        self.y = 0.0          # попередній вихід (стан ланки)
        self.alpha = alpha    # коефіцієнт згладжування

    def step(self, x):
        self.y += self.alpha * (x - self.y)   # y += α·(вхід − y)
        return self.y
