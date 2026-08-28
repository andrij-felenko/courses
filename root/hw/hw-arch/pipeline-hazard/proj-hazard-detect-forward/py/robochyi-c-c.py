from dataclasses import dataclass, field

REGS   = 32          # регістрів у файлі; R0 — завжди нуль
NOP_RD = 0           # «нічого не пише» кодуємо записом у R0

# Коди операцій — рівно стільки, скільки треба для демонстрації.
OP_NOP, OP_ADD, OP_SUB, OP_LOAD, OP_BRANCH = range(5)

# Один «пакет» команди, що тече конвеєром від стадії до стадії.
# Це і є вміст міжстадійного регістра: усе, що стадія передає далі.
@dataclass
class Slot:
    op:    int  = OP_NOP   # що робити
    rs1:   int  = 0        # номери регістрів-джерел
    rs2:   int  = 0
    rd:    int  = 0        # номер регістра-призначення
    imm:   int  = 0        # безпосереднє значення / зсув переходу
    val:   int  = 0        # порахований результат (з'являється у ВК)
    wen:   bool = False    # чи справді пише в регістровий файл
    valid: bool = False    # пакет справжній, а не бульбашка

# Стан усього конвеєра. reg[0..3] — чотири міжстадійні регістри:
# [0]=IF/ID  [1]=ID/EX  [2]=EX/MEM  [3]=MEM/WB.
@dataclass
class Cpu:
    regfile:     list = field(default_factory=lambda: [0] * REGS)  # архітектурні регістри
    reg:         list = field(default_factory=lambda: [Slot() for _ in range(4)])  # пайплайн-регістри
    pc:          int  = 0      # лічильник команд: адреса наступної вибірки
    take_branch: bool = False  # стадія ВК підняла: перехід узято
    branch_pc:   int  = 0      # куди саме стрибнути
