# Два пороги в одиницях коду АЦП; TH_HI > TH_LO — це і є ширина мертвої зони.
TH_HI = 2600
TH_LO = 2400

class ThresholdHysteresis:
    def __init__(self):
        self.tripped = False          # пам'ять стану між викликами

    def __call__(self, x: int) -> bool:
        if not self.tripped:
            if x > TH_HI:
                self.tripped = True   # увімкнення — лише вгорі
        else:
            if x < TH_LO:
                self.tripped = False  # вимкнення — лише внизу
        return self.tripped
