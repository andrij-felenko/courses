from pathlib import Path

class FileStore:
    def __init__(self, model, path):
        self._model = model
        self._path = path
        model.on_change(self.save)       # той самий сигнал, що й у подань

    def save(self):
        Path(self._path).write_text(str(self._model.target))


# ── збірка: усе сходиться на одній моделі ──
model = Thermostat(22)
digit = DigitView(model)                 # підписник 1
bar   = BarView(model)                   # підписник 2
store = FileStore(model, "target.txt")   # підписник 3
controller = ThermostatController(model)

controller.plus_clicked()   # 22 → 23: обидва подання перемалювались, файл записався
