import math

K_BOLTZMANN = 1.380649e-23
K_AVOGADRO = 6.02214076e23
K_GAS_CONSTANT = K_BOLTZMANN * K_AVOGADRO

class EquipartitionCalculatorPy:
    def __init__(self, degrees_trans=3, degrees_rot=2, vib_temperatures=None, rot_temperature=85.4):
        self.degrees_trans = degrees_trans
        self.degrees_rot = degrees_rot
        self.vib_temperatures = vib_temperatures if vib_temperatures is not None else []
        self.rot_temperature = rot_temperature

    def classical_molar_heat_capacity_cv(self) -> float:
        f_total_quad = self.degrees_trans + self.degrees_rot + 2.0 * len(self.vib_temperatures)
        return 0.5 * f_total_quad * K_GAS_CONSTANT

    def quantum_molar_heat_capacity_cv(self, temp_kelvin: float) -> float:
        if temp_kelvin <= 0.0:
            raise ValueError("Температура повинна бути додатною")

        cv_sum = 0.5 * self.degrees_trans * K_GAS_CONSTANT

        if self.degrees_rot > 0:
            if temp_kelvin > self.rot_temperature:
                cv_sum += 0.5 * self.degrees_rot * K_GAS_CONSTANT
            else:
                ratio = self.rot_temperature / temp_kelvin
                cv_sum += 0.5 * self.degrees_rot * K_GAS_CONSTANT * math.exp(-ratio)

        for theta_vib in self.vib_temperatures:
            x = theta_vib / temp_kelvin
            if x > 100.0:
                continue
            exp_x = math.exp(x)
            einstein_factor = (x * x * exp_x) / ((exp_x - 1.0) ** 2)
            cv_sum += K_GAS_CONSTANT * einstein_factor

        return cv_sum

if __name__ == "__main__":
    calc = EquipartitionCalculatorPy(degrees_trans=3, degrees_rot=2, vib_temperatures=[3371.0], rot_temperature=2.88)
    print(f"Класична C_V (Py): {calc.classical_molar_heat_capacity_cv():.2f} Дж/(моль·К)")
    print(f"Квантова C_V 300K (Py): {calc.quantum_molar_heat_capacity_cv(300.0):.2f} Дж/(моль·К)")
