from dataclasses import dataclass
from math import atan, sin, cos

G = 9.80665                    # м/с², стандартне прискорення вільного падіння

@dataclass
class Bike:
    mass: float                # кг — гонщик, велосипед, бідони, все, що їде
    cda:  float = 0.36         # м² — C_d·A, уся аеродинаміка посадки одним числом
    crr:  float = 0.005        # безрозмірний коефіцієнт кочення шини
    rho:  float = 1.225        # кг/м³ — густина повітря
    eta:  float = 0.97         # частка потужності, що доходить від педалей до колеса

def air_density(altitude_m=0.0, temp_C=None):
    """Густина повітря за стандартною атмосферою: спершу тиск, тоді ρ = p/(R·T)."""
    p = 101325.0 * (1.0 - 2.25577e-5 * altitude_m) ** 5.25588       # Па
    if temp_C is None:
        temp_C = 15.0 - 0.0065 * altitude_m                          # стандартний градієнт
    return p / (287.05 * (temp_C + 273.15))

def power_budget(b, v, grade=0.0, headwind=0.0):
    """Ватти на педалях, розкладені на статті витрат. grade — ЧАСТКА (0.081 = 8.1 %)."""
    theta = atan(grade)                     # ухил у відсотках — тангенс, не синус
    v_air = v + headwind                    # зустрічний вітер додатний, попутний від'ємний
    w = {
        "тяжіння":    b.mass * G * sin(theta) * v,
        "кочення":    b.crr * b.mass * G * cos(theta) * v,
        "повітря":    0.5 * b.rho * b.cda * v_air * abs(v_air) * v,  # ×v ШЛЯХОВОЮ!
        "підшипники": v * (91.0 + 8.7 * v) * 1e-3,                   # Martin та ін., 1998
    }
    w["трансмісія"] = sum(w.values()) * (1.0 / b.eta - 1.0)          # ділення, не доданок
    return w

def pedal_power(b, v, grade=0.0, headwind=0.0):
    """Скільки ватів мусять видати ноги, щоб рівно триматися швидкості v (м/с)."""
    return sum(power_budget(b, v, grade, headwind).values())

def speed_for_power(b, power, grade=0.0, headwind=0.0, tol=1e-9):
    """Обернена задача: за потужністю знайти швидкість. Ділення відрізка навпіл."""
    v_calm = max(0.0, -headwind)            # де повітряна швидкість обнуляється
    if pedal_power(b, v_calm, grade, headwind) >= power:
        lo, hi = 0.0, v_calm                # сильний попутний: розв'язок нижче швидкості вітру
    else:
        lo, hi = v_calm, v_calm + 1.0
        while pedal_power(b, hi, grade, headwind) < power:
            hi = v_calm + 2.0 * (hi - v_calm)                # межа тікає вгору як v³ — швидко
            if hi - v_calm > 1e3:
                raise ValueError("розв'язку немає — перевір знаки ухилу й вітру")
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if pedal_power(b, mid, grade, headwind) < power:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

if __name__ == "__main__":
    climb = Bike(mass=78.0, cda=0.36, crr=0.005, rho=air_density(1200.0))
    for name, watts in power_budget(climb, 4.2, grade=0.081).items():
        print("%12s: %6.1f Вт" % (name, watts))
    print("%12s: %6.1f Вт" % ("РАЗОМ", pedal_power(climb, 4.2, grade=0.081)))

    flat = Bike(mass=78.0, cda=0.30, crr=0.005)              # рівнина, рівень моря
    print("250 Вт -> %.2f км/год" % (3.6 * speed_for_power(flat, 250.0)))
