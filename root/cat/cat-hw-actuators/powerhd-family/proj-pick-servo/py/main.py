# Підбір хобі-серва за навантаженням: чи вистачить моменту із запасом.
# Момент = сила · плече (кг·см); паспорт зводимо до робочої напруги
# й ділимо на derate (=2) — поправка на оптимістичний паспорт і розкид.

from dataclasses import dataclass, field


@dataclass
class Servo:
    name: str
    spec: list[tuple[float, float]]   # точки (напруга, момент кг·см)
    work_volts: float                 # напруга, якою реально живимо


@dataclass
class Load:
    force_kgf: float                  # сила на тязі, кгс (важкий випадок)
    arm_cm: float                     # плече рога від осі вала, см
    safety: float = 2.0               # запас на навантаження
    derate: float = 2.0               # ділник паспорта серва


def torque_at(spec, volts):
    """Лінійна інтерполяція паспорта на робочу напругу; за межами — не
    екстраполюємо оптимістично, а затискаємо крайньою точкою."""
    pts = sorted(spec)
    if len(pts) == 1:
        return pts[0][1]
    lo, hi = pts[0], pts[-1]
    v = max(lo[0], min(hi[0], volts))
    for (va, ta), (vb, tb) in zip(pts, pts[1:]):
        if va <= v <= vb:
            t = (v - va) / (vb - va)
            return ta + t * (tb - ta)
    return hi[1]


def pick_servo(load: Load, servo: Servo) -> dict:
    needed = load.force_kgf * load.arm_cm      # потрібний момент
    target = needed * load.safety              # з запасом на навантаження
    paper = torque_at(servo.spec, servo.work_volts)
    usable = paper / load.derate               # на що реально кладемось
    return {
        "needed_kgcm": round(needed, 2),
        "target_kgcm": round(target, 2),
        "paper_kgcm": round(paper, 2),
        "usable_kgcm": round(usable, 2),
        "ok": usable >= target,
        "margin": round(usable / target, 2),   # фактичний запас понад ціль
    }


# --- застосування: кермо машинки 1:10 на розі LF-20MG, живлення 6 В ---
lf20mg = Servo("Power HD LF-20MG",
               spec=[(4.8, 16.5), (6.6, 20.0)], work_volts=6.0)
steering = Load(force_kgf=2.5, arm_cm=1.5)

print(pick_servo(steering, lf20mg))
# {'needed_kgcm': 3.75, 'target_kgcm': 7.5, 'paper_kgcm': 18.83,
#  'usable_kgcm': 9.42, 'ok': True, 'margin': 1.26}
# потрібно 7.5 з запасом; реально доступно ~9.4 → проходить, ще й з запасом ×1.26
