import math
from dataclasses import dataclass

MU0 = 4e-7 * math.pi          # магнітна стала μ₀, Гн/м


# ── 1. Індуктивність петлі з геометрії ─────────────────────────────
@dataclass(frozen=True)
class Loop:
    """Силова петля як прямокутник: довжина туди-й-назад, просвіт, ширина."""
    length_mm: float          # ℓ — як далеко замикається петля
    gap_mm: float             # s — просвіт між прямим і зворотним шляхом
    width_mm: float           # w — ширина силової доріжки
    thick_um: float = 35.0    # товщина міді (1 унція ≈ 35 мкм)

    @property
    def area_mm2(self) -> float:
        return self.length_mm * self.gap_mm       # площа, яку охоплює петля

    def inductance_nH(self) -> float:
        # Два зустрічні провідники: L = (μ₀·ℓ/π)·ln(s/GMD).
        # GMD плоскої доріжки ≈ 0.2235·(w+t) — уже враховує внутрішній потік.
        w, t = self.width_mm * 1e-3, self.thick_um * 1e-6
        gmd = 0.2235 * (w + t)
        s, ell = self.gap_mm * 1e-3, self.length_mm * 1e-3
        ratio = max(s / gmd, 1.0)                  # s < GMD — провідники злиплися
        return (MU0 * ell / math.pi) * math.log(ratio) * 1e9


def overshoot_V(L_nH: float, di_A: float, dt_ns: float) -> float:
    """Викид на стоку при вимкненні: V = L·di/dt."""
    return (L_nH * 1e-9) * (di_A / (dt_ns * 1e-9))


# ── 2. Ширина силової доріжки за IPC-2221 ──────────────────────────
OZ_TO_MIL = 1.378             # 1 унція/фут² міді ≈ 1.378 mil ≈ 35 мкм

def ipc2221_width_mm(current_A: float, dT_C: float,
                     oz: float = 1.0, external: bool = True) -> float:
    """Ширина доріжки під заданий струм і приріст температури.
    Обертаємо I = k·ΔT^0.44·A^0.725 відносно площі перерізу, тоді ділимо
    на товщину міді. A — у квадратних мілях, як вимагає крива IPC."""
    k = 0.048 if external else 0.024
    area_mil2 = (current_A / (k * dT_C ** 0.44)) ** (1.0 / 0.725)
    width_mil = area_mil2 / (oz * OZ_TO_MIL)
    return width_mil * 0.0254                      # mil → мм


# ── 3. Тепловий опір полігону з via ────────────────────────────────
@dataclass(frozen=True)
class Thermal:
    """Насичувальна модель θ_JA(площа, via), підігнана під виміряні криві."""
    theta_jc: float = 1.5     # кристал → площадка, К/Вт (з даташита)
    theta0: float = 60.0      # гола площадка, край A → 0
    floor_1s: float = 40.0    # стеля з великою міддю, лише верхній бік
    floor_2s: float = 22.0    # ...коли via відкривають і нижній полігон
    knee_cm2: float = 1.0     # площа, на якій крива згинається (коліно)
    via_knee: float = 10.0    # скільки via дають половину виграшу від низу

    def theta_ja(self, area_cm2: float, n_via: int = 0) -> float:
        floor = self.floor_1s - (self.floor_1s - self.floor_2s) \
                * n_via / (n_via + self.via_knee)
        board = floor + (self.theta0 - floor) \
                * self.knee_cm2 / (area_cm2 + self.knee_cm2)
        return self.theta_jc + board


# ── Сценарій: 24 В, 10 А, вимкнення за 20 нс, ключ на 30 В ──────────
BUS, I, DI, DT = 24.0, 10.0, 10.0, 20.0
RON, DUTY, T_AMB, V_RATING = 8e-3, 1.0, 40.0, 30.0
P_cond = I * I * RON * DUTY                         # I²·Ron·D

print("── ПЕТЛЯ Й ВИКИД " + "─" * 40)
for tag, loop in [("недбала: конденсатор далеко", Loop(30.0, 2.0, 0.8)),
                  ("акуратна: конденсатор упритул", Loop(8.0, 0.5, 1.0))]:
    L = loop.inductance_nH()
    peak = BUS + overshoot_V(L, DI, DT)
    verdict = "OK" if peak <= V_RATING else "ПРОБІЙ"
    print(f"  {tag:32} площа {loop.area_mm2:5.1f} мм²  "
          f"L {L:5.1f} нГн  пік {peak:5.1f} В  [{verdict}]")

print("── ВАЖЕЛІ L: що насправді рухає індуктивність " + "─" * 12)
print(f"  базова 30/2.0/0.8 мм       : {Loop(30.0, 2.0, 0.8).inductance_nH():5.1f} нГн")
print(f"  довжина 30 → 10 мм (лінійно): {Loop(10.0, 2.0, 0.8).inductance_nH():5.1f} нГн")
print(f"  просвіт 2.0 → 0.5 мм (log)  : {Loop(30.0, 0.5, 0.8).inductance_nH():5.1f} нГн")
print(f"  ширина 0.8 → 3 мм (log)     : {Loop(30.0, 2.0, 3.0).inductance_nH():5.1f} нГн")

print("── ШИРИНА ДОРІЖКИ під 10 А (IPC-2221, зовнішній шар) " + "─" * 6)
for oz in (1.0, 2.0):
    for dT in (10.0, 20.0):
        print(f"  {oz:.0f} унц., ΔT {dT:.0f} °C : "
              f"{ipc2221_width_mm(I, dT, oz=oz):5.2f} мм")

print(f"── ПОЛІГОН І ГРАДУСИ (P = {P_cond:.2f} Вт, T_a = {T_AMB:.0f} °C) " + "─" * 8)
th = Thermal()
for A in (0.5, 1.0, 2.0, 4.0, 10.0):
    t0, tv = th.theta_ja(A, 0), th.theta_ja(A, 20)
    print(f"  {A:5.1f} см²:  без via θ {t0:4.1f} → T_j {T_AMB + P_cond*t0:5.1f} °C"
          f"   ·   20 via θ {tv:4.1f} → T_j {T_AMB + P_cond*tv:5.1f} °C")

print("── СПАД ВІДДАЧІ: що дає КОЖЕН доданий см² міді (без via) " + "─" * 3)
for a in range(6):
    gain = th.theta_ja(float(a), 0) - th.theta_ja(float(a + 1), 0)
    print(f"  {a} → {a+1} см² : {gain:+5.2f} К/Вт")
