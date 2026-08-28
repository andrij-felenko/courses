BLANK = "_"
# δ: (стан, символ) → (новий стан, що записати, куди рухатись: -1, 0, +1)
delta = {
    ("q0", "1"): ("q0", "1", +1),
    ("q0", "0"): ("q1", "1", +1),
    ("q1", "1"): ("q1", "1", +1),
    ("q1", "_"): ("q2", "_", -1),
    ("q2", "1"): ("qH", "_",  0),
}

def run(word):
    tape = dict(enumerate(word))
    head, state, steps = 0, "q0", 0
    while state != "qH":                     # qH — стан-зупинка
        sym = tape.get(head, BLANK)
        state, write, move = delta[(state, sym)]
        tape[head] = write
        head += move
        steps += 1
    return sum(1 for v in tape.values() if v == "1"), steps

def tm_add(m, n):
    ones, steps = run("1" * m + "0" + "1" * n)
    return ones                              # кількість одиниць = сума

print(tm_add(2, 3))   # 5
