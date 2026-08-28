# DC-blocker: y[n] = x[n] − x[n−1] + α·y[n−1].
# α близьке до 1 (тут 0.995) — зрізає лише найповільніший зсув, звук лишає.
# Стан у цілому з фіксованою комою — така сама арифметика, як на контролері.
class DcBlock:
    def __init__(self):
        self.x_prev = 0
        self.y_prev = 0

def dcblock(s, x):
    # α = 0.995 у форматі Q15: 0.995 · 32768 ≈ 32604
    y = x - s.x_prev + ((32604 * s.y_prev) >> 15)
    s.x_prev = x
    s.y_prev = y
    return y
