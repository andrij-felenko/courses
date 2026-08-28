from dataclasses import dataclass

# Захисний рівень (HPL) приймач обчислює з даних цілісності SBAS —
# це гарантована верхня межа горизонтальної похибки, у метрах.
# Допуск (HAL) задає поточна задача: для цього заходу — 40 м.
@dataclass
class Integrity:
    hpl_m: float
    hal_m: float

def position_trustworthy(ig: Integrity) -> bool:
    return ig.hpl_m <= ig.hal_m   # межа під допуском → довіряти можна

ig = Integrity(hpl_m=12.4, hal_m=40.0)
ok = position_trustworthy(ig)     # 12.4 ≤ 40.0 → True: використовувати

# Якби похмура іоносфера роздула межу:
ig.hpl_m = 47.0
ok = position_trustworthy(ig)     # 47.0 ≤ 40.0 → False: НЕ використовувати
