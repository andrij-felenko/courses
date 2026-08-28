# Вибрати актуальне значення регістра r для входу ALU.
# Порядок перевірок = пріоритет джерел: ближче (EX/MEM) — раніше.
def forward(c: Cpu, r: int) -> int:
    exmem = c.reg[2]   # команда на такт попереду
    memwb = c.reg[3]   # команда на два такти попереду

    # Джерело 1 — EX/MEM: найсвіжіший результат. Пріоритет над усім.
    if exmem.valid and exmem.wen and exmem.rd == r and r != 0:
        return exmem.val

    # Джерело 2 — MEM/WB: старіший результат. Беремо, лише якщо ближче не спрацювало.
    if memwb.valid and memwb.wen and memwb.rd == r and r != 0:
        return memwb.val

    # Пробросу немає — значення вже лежить у регістровому файлі.
    return c.regfile[r]
