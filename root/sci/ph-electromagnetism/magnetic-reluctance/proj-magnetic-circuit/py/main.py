import math

class CoreMaterial:
    """Модель матеріалу осердя за формулою Брауера."""
    def __init__(self, k1: float = 4.5, k2: float = 3.8, k3: float = 120.0, b_sat: float = 0.42):
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.b_sat = b_sat

    def h_field(self, b: float) -> float:
        """Напруженість H(B) у А/м."""
        return (self.k1 * math.exp(self.k2 * b * b) + self.k3) * b

    def dh_db(self, b: float) -> float:
        """Похідна dH/dB."""
        b2 = b * b
        exp_val = math.exp(self.k2 * b2)
        return self.k1 * exp_val * (1.0 + 2.0 * self.k2 * b2) + self.k3


def solve_magnetic_circuit(l_core: float, l_gap: float, area: float, 
                           turns: int, current: float, mat: CoreMaterial) -> dict:
    """Розв'язок нелінійного магнітного кола методом Ньютона-Рафсона."""
    mu0 = 4.0 * math.pi * 1e-7
    mmf = turns * current
    
    # Початкове наближення для B
    b = 0.1
    max_iter = 100
    tol = 1e-7

    for iteration in range(max_iter):
        h = mat.h_field(b)
        f_val = h * l_core + (b / mu0) * l_gap - mmf
        
        dh = mat.dh_db(b)
        df_val = dh * l_core + l_gap / mu0
        
        delta = f_val / df_val
        b -= delta
        
        if b < 0:
            b = 1e-4
            
        if abs(delta) < tol:
            break

    flux = b * area
    reluctance_core = (mat.h_field(b) * l_core) / flux if flux > 0 else 0
    reluctance_gap = l_gap / (mu0 * area)
    total_reluctance = reluctance_core + reluctance_gap
    inductance = (turns * turns) / total_reluctance

    return {
        "b_field": b,
        "flux": flux,
        "reluctance_core": reluctance_core,
        "reluctance_gap": reluctance_gap,
        "total_reluctance": total_reluctance,
        "inductance_uH": inductance * 1e6,
        "iterations": iteration + 1
    }


if __name__ == "__main__":
    material = CoreMaterial(k1=4.5, k2=3.8, k3=120.0)
    res = solve_magnetic_circuit(l_core=0.114, l_gap=0.001, area=2.11e-4, 
                                 turns=30, current=8.0, mat=material)
    print(f"B = {res['b_field']:.4f} Тл")
    print(f"Потік = {res['flux']*1e6:.2f} мкВб")
    print(f"Rm_core = {res['reluctance_core']:.1f} А·вт/Вб")
    print(f"Rm_gap  = {res['reluctance_gap']:.1f} А·вт/Вб")
    print(f"Індуктивність = {res['inductance_uH']:.2f} мкГн")
