import math
from typing import List, Tuple, Dict

class Electrode:
    def __init__(self, x: float, y: float, z: float, current: float):
        self.x = x
        self.y = y
        self.z = z  # глибина занурення центру витоку (м)
        self.current = current  # струм витоку (А)

class GroundPotentialSimulator:
    def __init__(self, soil_resistivity: float, body_resistance: float = 1000.0, step_distance: float = 0.8):
        self.rho = soil_resistivity  # питомий опір ґрунту (Ом·м)
        self.R_b = body_resistance   # опір тіла людини (Ом)
        self.s = step_distance       # довжина кроку (м)
        self.electrodes: List[Electrode] = []

    def add_electrode(self, x: float, y: float, z: float, current: float) -> None:
        self.electrodes.append(Electrode(x, y, z, current))

    def potential_at(self, x: float, y: float) -> float:
        """Обчислення потенціалу V(x, y) на поверхні землі (z=0) в вольтах."""
        v_total = 0.0
        for el in self.electrodes:
            dx = x - el.x
            dy = y - el.y
            r = math.sqrt(dx * dx + dy * dy + el.z * el.z)
            if r < 0.01:
                r = 0.01  # уникнення ділення на нуль біля електрода
            v_total += (self.rho * el.current) / (2.0 * math.pi * r)
        return v_total

    def max_step_voltage_at(self, x: float, y: float, angles_count: int = 16) -> Tuple[float, float]:
        """Знаходження максимальної крокової напруги в точці (x, y) та напрямку кроку."""
        v_center = self.potential_at(x, y)
        max_v_step = 0.0
        best_angle = 0.0

        for i in range(angles_count):
            angle = 2.0 * math.pi * i / angles_count
            nx = x + self.s * math.cos(angle)
            ny = y + self.s * math.sin(angle)
            v_next = self.potential_at(nx, ny)
            v_step = abs(v_center - v_next)
            if v_step > max_v_step:
                max_v_step = v_step
                best_angle = angle

        return max_v_step, best_angle

    def calculate_foot_resistance(self, foot_radius: float = 0.08) -> float:
        """Опір контакту однієї ступні з землею (Ом)."""
        return self.rho / (4.0 * foot_radius)

    def evaluate_safety(self, max_v_step: float, fault_duration_sec: float) -> Dict[str, float]:
        """Перевірка безпеки за критерієм Далзіела (IEEE Std 80)."""
        R_f = self.calculate_foot_resistance()
        R_total = self.R_b + 2.0 * R_f
        I_body_mA = (max_v_step / R_total) * 1000.0
        
        # Допустимий струм крізь тіло за формулою Далзіела (для людини 50 кг)
        I_limit_mA = (116.0 / math.sqrt(fault_duration_sec))
        
        is_safe = I_body_mA <= I_limit_mA
        return {
            "max_v_step_volts": max_v_step,
            "foot_resistance_ohms": R_f,
            "total_circuit_ohms": R_total,
            "body_current_mA": I_body_mA,
            "limit_current_mA": I_limit_mA,
            "is_safe": 1.0 if is_safe else 0.0
        }

def main():
    # Налаштування параметрів: ґрунт 100 Ом·м, час відключення захисту 0.5 с
    sim = GroundPotentialSimulator(soil_resistivity=100.0)
    
    # Додаємо 4 заземлювальні стержні по кутах квадрата 10х10 м (струм 250 А на стержень)
    sim.add_electrode(x=0.0,  y=0.0,  z=0.5, current=250.0)
    sim.add_electrode(x=10.0, y=0.0,  z=0.5, current=250.0)
    sim.add_electrode(x=0.0,  y=10.0, z=0.5, current=250.0)
    sim.add_electrode(x=10.0, y=10.0, z=0.5, current=250.0)

    print("=== Сканування сітки потенціалів ґрунту (15х15 м) ===")
    overall_max_step = 0.0
    critical_point = (0.0, 0.0)

    # Скануємо поверхню з кроком 0.5 м
    for ix in range(-20, 220, 5):
        x = ix / 10.0
        for iy in range(-20, 220, 5):
            y = iy / 10.0
            v_step, _ = sim.max_step_voltage_at(x, y)
            if v_step > overall_max_step:
                overall_max_step = v_step
                critical_point = (x, y)

    print(f"Найкритичніша точка: x={critical_point[0]:.1f} м, y={critical_point[1]:.1f} м")
    res = sim.evaluate_safety(overall_max_step, fault_duration_sec=0.5)
    
    print(f"Максимальна крокова напруга: {res['max_v_step_volts']:.1f} В")
    print(f"Опір кола кроку (R_b + 2*R_f): {res['total_circuit_ohms']:.1f} Ом")
    print(f"Розрахунковий струм крізь тіло: {res['body_current_mA']:.1f} мА")
    print(f"Гранично допустимий струм (0.5 с): {res['limit_current_mA']:.1f} мА")
    print(f"Оцінка безпеки: {'БЕЗПЕЧНО' if res['is_safe'] > 0 else 'НЕБЕЗПЕЧНО (Потрібне вирівнювання потенціалів!)'}")

if __name__ == "__main__":
    main()
