# ── Поріг завантаження В ГОДИНАХ: скільки годин/період машина має ────────
# пропрацювати, щоб обіцянка зрівнялася з роздробом.
#   рівність:  retail·H_used = committed·H_period
#     →  H_used = committed·H_period / retail
def breakeven_hours(committed_md_per_h: int, retail_md_per_h: int,
                    period_hours: int) -> int:
    # множимо ДО ділення й беремо цілочислове // — інакше втратимо ціле
    num = committed_md_per_h * period_hours
    return num // retail_md_per_h


# ── Порада: чи варто обіцянка при очікуваному завантаженні? ──────────────
# expected_used — скільки годин/період машина реально працюватиме.
def commitment_pays(committed_md_per_h: int, retail_md_per_h: int,
                    period_hours: int, expected_used: int) -> bool:
    return expected_used >= breakeven_hours(committed_md_per_h,
                                            retail_md_per_h, period_hours)
