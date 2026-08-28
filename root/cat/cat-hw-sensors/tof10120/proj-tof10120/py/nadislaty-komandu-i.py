from time import ticks_ms, ticks_diff

# Шле команду (напр. "s3-1#") і збирає відповідь модуля до '\n' або тайм-ауту.
# Повертає (ok, resp): ok=True, якщо у відповіді трапилось "ok"; resp — текст.
def tof_command(cmd, timeout_ms=200):
    while uart.any():                              # прибрати недочитаний потік
        uart.read()

    uart.write(cmd)                                # напр. "s3-1#"

    resp = bytearray()
    t0 = ticks_ms()
    while ticks_diff(ticks_ms(), t0) < timeout_ms:
        c = uart.read(1)
        if c is None:
            continue
        if c in (b'\n', b'\r'):                    # кінець рядка відповіді
            if resp:
                return (b"ok" in resp, resp.decode())
        else:
            resp += c
    return (False, resp.decode())                  # модуль не відповів вчасно

def apply_settings():
    # сира миттєва відстань
    ok, resp = tof_command("s3-1#")
    print("режим: сира — ok" if ok else "режим: збій, відповідь=" + resp)

    # пасивний режим: більше не базікає сам
    tof_command("s5-1#")

    # юстування нуля: якщо модуль стабільно завищує на 5 мм — компенсуємо
    tof_command("s1-05#")

    # тепер відстань беремо на запит
    ok, resp = tof_command("r6#")
    if ok:
        print("на r6# прийшло:", resp)             # напр. L=0748
