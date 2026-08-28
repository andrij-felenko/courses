# --- Перерахунок тиску (Па) у глибину (м) з обнуленням на поверхні ---
class DepthSensor:
    def __init__(self, rho, g, ema_alpha):
        self.rho_g = rho * g          # напр. 1025·9.81 для морської води
        self.p_surface = 101325.0     # доки не протаровано — стандартна атм.
        self.depth_f = 0.0            # згладжена глибина, м (стан EMA)
        self.ema_alpha = ema_alpha    # коеф. згладжування 0<α≤1 (1 = без фільтра)
        self.tared = False            # чи вже обнулено на поверхні

    def tare(self, p_abs):
        """Викликати РАЗ, поки апарат ще на поверхні й нерухомий."""
        self.p_surface = p_abs        # цей тиск = «нуль глибини»
        self.depth_f = 0.0
        self.tared = True

    def depth_from_pressure(self, p_abs):
        """Сирий абсолютний тиск (Па) → згладжена глибина (м, вниз додатна)."""
        depth_raw = (p_abs - self.p_surface) / self.rho_g   # h = (P−P₀)/(ρg)
        # EMA: тягне збережену глибину до свіжого виміру на частку α
        self.depth_f += (depth_raw - self.depth_f) * self.ema_alpha
        return self.depth_f
