from enum import Enum

class Uop(Enum):
    LOAD  = "load"
    ADD   = "add"
    STORE = "store"

# «ROM мікрокоду»: рецепт (послідовність мікрооперацій) на кожну машинну команду.
OP_ADD, OP_ADDM = "ADD", "ADDM"

rom = {
    OP_ADD:  [Uop.ADD],
    # УВАГА: у цьому рецепті помилка — бракує Uop.STORE (результат не збережеться).
    OP_ADDM: [Uop.LOAD, Uop.ADD],
}

# «patch RAM»: спершу порожня — заповнює прошивка на старті.
patch = {}

TEXT = {
    Uop.LOAD:  "  µop: load  t <- [mem]",
    Uop.ADD:   "  µop: add   t += reg",
    Uop.STORE: "  µop: store [mem] <- t",
}

# Рушій: вибрати рецепт (патч має пріоритет над ROM) і виконати мікрооперації.
def run_instruction(opcode):
    seq = patch.get(opcode, rom[opcode])   # є патч → беремо його, інакше рідний ROM
    for uop in seq:
        print(TEXT[uop])

# Прошивка на старті заливає патч у patch RAM (тут — після перевірки підпису).
def load_microcode_patch():
    # виправлений рецепт ADDM — уже з кроком збереження
    patch[OP_ADDM] = [Uop.LOAD, Uop.ADD, Uop.STORE]

if __name__ == "__main__":
    print("ADDM до патча (помилковий рецепт, без store):")
    run_instruction(OP_ADDM)

    load_microcode_patch()        # <- те, що робить BIOS/ОС на кожному старті

    print("ADDM після патча (виправлено):")
    run_instruction(OP_ADDM)
