line = bytearray()           # буфер для одного рядка-команди
MAX_LEN = 63                 # межа проти переповнення

def poll(port):
    # 1. Забрати все, що ВЖЕ прийшло, не чекаючи решти
    while port.in_waiting:
        c = port.read(1)                     # рівно один байт

        if c in (b'\n', b'\r'):              # кінець рядка → команда готова
            if line:
                handle_command(line.decode())  # розібрати її
                line.clear()                   # і почати збирати наступну
        elif len(line) < MAX_LEN:            # звичайний символ — у буфер
            line += c
        else:
            line.clear()                     # переповнення: скинути сміття

def loop(port):
    while True:
        poll(port)
        # 2. Решта циклу біжить ЩОтакту, бо ми ніде не блокувалися
        update_motors()
        check_failsafe()
