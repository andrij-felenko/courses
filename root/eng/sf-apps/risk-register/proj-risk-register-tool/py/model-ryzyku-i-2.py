REGISTER = [
    Risk("R1", "Vendor-API відмовить під піком", 0.30, 500_000,
         "p95 latency > 800 мс",       "Оля",   State.MITIGATING),
    Risk("R2", "Витік через невчасний патч",     0.10, 800_000,
         "CVE у прямій залежності",     "Тарас", State.WATCHED),
    Risk("R3", "Ключова людина звільниться",     0.20, 300_000,
         "вигорання видно на 1:1",      "Ліда",  State.OPEN),
    Risk("R4", "Схема бази застигне",            0.25, 120_000,
         "міграція триває > 2 год",     "Оля",   State.OPEN),
    Risk("R0", "Стара інтеграція впаде",         0.40, 200_000,
         "—",                           "Тарас", State.CLOSED),  # закритий!
]

def rank(reg: list[Risk]) -> None:
    live = [r for r in reg if r.state not in DEAD]
    for r in sorted(live, key=exposure, reverse=True):
        print(f"  {r.id}  {r.desc:30.30}  p={r.p:.2f}  L={r.L:>8.0f}"
              f"  →  {exposure(r):>8.0f}  [{r.owner}]")
    print(f"  Σ портфеля (активні рядки) = {portfolio(reg):.0f}")

rank(REGISTER)
