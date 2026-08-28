# Багата модель: правило живе в самому пристрої, поля закриті
class Device:
    def __init__(self):
        self._status = "new"      # приватне — ззовні не дотягтися
        self._home = None

    def commission(self, home_id):
        if self._status != "new":            # вартовий переходу — ТУТ, при своїх даних
            raise DomainError("пристрій уже введено в дім")
        self._status = "online"
        self._home = home_id
