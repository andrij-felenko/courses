from dataclasses import dataclass

# Стан ліній Wishbone-ведучого. Кожне поле — окремий провід (чи джгут).
@dataclass
class WbMaster:
    adr: int = 0    # ADR_O — куди звертаємось
    dat_i: int = 0  # DAT_I — дані, що прийшли від веденого (читання)
    we: int = 0     # WE_O  — 1: запис, 0: читання
    stb: int = 0    # STB_O — «звертаюсь зараз»
    cyc: int = 0    # CYC_O — «тримаю шину»
    ack: int = 0    # ACK_I — «ведений готовий» (вхід)

# Прочитати одне слово за адресою addr. Крутиться, доки ведений не підтвердить.
# Повертає (значення, лічильник тактів очікування) — видно, швидкий ведений чи ні.
def wb_read(wb: WbMaster, addr: int) -> tuple[int, int]:
    wb.adr = addr
    wb.we  = 0            # читаємо
    wb.stb = 1            # звернення дійсне
    wb.cyc = 1            # тримаємо шину
    tick()                # фронт такту: лінії зафіксовано

    waited = 0
    while not wb.ack:     # ще не готово — просто чекаємо наступного фронту
        waited += 1
        tick()            # STB тримаємо піднятим — це і є суть рукостискання

    value = wb.dat_i      # ACK піднятий → дані на DAT_I дійсні саме зараз
    wb.stb = 0            # забрали слово — знімаємо звернення
    wb.cyc = 0            # відпускаємо шину
    tick()
    return value, waited
