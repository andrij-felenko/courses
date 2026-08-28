# Спроєктувати весь фільтр заданого типу під частоту зрізу fc і резистор R.
# Повертає список готових ланок (кожна — з власними C1, C2, фактичними f0, Q).
def sk_design_filter(ft: SKFilterType, fc: float, R: float) -> list[SKStage]:
    out = []
    for rec in ft.stage:
        s = SKStage(R=R, f0=fc * rec.fmul, Q=rec.Q)  # частота і Q ЦІЄЇ ланки
        sk_design(s)                                  # ідеал → E12 → фактичні
        out.append(s)
    return out

# Друк підсумку: що замовляли і що вийшло.
def sk_report(ft: SKFilterType, fc: float, st: list[SKStage]) -> None:
    print(f"Фільтр: {ft.name}, зріз {fc:.0f} Гц")
    for i, s in enumerate(st, start=1):
        print(f"  ланка {i}: R={s.R:.0f}  C1={s.C1 * 1e9:.1f} нФ  "
              f"C2={s.C2 * 1e9:.1f} нФ  ->  f0={s.f0:.0f} Гц  Q={s.Q:.3f}")
