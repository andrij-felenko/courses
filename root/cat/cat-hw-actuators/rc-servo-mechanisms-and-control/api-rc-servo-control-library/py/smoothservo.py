import time

class SmoothServo:
    def __init__(self, min_us=1000, max_us=2000, max_step_us=15):
        self.min_us = min_us
        self.max_us = max_us
        self.max_step_us = max_step_us
        self.current_us = float((min_us + max_us) // 2)
        self.target_us = self.current_us

    def set_target(self, target_us):
        # Обмеження (clamping) в безпечних межах
        self.target_us = max(self.min_us, min(self.max_us, target_us))

    def update(self):
        # Ітеративна зміна ширини імпульсу
        diff = self.target_us - self.current_us
        if abs(diff) <= self.max_step_us:
            self.current_us = float(self.target_us)
        else:
            self.current_us += self.max_step_us if diff > 0 else -self.max_step_us
        return int(self.current_us)
