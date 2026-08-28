# Один такт бек-енду. Приймає свіжі сирі цифри raw[0..NSTAGE-1] і 2-бітний хвіст final2.
# Коли конвеєр наповнився — повертає (True, зібраний код відліку, що зайшов LAT тактів тому).
# Інакше повертає (False, 0) — конвеєр ще наповнюється.
def be_step(b, raw, final2):
    L = NSTAGE                                     # довжина кільця

    for s in range(NSTAGE):                        # (1) записати свіжі цифри
        b.line[s][b.wr] = raw[s] & 0x3             #     (лише 2 біти цифри)
    b.fin[b.wr] = final2 & 0x3

    valid = (b.filled >= LAT)                       # конвеєр наповнився?
    code = 0
    if valid:                                       # (2) вирівняти й скласти
        for s in range(NSTAGE):
            delay = LAT - s                         # щабель 0 → 5 тактів, … щабель 5 → 0
            idx   = (b.wr - delay) % L              # зчитати з глибини кільця
            d = b.line[s][idx]                      # цифра цього щабля для ОДНОГО відліку
            code += d << ((NBITS - 2) - s)          # вага: 6,5,4,3,2,1 — зсув на 1 розряд/щабель
        code += b.fin[b.wr]                         # хвіст-flash у два молодші розряди
        max_code = (1 << NBITS) - 1
        if code > max_code:
            code = max_code                         # страховка від переповнення на краю

    b.wr = (b.wr + 1) % L                            # (3) посунути кільце
    if b.filled <= LAT:
        b.filled += 1
    return valid, code
