from dataclasses import dataclass

# Опкоди й операції АЛП
OP_ADD, OP_SUB, OP_LOAD = 0x1, 0x2, 0x3
ALU_ADD, ALU_SUB, ALU_PASS = 0, 1, 2

# Керувальні сигнали — по одному "дроту" на поле (модель зашитого декодера).
@dataclass
class Control:
    reg_a: int = 0
    reg_b: int = 0
    reg_dst: int = 0        # які регістри читати / куди писати
    alu_op: int = ALU_PASS  # яку операцію ввімкнути в АЛП
    reg_write: bool = False # лінія "защіпнути результат у регістр"
    mem_read: bool = False  # лінія "читати з пам'яті по шині"

def decode(ir: int) -> Control:
    c = Control()                   # усі лінії спершу опущені (0)
    op  = (ir >> 12) & 0xF          # опкод      = старші 4 біти
    dst = (ir >>  8) & 0xF          # призначення = наступні 4
    a   = (ir >>  4) & 0xF          # операнд A
    b   =  ir        & 0xF          # операнд B

    if op == OP_ADD:                # 0x1 → додати
        c.reg_a, c.reg_b, c.reg_dst = a, b, dst
        c.alu_op = ALU_ADD          # увімкнути в АЛП додавання
        c.reg_write = True          # після рахунку — записати результат
    elif op == OP_LOAD:             # 0x3 → завантажити з пам'яті
        c.reg_dst = dst
        c.mem_read = True           # спершу привезти число шиною
        c.reg_write = True
    # ... решта опкодів

    return c                        # готовий набір сигналів на цей такт
