# Усі ставки — у мілідоларах за годину (1 $ = 1000).
# Гроші — у мілідоларах. Цілі, щоб не тягнути float у рахунок.
# (Python має необмежені int — переповнення не загрожує.)

# ── Рахунок за період на РОЗДРІБІ: платимо лише за ввімкнені години ──────
# used_hours — реально ввімкнені години за період.
def retail_cost_md(retail_md_per_h: int, used_hours: int) -> int:
    return retail_md_per_h * used_hours


# ── Рахунок за період на ОБІЦЯНЦІ: платимо за ВСІ години строку ──────────
# period_hours — усього годин у періоді (місяць ≈ 720), байдуже до завантаження.
def committed_cost_md(committed_md_per_h: int, period_hours: int) -> int:
    return committed_md_per_h * period_hours
