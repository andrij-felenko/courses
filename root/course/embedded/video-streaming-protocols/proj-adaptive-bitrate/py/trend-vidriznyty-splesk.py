from dataclasses import dataclass, field

@dataclass
class AbrTrend:
    base: Abr                    # контролер із гістерезисом (вище)
    loss_avg: int = 0            # згладжені втрати, ‰  (EMA)
    jitter_avg: int = 0          # згладжений джитер (одиниці RTP timestamp)
    alpha_pct: int = 25          # вага нового звіту в EMA, %  (напр., 25 → α=0.25)
    seeded: bool = False         # False до першого звіту: EMA треба засіяти, не зростати з нуля


def abr_trend_init(start: int, lo: int, hi: int) -> AbrTrend:
    # α = 0.25: розумний баланс глушіння й чуйності;
    # перший звіт сяде в середнє цілком, без розгону з 0
    return AbrTrend(base=abr_init(start, lo, hi), alpha_pct=25)


# EMA в цілій арифметиці:  avg += α·(нове − avg)
def _ema(avg: int, sample: int, alpha_pct: int) -> int:
    return avg + (sample - avg) * alpha_pct // 100


def abr_trend_on_report(t: AbrTrend, fraction_lost: int, jitter: int) -> int:
    loss = (fraction_lost * 1000) >> 8

    # 0) перший звіт сяде в середнє ЦІЛКОМ — інакше EMA повзла б від нуля
    #    кілька звітів і пропустила б ранній стан каналу
    if not t.seeded:
        t.loss_avg   = loss
        t.jitter_avg = jitter
        t.seeded     = True

    # 1) згладжуємо обидва датчики — гасимо одиничні сплески
    t.loss_avg   = _ema(t.loss_avg, loss, t.alpha_pct)
    # джитер згладимо тим самим правилом
    t.jitter_avg = _ema(t.jitter_avg, jitter, t.alpha_pct)

    # 2) РАННЄ ПОПЕРЕДЖЕННЯ за джитером: він росте швидко, а втрат ще нема —
    #    канал ось-ось захлинеться. Не піднімаємось, навіть якщо втрати малі.
    jitter_rising = jitter > t.jitter_avg * 3 // 2

    if jitter_rising and t.loss_avg < t.base.loss_up_permille:
        # притримуємо ріст: пропускаємо крок угору, лишаємо бітрейт як є
        return t.base.rate

    # 3) рішення — на ЗГЛАДЖЕНИХ втратах, не на сирих.
    #    переводимо ‰ (0..1000) назад у формат RR (0..255) і затискаємо стелею:
    f255 = (t.loss_avg << 8) // 1000        # ‰ → 0..256
    f255 = min(f255, 255)                    # 100% не має дати 0!
    return abr_on_report(t.base, f255)
