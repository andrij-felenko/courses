import math
from dataclasses import dataclass


# Параметри конкретного JFET (виміряні або з даташита).
@dataclass
class Jfet:
    idss: float   # струм насичення витоку, А (U_GS = 0)
    vp: float     # напруга відсічки, В — ВІД'ЄМНА (напр. −3.0)


def source_resistor(q: Jfet, i_target: float) -> float:
    """Опір резистора витоку для бажаного струму self-bias-джерела.

    Повертає R_S в омах, або −1, якщо струм недосяжний для цього JFET.
    i_target — бажаний струм, А (має бути 0 < i_target ≤ idss).
    """
    # Нижче за I_DSS опустити можна, вище — ні: за U_GS=0 уже тече
    # рівно I_DSS, а додатну U_GS на керівний перехід подавати не можна.
    if i_target <= 0.0 or i_target > q.idss:
        return -1.0

    # Точно I_DSS — це закорочений затвор: R_S = 0.
    if i_target == q.idss:
        return 0.0

    # Потрібна напруга затвор-витік за квадратичним законом:
    #   U_GS = U_P · (1 − sqrt(I_target / I_DSS))            (В, від'ємна)
    ugs = q.vp * (1.0 - math.sqrt(i_target / q.idss))

    # Резистор створює цю напругу падінням від струму:
    #   R_S = −U_GS / I_target                                (Ом)
    return -ugs / i_target
