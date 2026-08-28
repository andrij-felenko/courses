from dataclasses import replace

# Бульбашка — порожній пакет: усе нулі, valid = False.
def bubble() -> Slot:
    return Slot(op=OP_NOP, valid=False)

# Вибірка: дістати наступну команду за pc і посунути pc.
# imem_fetch — пам'ять команд (тут стороння для моделі).
def fetch(c: Cpu) -> Slot:
    s = imem_fetch(c.pc)
    s.valid = True
    c.pc += 1
    return s

# imem_fetch(pc) і mem_read(addr) — сторонні для моделі:
# пам'ять команд і пам'ять даних задає середовище симулятора.
