class DigitView:
    def __init__(self, model):
        self._model = model
        model.on_change(self.render)     # підписатися на сигнал зміни
        self.render()                    # намалюватися одразу, не чекаючи першої зміни

    def render(self):
        print(f"  {self._model.target}°")


class BarView:
    def __init__(self, model):
        self._model = model
        model.on_change(self.render)
        self.render()

    def render(self):
        t = self._model.target
        span = Thermostat.MAX - Thermostat.MIN
        filled = round((t - Thermostat.MIN) / span * 20)
        print("  " + "█" * filled + "·" * (20 - filled))
