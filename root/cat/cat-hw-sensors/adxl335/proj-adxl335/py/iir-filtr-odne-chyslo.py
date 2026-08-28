# Однополюсний IIR (експоненційне згладжування), стан — одне float.
# Той самий код працює і на CPython, і на MicroPython.
class Iir:
    def __init__(self):
        self.y = 0.0
        self.init = False

    def step(self, x, alpha):
        if not self.init:            # перший вимір — як є, без розгону
            self.y = x
            self.init = True
        self.y += alpha * (x - self.y)
        return self.y
