r    = [0] * 4          # регістри загального призначення
mem  = [0] * 256        # пам'ять для даних
code = [ ... ]          # програма: потік байтів-команд
ip = 0                  # лічильник команд PC
running = True

while running:                             # ── серцебиття ──
    op = code[ip]; ip += 1                 # ВИБІРКА: байт за PC, PC += 1
                                           # ДЕКОДУВАННЯ + ВИКОНАННЯ:
    if op == LD:
        d = code[ip]; ip += 1; n = code[ip]; ip += 1; r[d] = n
    elif op == LDM:
        d = code[ip]; ip += 1; a = code[ip]; ip += 1; r[d] = mem[a]
    elif op == ST:
        s = code[ip]; ip += 1; a = code[ip]; ip += 1; mem[a] = r[s]
    elif op == ADD:
        d = code[ip]; ip += 1; s = code[ip]; ip += 1; r[d] = r[d] + r[s]
    elif op == SUB:
        d = code[ip]; ip += 1; s = code[ip]; ip += 1; r[d] = r[d] - r[s]
    elif op == JMP:
        a = code[ip]; ip += 1; ip = a
    elif op == JNZ:
        s = code[ip]; ip += 1; a = code[ip]; ip += 1
        if r[s] != 0: ip = a
    elif op == HLT:
        running = False
