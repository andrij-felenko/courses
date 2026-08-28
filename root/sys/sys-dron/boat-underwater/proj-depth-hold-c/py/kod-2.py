# --- Вертикальний контур утримання глибини ---
def clampf(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


class DepthPID:
    def __init__(self, kp, ki, kd, tau_d, i_min, i_max, u_min, u_max):
        # параметри регулятора
        self.kp, self.ki, self.kd = kp, ki, kd  # коеф. П, І, Д (для осі глибини)
        self.tau_d = tau_d          # стала фільтра похідної, с
        self.i_min, self.i_max = i_min, i_max   # межі інтеграла (антивіндап)
        self.u_min, self.u_max = u_min, u_max   # межі виходу = межі тяги, −1..+1
        # стан
        self.integral = 0.0         # накопичена тяга проти сталої плавучості
        self.depth_prev = 0.0       # глибина на попередньому такті
        self.deriv_f = 0.0          # згладжена вертикальна швидкість

    def reset(self, depth_now):
        """Скидання перед вмиканням режиму: щоб перша похідна не «вистрелила»,
        а інтеграл не тягнув накопичене за простою."""
        self.integral = 0.0
        self.depth_prev = depth_now   # перша похідна = 0, не сплеск
        self.deriv_f = 0.0

    def step(self, target, measured, dt):
        """Один такт. target/measured — глибина в метрах (вниз додатна).
        Повертає нормовану вертикальну тягу u ∈ [u_min, u_max]:
        u>0 — гребти ВНИЗ (глибше), u<0 — гребти ВГОРУ (до поверхні)."""
        e = target - measured                    # глибше цілі → e<0

        # I: накопичуємо й ОДРАЗУ затискаємо (антивіндап)
        self.integral += e * dt
        self.integral = clampf(self.integral, self.i_min, self.i_max)

        # D: від ВИМІРУ (не від помилки) → нема поштовху на зміну target.
        # (depth_prev − measured)/dt = мінус вертикальна швидкість.
        deriv = (self.depth_prev - measured) / dt
        a = dt / (dt + self.tau_d)               # коеф. ФНЧ на похідну
        self.deriv_f += (deriv - self.deriv_f) * a

        # сума трьох складових
        u = self.kp * e + self.ki * self.integral + self.kd * self.deriv_f

        # межі вертикальної тяги (насичення рушіїв)
        u = clampf(u, self.u_min, self.u_max)

        self.depth_prev = measured
        return u
