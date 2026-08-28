# Сторож порога з гістерезисом: вмикається на ON, вимикається на OFF (OFF < ON).
class Hysteresis:
    def __init__(self, on_level, off_level):  # поріг вмикання / вимикання (нижчий!)
        self.on_level = on_level
        self.off_level = off_level
        self.state = False

    def update(self, value):
        """Подати нове значення, повернути стан тривоги."""
        if not self.state and value >= self.on_level:
            self.state = True                 # піднялись вище — вмикаємось
        if self.state and value <= self.off_level:
            self.state = False                # впали нижче — відпускаємо
        return self.state                     # між порогами — не міняємось


# Наприклад, стерегти за ppm-еквівалентом LPG: тривога від 350, відбій нижче 250.
lpg_watch = Hysteresis(350.0, 250.0)
