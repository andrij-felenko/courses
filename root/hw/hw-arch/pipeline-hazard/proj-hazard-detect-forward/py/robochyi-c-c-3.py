# Чи треба вставити бульбашку через конфлікт завантаж-використай?
# Дивимося на команду, що ЗАРАЗ у ID/EX (reg[1]) — вона на такт попереду.
def load_use_stall(c: Cpu) -> bool:
    idex = c.reg[1]   # попередня команда, іде у ВК
    ifid = c.reg[0]   # наша команда, готується ввійти в ID/EX

    if not idex.valid or idex.op != OP_LOAD or idex.rd == 0:
        return False  # попередня — не завантаження або пише в R0
    if not ifid.valid:
        return False  # нашої команди ще нема — гальмувати нічого

    # Наша команда читає регістр, який завантаження ще не встигне віддати?
    return ifid.rs1 == idex.rd or ifid.rs2 == idex.rd
