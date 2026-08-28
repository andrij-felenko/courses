def pm_poll(ch: PmChannel, read: ReadAdc, act: PmActions) -> None:
    c = ch.cfg

    code = read()                      # один сирий відлік
    avg = _ring_avg(ch, code)          # усереднений код
    ch.bus_mv = _code_to_bus_mv(c, avg)  # напруга шини, мВ

    want = _classify(c, ch.bus_mv, ch.st)

    # Підтвердження серією: різні класи мають різну «терплячість».
    # OK — це «добре», будь-яка аварія — «погано».
    if want == PmClass.OK:
        ch.bad_run = 0
        if ch.good_run < 0xFF:
            ch.good_run += 1
    else:
        ch.good_run = 0
        if ch.bad_run < 0xFF:
            ch.bad_run += 1

    # Скільки підтверджень треба саме для ЦЬОГО переходу.
    if want == PmClass.DEAD:
        need = c.confirm_dead          # мертву ловимо швидко
    elif want == PmClass.BODYDIODE:
        need = c.confirm_dead          # так само швидко
    elif want == PmClass.SAG:
        need = c.confirm_sag           # просад — терплячіше
    else:
        need = c.confirm_ok            # назад у норму — нехотя

    # Перехід стається лише коли серія добігла потрібної довжини
    # І новий клас відрізняється від поточного.
    enough = ch.good_run >= need if want == PmClass.OK else ch.bad_run >= need
    if not enough or want == ch.st:
        return                         # ще не впевнені або нема зміни

    # ── ПЕРЕХІД: тут і тільки тут смикаємо реакції ──────────────────────────
    ch.st = want

    if want != PmClass.OK:
        # Входимо в будь-яку аварію: спершу — рятуємо, тоді роз'єднуємо.
        ch.flag_latched = True         # липкий прапорець для сервісу
        if act.save_state:
            act.save_state()           # поки є заряд у C
        if act.set_load:
            act.set_load(False)        # зняти навантаження
    else:
        # Повертаємось у норму з аварії: знову дозволяємо навантаження.
        if act.set_load:
            act.set_load(True)
    if act.on_class:
        act.on_class(want)             # індикація/лог завжди


def pm_class(ch: PmChannel) -> PmClass:      return ch.st
def pm_bus_mv(ch: PmChannel) -> int:         return ch.bus_mv
def pm_fault_latched(ch: PmChannel) -> bool: return ch.flag_latched
