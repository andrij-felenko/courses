# power_monitor.py (продовження)

def pm_init(cfg: PmConfig) -> PmChannel:
    # Створити свіжий канал: доки не доведено погане — вважаємо норму (PM_OK).
    return PmChannel(cfg=cfg)   # решта полів — за замовчуванням (буфер нулів тощо)

# Сирий код АЦП → напруга шини в мілівольтах, з урахуванням дільника.
# Порядок множень навмисний: спершу *vref, тоді дільник — щоб не втратити
# точність на цілих (Python int безмежний, тож переповнення тут не боїмось).
def _code_to_bus_mv(c: PmConfig, code: int) -> int:
    v_adc = code * c.vref_mv // c.adc_full     # напруга на нозі
    v_bus = v_adc * c.div_num // c.div_den     # назад до шини
    return min(v_bus, 0xFFFF)

# Кільцевий буфер: один новий відлік за виклик, миттєве середнє по 8.
def _ring_avg(ch: PmChannel, code: int) -> int:
    ch._sum -= ch._buf[ch._head]
    ch._buf[ch._head] = code
    ch._sum += code
    ch._head = (ch._head + 1) & 7               # & 7 == % 8 (степінь двійки)
    if ch._count < 8:
        ch._count += 1
    return ch._sum // ch._count
