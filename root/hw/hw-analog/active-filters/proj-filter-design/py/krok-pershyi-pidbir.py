import math
from dataclasses import dataclass

# Опис однієї ланки Саллена–Кі (ФНЧ, рівні резистори R1=R2=R).
@dataclass
class SKStage:
    R: float = 0.0      # спільний резистор, Ом
    C1: float = 0.0     # конденсатор додатного ЗЗ (верхній), Ф
    C2: float = 0.0     # конденсатор на землю (нижній), Ф
    f0: float = 0.0     # частота зрізу ланки, Гц
    Q: float = 0.0      # добротність ланки

# Підібрати ідеальні C1, C2 для заданих R, f0, Q.
# Заповнює s.C1, s.C2; R, f0, Q беруться з полів об'єкта.
def sk_pick_caps(s: SKStage) -> None:
    Cg = 1.0 / (2.0 * math.pi * s.R * s.f0)   # √(C1·C2)
    two_q = 2.0 * s.Q                          # √(C1/C2)
    s.C1 = Cg * two_q     # верхній — більший за Q>0.5
    s.C2 = Cg / two_q     # нижній  — менший
