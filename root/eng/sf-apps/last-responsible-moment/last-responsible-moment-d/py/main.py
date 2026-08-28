from dataclasses import dataclass

@dataclass
class Deferral:
    carry_per_week: float   # c — накладні за тиждень тримання відкритим
    weeks_to_lrm: float     # t* — коли настане відповідальний момент
    reversal_cost: float    # C_r — ціна відкоту хибного вибору
    wrong_now: float        # p(0) — ймовірність хибитися, обравши зараз
    wrong_at_lrm: float     # p(t*) — ймовірність хибитися на моменті

def cost_of_deferring(d: Deferral) -> float:
    return d.carry_per_week * d.weeks_to_lrm + d.wrong_at_lrm * d.reversal_cost

def cost_of_seam_now(d: Deferral, seam: float, reduced: float) -> float:
    return seam + d.wrong_now * reduced

def verdict(d: Deferral, seam: float, reduced: float) -> str:
    defer = cost_of_deferring(d)
    now = cost_of_seam_now(d, seam, reduced)
    if now < defer:
        return f"Зроби оборотним і обирай зараз ({now:.0f} < {defer:.0f})"
    return f"Відкладай до моменту ({defer:.0f} < {now:.0f})"
