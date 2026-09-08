#!/usr/bin/env python3
"""
piston_pump_simulator.py
Моделювання кінематики ходу поршнів та пульсації миттєвої подачі
аксіально-поршневого насоса з похилою шайбою.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class PumpParameters:
    pitch_radius_m: float = 0.040        # Радіус розташування осей поршнів (м)
    swashplate_angle_deg: float = 18.0   # Кут нахилу похилої шайби (градуси)
    piston_diameter_m: float = 0.016     # Діаметр плунжера (м)
    num_pistons: int = 9                 # Кількість поршнів (стандарт 9 або 7)
    speed_rpm: float = 1500.0            # Частота обертання вала (об/хв)
    fluid_density_kg_m3: float = 870.0   # Густина оливи (кг/м^3)

class AxialPistonPumpSimulator:
    def __init__(self, params: PumpParameters):
        self.params = params
        self.gamma_rad = math.radians(params.swashplate_angle_deg)
        self.omega = 2.0 * math.pi * (params.speed_rpm / 60.0)
        self.piston_area = math.pi * (params.piston_diameter_m ** 2) / 4.0
        self.stroke_length = 2.0 * params.pitch_radius_m * math.tan(self.gamma_rad)

    def piston_displacement(self, phi_rad: float) -> float:
        """Хід поршня s(phi) = R * tg(gamma) * (1 - cos(phi)) [м]."""
        return self.params.pitch_radius_m * math.tan(self.gamma_rad) * (1.0 - math.cos(phi_rad))

    def piston_velocity(self, phi_rad: float) -> float:
        """Осьова швидкість поршня v(phi) = omega * R * tg(gamma) * sin(phi) [м/с]."""
        return self.omega * self.params.pitch_radius_m * math.tan(self.gamma_rad) * math.sin(phi_rad)

    def instantaneous_flow(self, phi_rad: float) -> float:
        """
        Сумарна подача насоса Q(phi) [л/хв].
        Поршень нагнітає оливу лише тоді, коли рухається вперед (v > 0, фаза 0..pi).
        """
        z = self.params.num_pistons
        q_total_m3_s = 0.0
        for i in range(z):
            phi_i = (phi_rad + 2.0 * math.pi * i / z) % (2.0 * math.pi)
            if 0.0 <= phi_i < math.pi:
                v_i = self.piston_velocity(phi_i)
                q_total_m3_s += self.piston_area * v_i

        return q_total_m3_s * 60000.0  # переведення в л/хв

    def simulate_revolution(self, num_points: int = 360) -> Tuple[List[float], List[float], float]:
        """Симуляція одного повного оберту вала 0..360 градусів."""
        angles_deg = []
        flows_l_min = []
        for step in range(num_points):
            phi_deg = step * (360.0 / num_points)
            phi_rad = math.radians(phi_deg)
            flow = self.instantaneous_flow(phi_rad)
            angles_deg.append(phi_deg)
            flows_l_min.append(flow)

        q_min = min(flows_l_min)
        q_max = max(flows_l_min)
        q_avg = sum(flows_l_min) / len(flows_l_min)
        ripple_percent = ((q_max - q_min) / q_avg) * 100.0

        return angles_deg, flows_l_min, ripple_percent

def main():
    print("================================================================")
    print("РОЗРАХУНОК АКСІАЛЬНО-ПОРШНЕВОГО НАСОСА З ПОХИЛОЮ ШАЙБОЮ")
    print("================================================================")

    # Порівняння непарного (Z=9) та парного (Z=8) насосів
    pump_z9 = AxialPistonPumpSimulator(PumpParameters(num_pistons=9))
    pump_z8 = AxialPistonPumpSimulator(PumpParameters(num_pistons=8))

    _, flows_9, ripple_9 = pump_z9.simulate_revolution()
    _, flows_8, ripple_8 = pump_z8.simulate_revolution()

    print(f"Хід поршня H: {pump_z9.stroke_length * 1000.0:.2f} мм")
    print(f"Робочий об'єм V_0 (Z=9): {pump_z9.stroke_length * pump_z9.piston_area * 9 * 1e6:.1f} см^3/об")
    print(f"Середня подача при 1500 об/хв: {sum(flows_9)/len(flows_9):.2f} л/хв")
    print("----------------------------------------------------------------")
    print(f"Непарна кількість Z=9: пульсація delta_Q = {ripple_9:.2f}% (ПРОМИСЛОВИЙ СТАНДАРТ)")
    print(f"Парна кількість   Z=8: пульсація delta_Q = {ripple_8:.2f}% (НЕПРИПУСТИМІ ГІДРОУДАРИ)")
    print("================================================================")

if __name__ == "__main__":
    main()
