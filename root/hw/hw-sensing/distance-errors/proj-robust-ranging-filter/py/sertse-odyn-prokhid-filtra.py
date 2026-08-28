def rf_update(f: RangeFilter, s: Sample) -> RangeResult:
    r = RangeResult(status=RangeStatus.FRESH)

    # 0. Пропуск (dropout): нема відлуння або сигнал нижче підлоги довіри.
    if not s.valid or s.strength < f.floor:
        f.drops += 1
        if f.have_est and f.drops <= f.max_drops:   # коротка сліпота —
            r.status = RangeStatus.HELD             # тримаємо останнє відоме
            r.mm = r.med_mm = int(f.est + 0.5)
            return r
        f.have_last = False          # довга сліпота — рвемо опору воріт
        r.status = RangeStatus.LOST  # і чесно кажемо «не знаю»
        r.mm = r.med_mm = 0
        return r                     # для уникання зіткнень це НЕБЕЗПЕКА, не «вільно»
    f.drops = 0

    # 1. Медіана-3 у кільцевому буфері — вбити поодинокий викид.
    f.ring[f.head] = s.dist_mm
    f.head = (f.head + 1) % 3
    if f.fill < 3:
        f.fill += 1
    med = median3(*f.ring) if f.fill == 3 else s.dist_mm   # поки буфер не повний — беремо як є

    # 2. Ворота швидкості: за Δt ціль не могла зрушити більш ніж на v_макс·Δt.
    if f.have_last:
        dt   = (s.t_ms - f.last_ms) & 0xFFFFFFFF   # маска uint32 коректна й на перевороті лічильника мс
        dmax = f.vmax_mm_s * dt // 1000 + f.margin_mm
        jump = abs(med - f.last_mm)
        if jump > dmax:
            f.rejects += 1
            if f.rejects <= f.max_rejects:   # фізично неможливий стрибок — викид
                r.status = RangeStatus.HELD
                r.mm = r.med_mm = int(f.est + 0.5)
                return r
            f.est = med   # стільки «неможливих» поспіль — це вже реальна зміна світу
        #                 # (або ми застрягли на привиді): пере-захоплюємо
    f.rejects = 0

    # 3. Довіра за силою відлуння → вага [0..1].
    conf = confidence(s.strength, f.floor, f.full)

    # 4. Зважене злиття: крок до медіани пропорційний довірі.
    if not f.have_est:
        f.est = med
        f.have_est = True
    else:
        alpha = f.base_alpha * conf     # кволий сигнал → майже не рухаємо оцінку
        f.est += alpha * (med - f.est)

    f.last_mm = med
    f.last_ms = s.t_ms
    f.have_last = True

    r.status = RangeStatus.FRESH
    r.conf   = conf
    r.med_mm = med                  # крайо-зберігаючий вихід — для безпеки
    r.mm     = int(f.est + 0.5)     # згладжений за довірою — для показу
    return r


def rf_init(vmax_mm_s: int, floor: int, full: int) -> RangeFilter:
    # найгірша швидкість ЗБЛИЖЕННЯ (не лише ваша); floor — нижче dropout; full — вище повна довіра.
    # margin_mm=15, base_alpha=0.6, max_drops=3, max_rejects=4 — з типових значень RangeFilter
    return RangeFilter(vmax_mm_s=vmax_mm_s, floor=floor, full=full)
