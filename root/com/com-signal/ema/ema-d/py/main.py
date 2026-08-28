class Ema:
    def __init__(self, alpha):
        self.alpha = alpha    # коефіцієнт згладжування, 0..1
        self.y = None         # y задамо першим же відліком, не нулем

    def step(self, x):
        if self.y is None:            # старт біля істини, а не від нуля
            self.y = x
        else:
            self.y += self.alpha * (x - self.y)   # одне множення, одне додавання
        return self.y
