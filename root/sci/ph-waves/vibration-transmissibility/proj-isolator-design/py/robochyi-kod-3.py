@dataclass
class Design:
    exc_hz: float          # частота трясіння, Гц
    mass_kg: float
    target_T: float
    zeta: float
    r_work: float          # робоче відношення частот f/fₙ
    fn_hz: float           # потрібна власна частота
    k_total: float         # сумарна жорсткість опори, Н/м
    defl_mm: float         # статичний прогин під вагою
    isolation_pct: float   # 100·(1−T) на робочій частоті
    peak_r: float          # де резонанс на розгоні
    peak_T: float          # у скільки разів підсилює на піку
    peak_rpm: float        # оберти, за яких проходить резонанс


def design_mount(mass_kg, target_T, zeta, *, exc_hz=None, rpm=None, order=1.0):
    """Підібрати опору за частотою трясіння (чи об/хв), масою, ціллю T і ζ."""
    if exc_hz is None:
        if rpm is None:
            raise ValueError("задай exc_hz або rpm")
        exc_hz = rpm / 60.0 * order
    r = ratio_for_target(target_T, zeta)
    fn = exc_hz / r
    wn = 2.0 * pi * fn
    k = wn * wn * mass_kg
    defl_mm = 1000.0 * G / (wn * wn)         # δ = g/ωₙ²
    pr, pt = resonance_peak(zeta)
    peak_rpm = fn * pr * 60.0 / order         # де f = fₙ·r_peak
    return Design(exc_hz, mass_kg, target_T, zeta, r, fn, k,
                  defl_mm, 100.0 * (1.0 - target_T), pr, pt, peak_rpm)
