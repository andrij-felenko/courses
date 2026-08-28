import math

class SNCurve:
    """Крива втоми за законом Басквіна, задана двома точками (лог-лог пряма)."""
    def __init__(self, s1, n1, s2, n2, ult):
        self.s1, self.n1 = s1, n1
        self.k   = math.log(n2 / n1) / math.log(s1 / s2)   # нахил прямої
        self.ult = ult                                     # границя міцності σ_u

    def cycles_to_failure(self, amp):
        return self.n1 * (self.s1 / amp) ** self.k

    def goodman_equiv(self, amp, mean):
        """Звести цикл із розтяжним середнім до рівносильної амплітуди при R=−1."""
        if mean <= 0:                       # стискальне середнє — не караємо (консервативно)
            return amp
        return amp / (1.0 - mean / self.ult)   # пряма Ґудмана
