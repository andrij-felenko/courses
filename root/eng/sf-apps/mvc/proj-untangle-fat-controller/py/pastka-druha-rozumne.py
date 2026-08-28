# ПАСТКА — розумне подання: у читача залізла логіка й навіть запис у модель
class BarView:
    def render(self):
        t = self._model.target
        if t > 28:                       # ← подання САМО «підправляє» число під себе
            t = 28
        if self._model.target >= Thermostat.MAX:   # ← подання ВИРІШУЄ політику
            self._model.nudge(-1)                  # ← і МІНЯЄ модель — читач став писарем
        span = Thermostat.MAX - Thermostat.MIN
        filled = round((t - Thermostat.MIN) / span * 20)
        print("  " + "█" * filled + "·" * (20 - filled))
