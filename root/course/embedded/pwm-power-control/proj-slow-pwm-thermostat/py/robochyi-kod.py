# Двопозиційний регулятор із гістерезисом.
# Викликати з повільним темпом (напр., раз на секунду) з готовою температурою.
class BangBang:
    def __init__(self, setpoint, hyst):
        self.setpoint = setpoint   # бажана температура, °C
        self.hyst = hyst           # півширина зони нечутливості (гістерезис), °C
        self.heating = False       # поточний стан: гріємо чи ні

    def update(self, temp):
        if self.heating:
            # Гріємо — вимкнемо лише коли перевалили ВЕРХНІЙ поріг.
            if temp > self.setpoint + self.hyst:
                self.heating = False
        else:
            # Не гріємо — увімкнемо лише коли впали під НИЖНІЙ поріг.
            if temp < self.setpoint - self.hyst:
                self.heating = True
        thermostat_set_power(1000 if self.heating else 0)
