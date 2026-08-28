import math
from dataclasses import dataclass

# ── Фіксований операційний податок на КОЖЕН окремо-розгортуваний сервіс ──────
#    (інженер-години на місяць, НЕ залежать від трафіку — беруться завжди)
PIPELINE, DASHBRD, ONCALL, PATCHING = 6, 5, 8, 5      # конвеєр · дашборди · чергування · патчі
OPS_PER_SVC = PIPELINE + DASHBRD + ONCALL + PATCHING  # = 24 год/сервіс/міс
TEAM_HOURS  = 6 * 160                                  # 6 інженерів × 160 продуктивних год

Z99 = 2.326    # 99-й перцентиль стандартної нормалі


@dataclass
class Hop:
    p50: float   # медіана затримки стрибка, мс
    p99: float   # 99-й перцентиль стрибка, мс
    fail: float  # ймовірність твердої відмови (таймаут / половинчаста відповідь)


NET = Hop(1.0, 15.0, 0.002)      # один RPC-стрибок усередині датацентру
MEM = Hop(0.002, 0.002, 0.0)     # виклик у пам'яті ≈ 2 мкс; вертає або кидає, одна транзакція


@dataclass
class Arch:
    name: str
    services: int    # окремо-розгортуваних одиниць
    hot: list        # стрибки «показати стан дому»: ідентичність → твін → керування


def ops_surface(a):
    """Скільки годин на місяць архітектура з'їдає операційкою — до першої фічі."""
    return a.services * OPS_PER_SVC


def _lognorm(h):
    """Логнормаль ln X ~ N(μ, σ), підігнана під (p50, p99) стрибка."""
    mu = math.log(h.p50)
    sigma = math.log(h.p99 / h.p50) / Z99 if h.p99 > h.p50 else 0.0   # 0 для виклику в пам'яті
    return mu, sigma


def path_latency(a):
    """p50 і p99 УСЬОГО шляху = сума незалежних стрибків. Фентон–Вілкінсон:
    наблизити суму логнормалей однією, що збігається за середнім і дисперсією.
    Середні ДОДАЮТЬСЯ; дисперсії ДОДАЮТЬСЯ; а хвіст — ні."""
    M = V = 0.0
    for h in a.hot:
        mu, s = _lognorm(h)
        m = math.exp(mu + s * s / 2)                            # середнє стрибка
        v = (math.exp(s * s) - 1) * math.exp(2 * mu + s * s)    # дисперсія стрибка
        M += m
        V += v
    if M == 0:
        return 0.0, 0.0
    sig2 = math.log(1 + V / (M * M))       # σ² підігнаної суми: росте як корінь, не лінійно
    mu_s = math.log(M) - sig2 / 2
    s = math.sqrt(sig2)
    return math.exp(mu_s), math.exp(mu_s + Z99 * s)             # p50, p99


def path_avail(a):
    """Шанс, що весь шлях повернувся чисто = добуток успіхів на кожному стрибку."""
    p = 1.0
    for h in a.hot:
        p *= (1 - h.fail)
    return p


def new_failure_modes(a):
    return sum(1 for h in a.hot if h.fail > 0)


def fmt_ms(x):
    return f"{x * 1000:.0f} мкс" if x < 1 else f"{x:.1f} мс"


# ── Три архітектури на тому самому гарячому шляху ───────────────────────────
mono    = Arch("моноліт (1 деплой)",         1, [MEM, MEM, MEM])
full    = Arch("повний розкол (9)",          9, [NET, NET, NET])
partial = Arch("моноліт + телеметрія (2)",   2, [MEM, MEM, MEM])

print("=== Податок на мікросервіс: DH, 2000 домів / 40 000 пристроїв ===\n")
print(f"{'архітектура':26}{'сервісів':>9}{'ops·год/міс':>13}{'команда':>10}"
      f"{'p50':>8}{'p99':>9}{'доступність':>13}{'+відмов':>9}")
for a in (mono, full, partial):
    p50, p99 = path_latency(a)
    print(f"{a.name:26}{a.services:>9}{ops_surface(a):>13}"
          f"{ops_surface(a) / TEAM_HOURS:>9.0%}{fmt_ms(p50):>8}{fmt_ms(p99):>9}"
          f"{path_avail(a):>12.3%}{new_failure_modes(a):>9}")

p50f, p99f = path_latency(full)
print(f"\nхвіст гарячого шляху (3 стрибки поспіль):")
print(f"  один стрибок:            p50 = {NET.p50:.0f} мс   p99 = {NET.p99:.0f} мс")
print(f"  якби хвіст додавався лінійно: 3 × 15 = {3 * NET.p99:.0f} мс")
print(f"  насправді (сума хвостів):  p50 = {p50f:.1f} мс   p99 = {p99f:.1f} мс")
print(f"  → p99 шляху = {p99f / NET.p99:.2f}× p99 одного стрибка, але {p99f / p50f:.2f}× власної медіани")
miss = 1 - path_avail(full)
print(f"  доступність {path_avail(full):.3%} → {miss:.3%} читань чіпляють ≥1 відмову")
print(f"    (~{50_000 * miss:.0f} збоїв на 50 000 читань/добу проти 0 у моноліті)")

# ── Крива окупності: коли ВЛАСНИЙ драйвер контексту переважує частку премії ──
ENG_HOUR = 80                              # $ за інженер-годину, повністю навантажена
PREMIUM  = OPS_PER_SVC * ENG_HOUR          # $ на місяць — чиста операційка одного сервісу
C_FULL   = 350                             # $/міс, одна ПОВНА репліка моноліта (усі модулі в пам'яті)
C_SLICE  = 110                             # $/міс, одна ТОНКА репліка одного контексту


def worth_split(peak_replicas):
    """Пік контексту вимагає peak_replicas додаткових одиниць потужності.
    У моноліті кожна одиниця — повна репліка; винесеш — тонка + фіксована премія."""
    keep  = peak_replicas * C_FULL
    split = PREMIUM + peak_replicas * C_SLICE
    return split < keep, keep, split


def breakeven_replicas():
    return PREMIUM / (C_FULL - C_SLICE)     # премія, виражена в повних репліках


print(f"\nкрива окупності (виносити, коли власний драйвер > частки премії):")
print(f"  премія сервісу = ${PREMIUM}/міс   поріг = {breakeven_replicas():.1f} повних реплік")
print(f"  {'контекст':26}{'драйвер':>8}{'тримати':>10}{'винести':>10}{'вердикт':>11}")
CONTEXTS = [("телеметрія (запис 40k)", 12), ("твін", 1), ("керування", 1),
            ("ідентичність", 0), ("білінг", 0)]
for name, u in CONTEXTS:
    ok, keep, split = worth_split(u)
    print(f"  {name:26}{u:>8}{'$' + str(keep):>10}{'$' + str(split):>10}"
          f"{'ВИНОСИТИ' if ok else 'тримати':>11}")
