import math
import cmath
import random
from typing import List, Tuple

class MachZehnderSimulator:
    """Чисельний симулятор оптичного інтерферометра Маха — Цендера.
    
    Моделює поширення хвилі, фазовий зсув у плечі за рахунок зміни n,
    гауссівський фазовий шум та балансне фотодетектування.
    """

    def __init__(self, wavelength_nm: float = 632.8, arm_length_mm: float = 100.0):
        self.wavelength = wavelength_nm * 1e-9  # перевід у метри
        self.arm_length = arm_length_mm * 1e-3  # перевід у метри
        self.k = 2.0 * math.pi / self.wavelength

    def simulate_sample(self, delta_n: float, phase_noise_std: float = 0.005) -> Tuple[float, float, float]:
        """Обчислює інтенсивності I1, I2 та різницевий сигнал S_diff для заданого Δn."""
        # Фазовий набіг у плечі A та B
        phi_a = self.k * (1.0 + delta_n) * self.arm_length
        phi_b = self.k * 1.0 * self.arm_length + random.gauss(0.0, phase_noise_std)

        # Комплексна вхідна хвиля з нормованою амплітудою E0 = 1.0
        e_in = complex(1.0, 0.0)

        # BS1: розщеплення амплітуди
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        e1_bs1 = e_in * inv_sqrt2
        e2_bs1 = e_in * complex(0.0, inv_sqrt2)

        # Поширення хвильовими плечима
        e1_arm = e1_bs1 * cmath.exp(complex(0.0, phi_a))
        e2_arm = e2_bs1 * cmath.exp(complex(0.0, phi_b))

        # BS2: зведення хвиль
        e_out1 = inv_sqrt2 * (e1_arm * complex(0.0, 1.0) + e2_arm)
        e_out2 = inv_sqrt2 * (e1_arm + e2_arm * complex(0.0, 1.0))

        # Фотодетектування
        i1 = abs(e_out1) ** 2
        i2 = abs(e_out2) ** 2
        diff_signal = i1 - i2

        return i1, i2, diff_signal

    def scan_refractive_index(self, start_dn: float, end_dn: float, steps: int) -> List[Tuple[float, float, float, float]]:
        """Виконує сканування показника заломлення та повертає список результатів."""
        results = []
        step_size = (end_dn - start_dn) / steps
        for i in range(steps + 1):
            dn = start_dn + i * step_size
            i1, i2, diff = self.simulate_sample(dn)
            results.append((dn, i1, i2, diff))
        return results


def main():
    sim = MachZehnderSimulator(wavelength_nm=632.8, arm_length_mm=100.0)
    print("Чисельне моделювання сканування показника заломлення (Python):")
    print(f"{'delta_n':>12} | {'I1':>8} | {'I2':>8} | {'Diff Signal':>12}")
    print("-" * 48)

    scan_data = sim.scan_refractive_index(0.0, 10e-6, 10)
    for dn, i1, i2, diff in scan_data:
        print(f"{dn:12.4e} | {i1:8.4f} | {i2:8.4f} | {diff:12.4f}")

if __name__ == "__main__":
    main()
