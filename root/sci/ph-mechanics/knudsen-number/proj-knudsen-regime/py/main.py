import math
from dataclasses import dataclass
from enum import Enum

class FlowRegime(Enum):
    CONTINUUM = "Суцільний (Continuum, Kn < 0.01)"
    SLIP = "З ковзанням (Slip, 0.01 <= Kn < 0.1)"
    TRANSITION = "Перехідний (Transition, 0.1 <= Kn < 10)"
    FREE_MOLECULAR = "Вільномолекулярний (Free-Molecular, Kn >= 10)"

BOLTZMANN_K = 1.380649e-23  # Дж/К

@dataclass
class GasProperties:
    name: str
    molecular_diameter_m: float  # м
    molar_mass_kg_mol: float    # кг/моль

GAS_AIR = GasProperties("Air (N2/O2)", 0.37e-9, 0.02897)
GAS_HE  = GasProperties("Helium", 0.22e-9, 0.00400)
GAS_N2  = GasProperties("Nitrogen", 0.375e-9, 0.02801)
GAS_CH4 = GasProperties("Methane", 0.380e-9, 0.01604)

@dataclass
class KnudsenResult:
    lambda_m: float
    knudsen_number: float
    regime: FlowRegime
    flow_enhancement_factor: float
    flow_enhancement_2nd: float

def analyze_gas_flow(
    temperature_k: float,
    pressure_pa: float,
    char_length_m: float,
    gas: GasProperties = GAS_AIR,
    accommodation_coef: float = 1.0
) -> KnudsenResult:
    """Обчислює вільний пробіг, число Кнудсена та режим течії."""
    d = gas.molecular_diameter_m
    # λ = k_B * T / (sqrt(2) * pi * d^2 * P)
    lambda_m = (BOLTZMANN_K * temperature_k) / (math.sqrt(2) * math.pi * (d ** 2) * pressure_pa)
    kn = lambda_m / char_length_m

    if kn < 0.01:
        regime = FlowRegime.CONTINUUM
    elif kn < 0.1:
        regime = FlowRegime.SLIP
    elif kn < 10.0:
        regime = FlowRegime.TRANSITION
    else:
        regime = FlowRegime.FREE_MOLECULAR

    sigma = accommodation_coef
    flow_factor = 1.0 + 6.0 * ((2.0 - sigma) / sigma) * kn
    flow_factor_2nd = flow_factor + 12.0 * 0.25 * (kn ** 2)

    return KnudsenResult(lambda_m, kn, regime, flow_factor, flow_factor_2nd)


if __name__ == '__main__':
    print("=========================================================")
    print("  Аналізатор числа Кнудсена та режимів розрідженого газу")
    print("=========================================================\n")

    # Сценарій 1: Головка жорсткого диска (L = 10 нм)
    res1 = analyze_gas_flow(298.15, 101325.0, 10e-9, GAS_AIR)
    print(f"--- Сценарій 1: Зазор головки HDD (L = 10 нм, P = 1 атм) ---")
    print(f"Середній вільний пробіг λ: {res1.lambda_m * 1e9:.2f} нм")
    print(f"Число Кнудсена Kn:          {res1.knudsen_number:.3f}")
    print(f"Режим течії:                {res1.regime.value}")
    print(f"Підсилення витрати (1-й):   {res1.flow_enhancement_factor:.3f}")
    print(f"Підсилення витрати (2-й):   {res1.flow_enhancement_2nd:.3f}\n")

    # Сценарій 2: Нанопора сланцю (L = 10 нм, P = 25 МПа)
    res3 = analyze_gas_flow(323.15, 25e6, 10e-9, GAS_CH4)
    print(f"--- Сценарій 2: Нанопора сланцю (L = 10 нм, P = 25 МПа, Метан) ---")
    print(f"Середній вільний пробіг λ: {res3.lambda_m * 1e9:.2f} нм")
    print(f"Число Кнудсена Kn:          {res3.knudsen_number:.3f}")
    print(f"Режим течії:                {res3.regime.value}")
    print(f"Підсилення витрати:         {res3.flow_enhancement_factor:.3f}\n")

    # Сценарій 3: Вакуумна лінія (L = 10 см, P = 0.1 Па)
    res2 = analyze_gas_flow(298.15, 0.1, 0.10, GAS_AIR)
    print(f"--- Сценарій 3: Вакуумна лінія (L = 10 см, P = 0.1 Па) ---")
    print(f"Середній вільний пробіг λ: {res2.lambda_m * 1e2:.2f} см")
    print(f"Число Кнудсена Kn:          {res2.knudsen_number:.3f}")
    print(f"Режим течії:                {res2.regime.value}")
    print(f"Підсилення витрати:         {res2.flow_enhancement_factor:.3f}")
