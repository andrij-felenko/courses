import math

# ── Тарифи керованого брокера (AWS IoT Core, US-East, 2025) ─────────────────
PRICE_PER_M_MSG      = 1.00      # $ за млн повідомлень (при обсязі падає до ~0.70)
PRICE_PER_M_CONN_MIN = 0.08      # $ за млн хвилин з'єднання
MSG_PER_HOME_MONTH   = 86_400    # 1 повідомл./30 с → 2 880/добу → 86 400/міс
CONN_MIN_PER_MONTH   = 43_200    # 30 діб × 1 440 хв, з'єднання тримається завжди

# ── Своє: разова побудова + вічний хвіст ────────────────────────────────────
ENG_MONTH_USD    = 12_500        # повна вартість інженер-місяця (з накладними)
BUILD_USD        = ENG_MONTH_USD * 12          # 2 інж. × 6 міс = $150 000 до v1
SECURITY_MONTH   = 2_500         # аудити, пентести, керування секретами
INFRA_PER_HOME   = 0.01          # свої сервери + резерв + трафік, на дім/міс


def managed_monthly(homes):
    """Рахунок за керований брокер — лінійний із трафіком."""
    msgs = homes * MSG_PER_HOME_MONTH
    conn = homes * CONN_MIN_PER_MONTH
    return msgs / 1e6 * PRICE_PER_M_MSG + conn / 1e6 * PRICE_PER_M_CONN_MIN


def ops_fte(homes):
    """Скільки інженерів тримають брокер живим 24/7. Щедро занижено: гайд
    Google SRE радить від ~8 на майданчик для сталого чергування, ми беремо від 2."""
    return max(2.0, 2.0 + 2.0 * math.log10(homes / 10_000))


def own_monthly(homes):
    """Своє БЕЗ разової побудови: люди + залізо + безпека."""
    return ops_fte(homes) * ENG_MONTH_USD + INFRA_PER_HOME * homes + SECURITY_MONTH


def own_tco(homes, months):
    """Повна вартість володіння: разова побудова + хвіст за N місяців."""
    return BUILD_USD + own_monthly(homes) * months


def breakeven_homes(months=None):
    """Найменший масштаб, де своє дешевше. months=None → сталий місячний режим."""
    own = (lambda h: own_tco(h, months)) if months else own_monthly
    buy = lambda h: managed_monthly(h) * (months or 1)
    lo, hi = 1_000.0, 100_000_000.0
    for _ in range(60):                     # двійковий пошук по геом. середині
        mid = math.sqrt(lo * hi)            # (вісь масштабу логарифмічна)
        lo, hi = (mid, hi) if own(mid) > buy(mid) else (lo, mid)
    return math.sqrt(lo * hi)


def grp(x):                                # тисячі — пробілом, як прийнято
    return f"{x:,.0f}".replace(",", " ")

SCEN = [5_000, 50_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
print(f"{'домів':>11}  {'повід./с':>8}  {'куплене/міс':>12}  {'своє/міс':>10}  дешевше")
for n in SCEN:
    buy, own = managed_monthly(n), own_monthly(n)
    print(f"{grp(n):>11}  {grp(n / 30):>8}  {grp(buy) + '$':>12}  {grp(own) + '$':>10}  "
          f"{'СВОЄ' if own < buy else 'куплене'}")

be_now = breakeven_homes()
print(f"\nперетин, сталий місяць:      {grp(be_now)} домів")
print(f"перетин, володіння 36 міс:   {grp(breakeven_homes(36))} домів")
print(f"DH сьогодні 5 000 → до перетину ще ~{be_now / 5_000:.0f}×")
