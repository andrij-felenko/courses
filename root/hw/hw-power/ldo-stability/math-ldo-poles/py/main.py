import math

# ── Мала-сигнальна петля LDO: два полюси + нуль ESR ─────────────────
VT     = 0.02585         # тепловий потенціал при 27 °C, В
N_SUB  = 1.3             # коефіцієнт нахилу підпорогової ділянки
V_OUT  = 3.3             # напруга виходу, В
V_REF  = 1.2             # опорна напруга, В
BETA   = V_REF / V_OUT   # частка виходу, що вертається в петлю
A_EA   = 200.0           # підсилення підсилювача похибки (його власне gm·R)
R_EA   = 200e3           # вихідний опір підсилювача похибки, Ом
C_G    = 20e-12          # ємність затвора прохідного транзистора, Ф
C_OUT  = 1e-6            # вихідний конденсатор, Ф

F_P2 = 1 / (2 * math.pi * R_EA * C_G)   # полюс вузла A — від струму не залежить


def gm_pass(i_load, v_ov_full=0.4, i_full=0.5):
    """Крутість прохідного PMOS у робочій точці i_load.
    Сильна інверсія: gm = 2·I/Vнад = √(2·k·I). Слабка: gm = I/(n·VT) — стеля."""
    k = 2 * i_full / v_ov_full ** 2              # параметр приладу, А/В²
    return min(math.sqrt(2 * k * i_load),        # квадратичний закон
               i_load / (N_SUB * VT))            # підпорогова стеля


def loop(f, i_load, esr):
    """Підсилення петлі на частоті f: (модуль, фаза в градусах)."""
    r_out = V_OUT / i_load                       # опір вузла виходу ≈ опір навантаження
    f_p1  = 1 / (2 * math.pi * r_out * C_OUT)    # полюс виходу
    f_z   = 1 / (2 * math.pi * esr * C_OUT)      # нуль ESR
    t0    = A_EA * gm_pass(i_load) * r_out * BETA
    mag = t0 * math.hypot(1, f / f_z) / (math.hypot(1, f / f_p1) * math.hypot(1, f / F_P2))
    deg = math.degrees(math.atan(f / f_z) - math.atan(f / f_p1) - math.atan(f / F_P2))
    return mag, deg


def crossover(i_load, esr):
    """Частота зрізу — де модуль петлі падає до одиниці (ділення навпіл по логарифму)."""
    lo, hi = 1.0, 1e9
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if loop(mid, i_load, esr)[0] > 1.0:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


I = 1e-3                                          # найтяжчий кут: легке навантаження
for name, esr in [("тантал", 1.0), ("кераміка", 0.005)]:
    f_c = crossover(I, esr)
    print("%s: ESR=%5.3f Ом, нуль=%8.1f кГц, зріз=%6.1f кГц, запас фази=%4.1f°"
          % (name, esr, 1 / (2 * math.pi * esr * C_OUT) / 1e3, f_c / 1e3,
             180 + loop(f_c, I, esr)[1]))

# тантал:   ESR=1.000 Ом, нуль=   159.2 кГц, зріз= 130.1 кГц, запас фази=56.3°
# кераміка: ESR=0.005 Ом, нуль= 31831.0 кГц, зріз= 113.7 кГц, запас фази=19.5°
