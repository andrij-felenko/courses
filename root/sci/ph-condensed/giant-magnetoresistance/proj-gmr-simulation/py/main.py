import math

class GmrSpinValveSim:
    """Клас моделювання характеристик спинового клапана GMR."""

    def __init__(self, r_p: float = 100.0, gmr_ratio: float = 0.12, h_c: float = 0.5, h_ex: float = 25.0):
        """Ініціалізація параметрів спинового клапана.
        
        :param r_p: Опір у паралельному стані (Ом)
        :param gmr_ratio: Відносний коефіцієнт GMR (ΔR/R_P)
        :param h_c: Коерцитивна сила вільного шару (мТл)
        :param h_ex: Поле обмінного зсуву закріпленого шару (мТл)
        """
        self.r_p = r_p
        self.r_ap = r_p * (1.0 + gmr_ratio)
        self.h_c = h_c     
        self.h_ex = h_ex   

    def calculate_free_layer_angle(self, h_field: float, sweep_up: bool) -> float:
        """Обчислення кута намагніченості вільного шару з урахуванням коерцитивності гістерезису."""
        if sweep_up:
            if h_field < -self.h_c:
                return math.pi  # Намагніченість спрямована вліво (180°)
            elif h_field > self.h_c:
                return 0.0      # Намагніченість спрямована вправо (0°)
            else:
                return math.pi  # Збереження попередньої гілки гістерезису
        else:
            if h_field > self.h_c:
                return 0.0
            elif h_field < -self.h_c:
                return math.pi
            else:
                return 0.0

    def calculate_pinned_layer_angle(self, h_field: float) -> float:
        """Обчислення кута закріпленого шару (перемикається лише при високих полях H_ex)."""
        if h_field > -self.h_ex:
            return 0.0          # Закріплений стан під дією exchange bias (0°)
        else:
            return math.pi      # Зовнішнє поле подолало exchange bias (180°)

    def compute_resistance(self, theta_free: float, theta_pinned: float) -> float:
        """Обчислення електричного опору за кутом між векторами намагніченості."""
        cos_angle = math.cos(theta_free - theta_pinned)
        return self.r_p + 0.5 * (self.r_ap - self.r_p) * (1.0 - cos_angle)

    def run_sweep(self, h_min: float = -40.0, h_max: float = 40.0, steps: int = 200):
        """Виконання повного гістерезисного циклу розгортки магнітного поля."""
        results = []
        step_size = (h_max - h_min) / steps
        
        # Прямий хід розгортки (від h_min до h_max)
        for i in range(steps + 1):
            h = h_min + i * step_size
            t_free = self.calculate_free_layer_angle(h, sweep_up=True)
            t_pin = self.calculate_pinned_layer_angle(h)
            r = self.compute_resistance(t_free, t_pin)
            results.append((h, t_free, r, "up"))

        # Зворотний хід розгортки (від h_max до h_min)
        for i in range(steps + 1):
            h = h_max - i * step_size
            t_free = self.calculate_free_layer_angle(h, sweep_up=False)
            t_pin = self.calculate_pinned_layer_angle(h)
            r = self.compute_resistance(t_free, t_pin)
            results.append((h, t_free, r, "down"))

        return results

if __name__ == "__main__":
    sim = GmrSpinValveSim(r_p=100.0, gmr_ratio=0.10, h_c=0.8, h_ex=20.0)
    sweep_data = sim.run_sweep(-30.0, 30.0, 10)
    print(" H (mT) | theta_free (rad) | R (Ohm) | Sweep")
    print("-" * 45)
    for h, tf, r, direction in sweep_data[:6]:
        print(f"{h:7.2f} | {tf:16.3f} | {r:7.2f} | {direction}")
