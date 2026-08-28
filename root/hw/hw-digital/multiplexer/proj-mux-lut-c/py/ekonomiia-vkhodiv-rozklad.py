from enum import Enum

# Позначення того, у що зводиться функція від останньої змінної c у кожній парі рядків.
class MuxDin(Enum):     # 0, 1, c, ¬c
    IN_0 = 0
    IN_1 = 1
    IN_C = 2
    IN_NC = 3

# Розклад f(a,b,c) за молодшою змінною c:
# для кожної адреси (a,b) визначаємо, яку з чотирьох форм дає функція від c.
# Результат — чотири входи даних мультиплексора 4→1 з адресою (a,b).
def decompose_by_c(f) -> list[MuxDin]:
    din = [MuxDin.IN_0] * 4
    for ab in range(4):
        a = (ab >> 1) & 1
        b = (ab >> 0) & 1
        y0 = f(a, b, 0)                # кофактор c=0
        y1 = f(a, b, 1)                # кофактор c=1
        if   not y0 and not y1: din[ab] = MuxDin.IN_0    # обидва 0  → сталий 0
        elif     y0 and     y1: din[ab] = MuxDin.IN_1    # обидва 1  → сталий 1
        elif not y0 and     y1: din[ab] = MuxDin.IN_C    # 0,1       → дорівнює c
        else:                   din[ab] = MuxDin.IN_NC   # 1,0       → дорівнює ¬c
    return din

# Обчислення на меншому мультиплексорі: адреса — лише (a,b),
# а обраний вхід за потреби підставляє живе значення c.
def mux4_eval(din: list[MuxDin], a: bool, b: bool, c: bool) -> bool:
    ab = (a << 1) | b                  # адреса з двох змінних
    choice = din[ab]                   # "прочитати" обраний вхід
    if   choice is MuxDin.IN_0:  return False
    elif choice is MuxDin.IN_1:  return True
    elif choice is MuxDin.IN_C:  return c
    else:                        return not c
