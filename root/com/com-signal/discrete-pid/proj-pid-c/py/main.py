def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


class PID:
    """Дискретний ПІД зі станом і чотирма захистами (той самий модуль, що на C)."""

    def __init__(self, kp, ki, kd, tau, i_min, i_max, u_min, u_max):
        # параметри (задаємо при ініціалізації)
        self.kp, self.ki, self.kd = kp, ki, kd
        self.tau = tau                    # стала фільтра похідної, с
        self.i_min, self.i_max = i_min, i_max   # межі інтеграла (антивіндап)
        self.u_min, self.u_max = u_min, u_max   # межі виходу (виконавчий орган)
        # стан (живе між тактами)
        self.integral = 0.0               # накопичений інтеграл
        self.meas_prev = 0.0              # вимір на попередньому такті
        self.deriv_f = 0.0                # відфільтрована похідна

    def step(self, setpoint, meas, dt):
        e = setpoint - meas                           # помилка

        # I: накопичуємо й ОДРАЗУ затискаємо (антивіндап)
        self.integral += e * dt
        self.integral = _clamp(self.integral, self.i_min, self.i_max)

        # D: від виміру (не від помилки) → нема поштовху на зміну завдання
        deriv = (self.meas_prev - meas) / dt          # = −d(meas)/dt
        # однополюсний ФНЧ на похідну: гасить шумові сплески
        a = dt / (dt + self.tau)                      # 0 < a ≤ 1
        self.deriv_f += (deriv - self.deriv_f) * a

        # сума трьох складових
        u = self.kp * e + self.ki * self.integral + self.kd * self.deriv_f

        # межі виконавчого органу
        u = _clamp(u, self.u_min, self.u_max)

        self.meas_prev = meas                         # запам'ятати для наступного
        return u

    def reset(self, meas):
        """Скидання стану — при зброєнні/зльоті, перш ніж контур піде в роботу."""
        self.integral = 0.0
        self.meas_prev = meas      # щоб перша похідна була 0, а не сплеск
        self.deriv_f = 0.0
