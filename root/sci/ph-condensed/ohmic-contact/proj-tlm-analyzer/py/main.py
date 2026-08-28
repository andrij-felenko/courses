import math
from typing import List, Dict, Optional

class TLMAnalyzer:
    """Клас аналізу даних вимірювань TLM та екстраполяції параметрів контакту."""
    
    def __init__(self, contact_width_um: float, contact_length_um: float):
        """
        :param contact_width_um: Ширина контактної площадки W у мікрометрах.
        :param contact_length_um: Довжина контактної площадки L у мікрометрах.
        """
        if contact_width_um <= 0 or contact_length_um <= 0:
            raise ValueError("Геометричні розміри контактів повинні бути додатними.")
        self.w_cm = contact_width_um * 1e-4   # Переведення мкм -> см
        self.l_cm = contact_length_um * 1e-4   # Переведення мкм -> см

    def analyze(self, spacings_um: List[float], resistances_ohm: List[float]) -> Optional[Dict[str, float]]:
        """
        Обробляє масиви відстаней d [мкм] та опорів R_T [Ом].
        :return: Словник з розрахованими параметрами або None у разі помилки.
        """
        n = len(spacings_um)
        if n < 2 or n != len(resistances_ohm):
            return None

        # Переведення зазорів d з мкм у см
        d_cm = [d * 1e-4 for d in spacings_um]

        # Обчислення сум МНК для лінійного рівняння Y = A*X + B
        sum_x = sum(d_cm)
        sum_y = sum(resistances_ohm)
        sum_xx = sum(x * x for x in d_cm)
        sum_xy = sum(x * y for x, y in zip(d_cm, resistances_ohm))

        denom = n * sum_xx - sum_x * sum_x
        if abs(denom) < 1e-15:
            return None

        slope = (n * sum_xy - sum_x * sum_y) / denom      # A = R_sh / W
        intercept = (sum_y * sum_xx - sum_x * sum_xy) / denom # B = 2 * R_c

        # Фізична валідація: нахил та відсічка повинні бути строго додатними
        if slope <= 0.0 or intercept <= 0.0:
            return None

        r_sh = slope * self.w_cm                            # Ом/кв
        r_c = intercept / 2.0                              # Ом
        l_t_cm = intercept / (2.0 * slope)                 # см
        
        # Перевірка на короткий/довгий контакт та обчислення точного rho_c
        ratio = self.l_cm / l_t_cm
        if ratio < 2.0:
            rho_c = r_c * self.w_cm * l_t_cm * math.tanh(ratio)
        else:
            rho_c = r_c * self.w_cm * l_t_cm               # Ом·см²

        # Обчислення коефіцієнта детермінації R^2
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in resistances_ohm)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(d_cm, resistances_ohm))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return {
            "r_sh_ohm_sq": r_sh,
            "r_c_ohm": r_c,
            "l_t_um": l_t_cm * 1e4,
            "rho_c_ohm_cm2": rho_c,
            "r2_score": r2,
            "l_ratio": ratio
        }

if __name__ == "__main__":
    analyzer = TLMAnalyzer(contact_width_um=100.0, contact_length_um=20.0)
    # Набір даних: зазори d = [5, 10, 15, 20, 25] мкм, виміряні R_T [Ом]
    d_data = [5.0, 10.0, 15.0, 20.0, 25.0]
    r_data = [12.4, 18.2, 24.1, 30.0, 35.9]

    res = analyzer.analyze(d_data, r_data)
    if res:
        print(f"R_sh    = {res['r_sh_ohm_sq']:.2f} Ohm/sq")
        print(f"R_c     = {res['r_c_ohm']:.3f} Ohm")
        print(f"L_T     = {res['l_t_um']:.3f} um")
        print(f"rho_c   = {res['rho_c_ohm_cm2']:.3e} Ohm*cm^2")
        print(f"R^2     = {res['r2_score']:.4f}")
        print(f"L / L_T = {res['l_ratio']:.2f}")
