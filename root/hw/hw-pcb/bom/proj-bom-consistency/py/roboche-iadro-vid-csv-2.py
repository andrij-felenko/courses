import re

# Розділити позначення на літерний префікс і числовий хвіст: "R12" → ("R",12).
# Якщо хвіст не число — number = -1 (не діапазонне позначення).
def split_ref(r):
    m = re.fullmatch(r"(\D*)(\d+)", r)         # префікс без цифр + числовий хвіст
    if not m:
        return "", -1                          # немає цифр або хвіст не чисто числовий
    return m.group(1), int(m.group(2))

# Розгорнути "R1-R4" → ["R1","R2","R3","R4"]. Якщо це не діапазон — повернути сам токен.
# Працює лише коли префікси збігаються (R..R), а хвости — числа.
def expand_range(token):
    dash = token.find('-')
    if dash < 0:
        return [token]                         # не діапазон

    lp, ln = split_ref(norm_ref(token[:dash]))
    hp, hn = split_ref(norm_ref(token[dash + 1:]))

    # Діапазон правомірний лише якщо обидва боки — позначення з ОДНАКОВИМ префіксом.
    if ln < 0 or hn < 0 or not lp or lp != hp:
        return [norm_ref(token)]               # не схоже на діапазон — як є

    step = 1 if ln <= hn else -1               # діапазон може й спадати
    return [lp + str(n) for n in range(ln, hn + step, step)]   # R1, R2, ...
