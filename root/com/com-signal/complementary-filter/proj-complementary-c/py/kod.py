from dataclasses import dataclass


@dataclass
class Comp:
    # параметри
    alpha: float          # базовий коеф. довіри гіроскопу (напр. 0.98)
    g: float              # очікувана норма прискорення спокою, м/с² (9.81)
    acc_band: float       # допуск |a|−g, за яким акселерометру не вірити
    # стан (живе між тактами)
    roll: float = 0.0     # поточна оцінка крену, рад
    pitch: float = 0.0    # поточна оцінка тангажа, рад
    seeded: bool = False  # чи засіяно стартову оцінку
