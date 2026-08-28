from dataclasses import dataclass

# ── шкала гарантій: множник податку відносно повної (лінеаризовної) строгості ──
# нелінійна ціна зі спектра: сесійна ~8% повної, причинна ~30%, лінеаризовність — 100%
FACTOR = {"кінцева": 0.0, "сесійна": 0.08, "причинна": 0.30, "лінеаризовність": 1.0}

# яку НАЙСЛАБШУ гарантію вимагає кожен рід аномалії
NEEDS = {
    "самолікується": "кінцева",          # відстало й само вирівнялось — прибирати нема чого
    "свій-запис":    "сесійна",          # read-your-writes: бачити власну зміну одразу
    "причинний-лад": "причинна",         # наслідок не випереджає причину
    "єдиний-лад":    "лінеаризовність",  # безпека / гроші: один глобальний порядок
}

# грубі ціни координації — тюнери під свій бізнес
LAT_EUR_PER_S = 0.5    # € за секунду сукупного доданого чекання, накопиченого за секунду
MSG_EUR       = 0.02   # € за одне крос-регіон-повідомлення координації

@dataclass
class Item:
    name: str
    p_anom: float      # P(аномалія) на одну операцію
    harm_eur: float    # шкода однієї аномалії, €
    ops_s: float       # операцій/сек (обсяг)
    rtt_ms: float      # крос-регіон RTT, мс
    replicas: int      # скільки реплік координувати
    anomaly: str       # рід неконсистентності, що тут болить

def harm_per_s(it: Item) -> float:
    "Очікувана шкода неконсистентності за секунду: P · шкода · обсяг."
    return it.p_anom * it.harm_eur * it.ops_s

def full_tax_per_s(it: Item) -> float:
    "Податок координації за секунду при ПОВНІЙ строгості: затримка·обсяг + трафік."
    latency = (it.rtt_ms / 1000) * it.ops_s * LAT_EUR_PER_S
    traffic = it.ops_s * (it.replicas - 1) * MSG_EUR
    return latency + traffic

def verdict(it: Item, hot_harm=1000.0, hot_tax=100.0) -> dict:
    harm = harm_per_s(it)
    full = full_tax_per_s(it)
    need = NEEDS[it.anomaly]
    fix_tax = full * FACTOR[need]                     # податок ЩАБЛЯ, що прибирає аномалію
    score = harm / full if full else float("inf")     # «тиск»: ліва частина ÷ права

    if need == "кінцева":
        call = "кінцева"
        why = "аномалія самолікується — координувати нема чого"
    elif fix_tax < harm:
        call = f"тримати строго: {need}"              # найслабший щабель, що окупається
        why = f"{need} коштує {fix_tax:.1f} €/с < шкода {harm:.0f} €/с"
    else:
        call = "терпіти / змінити гру"                # навіть потрібний щабель дорожчий за шкоду
        why = f"навіть {need} ({fix_tax:.1f} €/с) дорожча за шкоду {harm:.0f} €/с"

    hot = harm > hot_harm and fix_tax > hot_tax
    return dict(name=it.name, harm_s=harm, full_tax_s=full,
                score=score, call=call, why=why, hot=hot)

def rank(items: list[Item]) -> list[dict]:
    return sorted((verdict(it) for it in items), key=lambda r: r["score"], reverse=True)

# ── дані Digital Homes ──
DH = [
    Item("замок дверей",      0.005, 800.0,        8,   90, 3, "єдиний-лад"),
    Item("білінг (підсумок)", 0.01,  200.0,     2000,   90, 5, "єдиний-лад"),
    Item("твін: обігрівач",   0.08,    0.5,     3000,   90, 3, "свій-запис"),
    Item("presence «онлайн»", 0.15,    0.002,  50000,   90, 3, "самолікується"),
    Item("телеметрія",        0.20,    0.00005, 500000, 90, 3, "самолікується"),
]

print(f"{'дані DH':20}{'шкода €/с':>11}{'повний под. €/с':>16}{'тиск':>7}  вердикт")
print("-" * 74)
for r in rank(DH):
    flag = "   🔥 звузити зону" if r["hot"] else ""
    print(f"{r['name']:20}{r['harm_s']:>11.1f}{r['full_tax_s']:>16.0f}{r['score']:>7.2f}  {r['call']}{flag}")
    print(f"{'':20}  └ {r['why']}")
