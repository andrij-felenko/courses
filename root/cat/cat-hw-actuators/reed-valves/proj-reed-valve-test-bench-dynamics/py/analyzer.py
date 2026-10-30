import math

class ValveAnalyzer:
    def __init__(self, time_data: list, pressure_data: list, flow_data: list):
        self.time_data = time_data
        self.pressure_data = pressure_data
        self.flow_data = flow_data

    def detect_phase_shift(self) -> float:
        # Простий метод пошуку кореляції або максимуמים для оцінки фазового зсуву
        max_p_idx = self.pressure_data.index(max(self.pressure_data))
        max_f_idx = self.flow_data.index(max(self.flow_data))
        
        dt = self.time_data[1] - self.time_data[0]
        time_diff = (max_f_idx - max_p_idx) * dt
        
        # Приблизна оцінка в градусах для частоти 100 Гц
        frequency = 100.0
        phase_deg = time_diff * frequency * 360.0
        return phase_deg

    def calculate_dynamic_reverse_flow(self) -> float:
        # Розрахунок мінімального (від'ємного) значення потоку як міри зворотного протікання
        min_flow = min(self.flow_data)
        if min_flow < 0:
            return abs(min_flow)
        return 0.0
