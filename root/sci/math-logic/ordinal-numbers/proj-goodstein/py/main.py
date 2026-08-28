from dataclasses import dataclass

# ── 1. Спадкова основа: прочитати v за основою b, переписати за основою c ──────
def bump(v, b, c):
    """Спадковий запис v за основою b, з КОЖНОЮ основою (і в показниках!)
    заміненою на c. При c = b+1 це і є «підвищ основу» кроку Ґудстейна."""
    if v == 0:
        return 0
    total, power = 0, 0
    while v > 0:
        d = v % b                                 # цифра при b^power
        if d:
            total += d * c ** bump(power, b, c)   # показник теж підвищуємо — рекурсія
        v //= b
        power += 1
    return total

# ── 2. Ординал-тінь у канторовій нормальній формі ─────────────────────────────
@dataclass(frozen=True)
class Ord:
    """КНФ: терми (показник: Ord, коефіцієнт: int); показники строго спадають."""
    terms: tuple            # ((exp, coef), …)

ZERO = Ord(())

def to_ordinal(v, b):
    """Та сама схема, що й bump, але замість основи підставляємо ω."""
    if v == 0:
        return ZERO
    terms, power = [], 0
    while v > 0:
        d = v % b
        if d:
            terms.append((to_ordinal(power, b), d))   # показник — теж ординал
        v //= b
        power += 1
    return Ord(tuple(reversed(terms)))                 # показники — за спаданням

def ord_cmp(A, B):
    """-1 / 0 / +1. Лексикографічно: показник важить більше за коефіцієнт."""
    for (ea, ca), (eb, cb) in zip(A.terms, B.terms):
        c = ord_cmp(ea, eb)
        if c:
            return c
        if ca != cb:
            return -1 if ca < cb else 1
    if len(A.terms) == len(B.terms):
        return 0
    return 1 if len(A.terms) > len(B.terms) else -1    # довший запис — більший

SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
def _wrap(e):
    return e if all(ch not in e for ch in "+· ") else "(%s)" % e
def ord_str(A):
    if not A.terms:
        return "0"
    out = []
    for exp, c in A.terms:
        if exp == ZERO:                              # ω⁰ = 1  →  просто число
            out.append(str(c))
        else:
            e = ord_str(exp)
            base = "ω" if e == "1" else ("ω" + e.translate(SUP) if e.isdigit()
                                         else "ω^" + _wrap(e))
            out.append(base if c == 1 else "%s·%d" % (base, c))
    return " + ".join(out)

# ── 3. Крок Ґудстейна + паралельна тінь ───────────────────────────────────────
def goodstein(start, max_steps=40):
    v, b = start, 2
    prev = None
    for step in range(max_steps):
        shadow = to_ordinal(v, b)                    # тінь поточного числа
        mark = "" if prev is None else (
            "↓ строго меншає" if ord_cmp(shadow, prev) < 0 else "??? НЕ МЕНШАЄ")
        print(f"крок {step:>2}: основа {b:>2}   G = {v:<20} тінь = {ord_str(shadow):<18}{mark}")
        prev = shadow
        if v == 0:
            print(f"→ дійшли 0 за {step} кроків"); return
        v = bump(v, b, b + 1) - 1                     # ① підвищ основу  ② −1
        b += 1

goodstein(3)
print()
goodstein(4, max_steps=6)
