BL = "␣"                                      # порожня клітинка

def run(delta, w, start="q0", limit=10_000, trace=False):
    tape = {i: c for i, c in enumerate(w)}    # стрічка — словник, не масив
    q, head = start, 0
    for steps in range(limit + 1):
        if trace:
            print(snapshot(tape, head, q))
        if q == "qa":
            return "ПРИЙНЯТО", steps, content(tape)
        if q == "qr":
            return "ВІДКИНУТО", steps, content(tape)
        rule = delta.get((q, tape.get(head, BL)))     # уся δ — один пошук
        if rule is None:                              # правила немає — за домовленістю «ні»
            return "ВІДКИНУТО", steps, content(tape)
        write, move, q = rule
        tape[head] = write
        head += 1 if move == "R" else -1
    return "НЕ ЗНАЮ", limit, content(tape)            # ліміт вичерпано — і це НЕ «зациклилась»

def snapshot(tape, head, q):
    keys = list(tape) + [head]
    cells = "".join(("▸" if i == head else " ") + tape.get(i, BL)
                    for i in range(min(keys), max(keys) + 1))
    return "%-3s%s" % (q + ":", cells)

def content(tape):
    return "".join(tape[i] for i in sorted(tape)).strip(BL)

# таблиця δ машини, що перевіряє мову {0ⁿ1ⁿ}: викреслюємо пари 0↔1 позначками X та Y
D01 = {
    ("q0", "0"): ("X", "R", "q1"), ("q0", "Y"): ("Y", "R", "q3"), ("q0", BL): (BL, "R", "qa"),
    ("q1", "0"): ("0", "R", "q1"), ("q1", "Y"): ("Y", "R", "q1"), ("q1", "1"): ("Y", "L", "q2"),
    ("q2", "0"): ("0", "L", "q2"), ("q2", "Y"): ("Y", "L", "q2"), ("q2", "X"): ("X", "R", "q0"),
    ("q3", "Y"): ("Y", "R", "q3"), ("q3", BL): (BL, "R", "qa"),
}
