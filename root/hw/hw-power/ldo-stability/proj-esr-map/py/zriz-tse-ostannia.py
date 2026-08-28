    def crossover(self, cout, esr, f_lo=1e-1, f_hi=1e10, steps=400):
        """Частота зрізу: ОСТАННІЙ перехід |L| через одиницю згори вниз."""
        lo, hi = math.log10(f_lo), math.log10(f_hi)
        prev_f, prev_above = f_lo, self.gain(f_lo, cout, esr) >= 1.0
        bracket = None
        for i in range(1, steps + 1):
            f = 10.0 ** (lo + (hi - lo) * i / steps)
            above = self.gain(f, cout, esr) >= 1.0
            if prev_above and not above:
                bracket = (prev_f, f)      # не виходимо: беремо останній
            prev_f, prev_above = f, above
        if bracket is None:
            return None
        a, b = bracket
        for _ in range(50):                # уточнення в лог-масштабі
            m = math.sqrt(a * b)
            if self.gain(m, cout, esr) >= 1.0:
                a = m
            else:
                b = m
        return math.sqrt(a * b)

    def margin(self, cout, esr):
        """(частота зрізу, запас фази в градусах)."""
        fc = self.crossover(cout, esr)
        if fc is None:
            return None, None
        return fc, 180.0 + self.phase(fc, cout, esr)
