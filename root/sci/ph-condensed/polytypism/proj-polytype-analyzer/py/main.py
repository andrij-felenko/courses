import math
import cmath
import re
from typing import List, Tuple, Dict

class PolytypeAnalyzer:
    """
    Автоматизований аналізатор кристалографічних послідовностей укладання політипів.
    Підтримує номенклатурні перетворення Рамсделла, Жданова та Ягодзінського,
    а також симуляцію рентгенівського структурного фактора I(10L).
    """
    
    POS_MAP: Dict[str, float] = {'A': 0.0, 'B': 2.0 / 3.0, 'C': 1.0 / 3.0}

    def __init__(self, zhdanov_pair: Tuple[int, int], name: str = "Custom"):
        """
        Ініціалізація аналізатора парами індексів Жданова (n1, n2).
        """
        if zhdanov_pair[0] < 0 or zhdanov_pair[1] < 0:
            raise ValueError("Індекси Жданова n1 та n2 повинні бути невід'ємними.")
            
        self.name = name
        self.zhdanov = zhdanov_pair
        self.sequence = self._expand_zhdanov(zhdanov_pair)
        self.period = len(self.sequence)
        self.jagodzinski = self._compute_jagodzinski()
        self.hexagonality = self._compute_hexagonality()

    @classmethod
    def from_ramsdell(cls, ramsdell_symbol: str) -> 'PolytypeAnalyzer':
        """
        Фабричний метод для створення об'єкта за стандартною назвою Рамсделла (наприклад "4H", "6H", "3C", "15R").
        """
        known_polytypes: Dict[str, Tuple[int, int]] = {
            "2H": (1, 1),
            "3C": (3, 0),
            "4H": (2, 2),
            "6H": (3, 3),
            "8H": (4, 4),
            "15R": (3, 2),
            "21R": (4, 3)
        }
        symbol_clean = ramsdell_symbol.strip().upper()
        if symbol_clean in known_polytypes:
            return cls(known_polytypes[symbol_clean], name=symbol_clean)
        raise ValueError(f"Невідомий політип Рамсделла: {ramsdell_symbol}")

    def _expand_zhdanov(self, pair: Tuple[int, int]) -> List[str]:
        """Розгортає пару індексів Жданова в циклічний ланцюжок шарів A, B, C."""
        n1, n2 = pair
        if n1 == 0 and n2 == 0:
            return ['A']
            
        seq = ['A']
        curr_pos = 0  # 0: A, 1: B, 2: C
        
        # Прямий хід (+1)
        for _ in range(n1):
            curr_pos = (curr_pos + 1) % 3
            seq.append(['A', 'B', 'C'][curr_pos])
            
        # Зворотний хід (-1)
        for _ in range(n2):
            curr_pos = (curr_pos - 1) % 3
            seq.append(['A', 'B', 'C'][curr_pos])
            
        # Вилучаємо останній дубльований шар для забезпечення трансляційної комірки
        return seq[:-1]

    def _compute_jagodzinski(self) -> str:
        """Обчислює рядок символів Ягодзінського (h/k) з урахуванням циклічних крайових умов."""
        n = self.period
        if n < 3:
            return 'k' * n
            
        jag: List[str] = []
        for i in range(n):
            prev_layer = self.sequence[(i - 1 + n) % n]
            next_layer = self.sequence[(i + 1) % n]
            if prev_layer == next_layer:
                jag.append('h')
            else:
                jag.append('k')
        return "".join(jag)

    def _compute_hexagonality(self) -> float:
        """Обчислює відсоток гексагональних шарів alpha_h."""
        if self.period == 0:
            return 0.0
        h_count = self.jagodzinski.count('h')
        return (h_count / self.period) * 100.0

    def compute_structure_factor(self, l_index: float) -> float:
        """
        Обчислює квадрат модуля структурного фактора I(10L) = |S(L)|^2
        для заданого уздовж стержня L значення оберненої ґратки.
        """
        s_complex = 0.0 + 0.0j
        n = self.period
        for j, pos in enumerate(self.sequence):
            x_j = self.POS_MAP[pos]
            phase = 2.0 * math.pi * (x_j + l_index * (j / n))
            s_complex += cmath.exp(1j * phase)
        return abs(s_complex) ** 2

    def generate_diffraction_profile(self, l_min: float = 0.0, l_max: float = 2.0, step: float = 0.1) -> List[Tuple[float, float]]:
        """Генерує дифракційний профіль інтенсивності вздовж стержня 10L."""
        profile: List[Tuple[float, float]] = []
        curr_l = l_min
        while curr_l <= l_max + 1e-9:
            intensity = self.compute_structure_factor(curr_l)
            profile.append((round(curr_l, 4), intensity))
            curr_l += step
        return profile


def main():
    polytypes = [
        PolytypeAnalyzer.from_ramsdell("3C"),
        PolytypeAnalyzer.from_ramsdell("4H"),
        PolytypeAnalyzer.from_ramsdell("6H"),
        PolytypeAnalyzer.from_ramsdell("15R")
    ]
    
    print(f"{'Політип':<10} | {'Період N':<8} | {'Символ Жданова':<15} | {'Ягодзінський':<18} | {'α_h (%)':<10}")
    print("-" * 75)
    for p in polytypes:
        zh_str = f"({p.zhdanov[0]}, {p.zhdanov[1]})"
        print(f"{p.name:<10} | {p.period:<8} | {zh_str:<15} | {p.jagodzinski:<18} | {p.hexagonality:.1f}%")

    print("\nДифракційні піки 4H-SiC вздовж стержня 10L:")
    sim_4h = PolytypeAnalyzer.from_ramsdell("4H")
    for l_val, intensity in sim_4h.generate_diffraction_profile(0.0, 2.0, 0.25):
        print(f"L = {l_val:4.2f} | Інтенсивність I(10L): {intensity:6.3f}")

if __name__ == "__main__":
    main()
