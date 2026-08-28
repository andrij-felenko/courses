class Airspeed:
    def __init__(self, offset=0.0, q_min=15.0):
        self.offset = offset      # нуль-зсув (Па)
        self.lp = Ema()           # ФНЧ на знаковому Δp
        self.q_min = q_min        # поріг зони нечутливості (Па)
        self.valid = False
        self.eas = self.tas = 0.0

    def update(self, dp_raw, p_static, T_kelvin, dt):
        dp = dp_raw - self.offset                       # 1. зняти зсув
        dp = self.lp.update(dp, dt / (0.05 + dt))       # 2. ФНЧ на знаковому Δp
        if dp < self.q_min:                             # 3. зона нечутливості
            self.valid = False
            self.eas = self.tas = 0.0
            return
        self.valid = True
        rho = air_density(p_static, T_kelvin)           # 4. реальна густина
        self.eas = (2.0 * dp / RHO_SSL) ** 0.5          # 5a. приладова
        self.tas = (2.0 * dp / rho) ** 0.5              # 5b. справжня
        if self.tas > 80.0:                             # 6. стислива поправка
            self.tas = tas_compressible(dp, p_static, T_kelvin)
