from dataclasses import dataclass
from enum import IntEnum

class Cond(IntEnum):           # вибір умови
    NONE = 0
    ZERO = 1
    CARRY = 2

# Одна горизонтальна мікрокоманда: керувальні біти прямо, плюс керування μPC.
@dataclass
class Micro:
    # --- керувальні лінії (кожен біт = один "дріт") ---
    alu_add: bool = False      # яку операцію ввімкнути в АЛП
    alu_sub: bool = False
    reg_write: bool = False    # защіпнути результат у регістр
    mem_read: bool = False     # читати з пам'яті шиною
    # --- керування послідовністю ---
    cond: Cond = Cond.NONE     # на який прапорець дивитися (0 = безумовно)
    next: int = 0              # куди вести μPC на розвилці

# Прапорці стану від АЛП (те, на що дивиться логіка наступної адреси).
@dataclass
class Flags:
    zero: bool = False
    carry: bool = False

store: list[Micro] = []        # сховище мікрокоманд (control store)
alu_flags = Flags()            # поточний стан від АЛП

def apply(m: Micro) -> None:   # виставити біти рядка на дроти
    ...

# Один такт мікрорушія: прочитати рядок, виконати, порахувати наступну адресу.
def micro_step(upc: int) -> int:
    m = store[upc]             # ЧИТАННЯ зі сховища — саме цей зайвий такт
    apply(m)                   # біти рядка йдуть прямо на керувальні лінії

    # --- логіка наступної адреси (друга машина — послідовність) ---
    if m.cond == Cond.ZERO:    # чи спрацювала умова розгалуження?
        take = alu_flags.zero
    elif m.cond == Cond.CARRY:
        take = alu_flags.carry
    else:                      # COND_NONE — просто далі
        take = False

    return m.next if take else (upc + 1) & 0xFFFF   # стрибок або наступний рядок
