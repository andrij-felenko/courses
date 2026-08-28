import math
from typing import List, Tuple, Dict, Any

class CNTGenerator:
    """Генератор геометричних та електронних параметрів вуглецевих нанотрубок."""
    
    A_CC: float = 0.142  # довжина зв'язку C-C у нанометрах
    A: float = A_CC * math.sqrt(3)  # 0.24613 нм — стала ґратки
    TIGHT_BINDING_T: float = 2.7  # еВ — інтеграл перескоку

    def __init__(self, n: int, m: int) -> None:
        if n < 0 or m < 0 or (n == 0 and m == 0):
            raise ValueError("Індекси хіральності (n, m) повинні бути невід'ємними та не нульовими одночасно.")
        self.n = n
        self.m = m

    def compute_properties(self) -> Dict[str, Any]:
        """Обчислює аналітичні фізичні параметри нанотрубки."""
        n, m = self.n, self.m
        l_circ = self.A * math.sqrt(n**2 + n * m + m**2)
        diameter = l_circ / math.pi
        
        cos_theta = (2 * n + m) / (2 * math.sqrt(n**2 + n * m + m**2))
        theta_deg = math.degrees(math.acos(clamp(cos_theta, -1.0, 1.0)))

        is_metal = ((n - m) % 3 == 0)
        band_gap = 0.0 if is_metal else (2 * self.A_CC * self.TIGHT_BINDING_T) / diameter

        return {
            "indices": (n, m),
            "diameter_nm": round(diameter, 4),
            "chiral_angle_deg": round(theta_deg, 2),
            "is_metal": is_metal,
            "band_gap_eV": round(band_gap, 4)
        }

    def generate_unit_cell_atoms(self) -> List[Tuple[float, float, float]]:
        """Генерує 3D-координати атомів однієї елементарної комірки в нанометрах."""
        n, m = self.n, self.m
        d_val = (self.A / math.pi) * math.sqrt(n**2 + n * m + m**2)
        radius = d_val / 2.0
        
        gcd_val = math.gcd(2 * m + n, 2 * n + m)
        num_hexagons = (2 * (n**2 + n * m + m**2)) // gcd_val
        atoms: List[Tuple[float, float, float]] = []

        for i in range(num_hexagons):
            phi = (2 * math.pi * i) / num_hexagons
            z = (i * self.A_CC) / math.sqrt(3)
            
            x = radius * math.cos(phi)
            y = radius * math.sin(phi)
            atoms.append((round(x, 4), round(y, 4), round(z, 4)))

        return atoms

def clamp(val: float, min_val: float, max_val: float) -> float:
    """Обмежує значення в інтервалі [min_val, max_val] для запобігання похибкам acos."""
    return max(min_val, min(val, max_val))

if __name__ == "__main__":
    cnt = CNTGenerator(10, 0) # Зигзаг (10, 0)
    props = cnt.compute_properties()
    print("Параметри нанотрубки:", props)
    atoms = cnt.generate_unit_cell_atoms()
    print(f"Згенеровано {len(atoms)} атомів у 3D.")
