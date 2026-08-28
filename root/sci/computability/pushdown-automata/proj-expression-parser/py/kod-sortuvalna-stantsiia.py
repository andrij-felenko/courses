import operator
import re

# Лексер: рядок → список лексем. Числа стають числами, решта лишається символом.
TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|(.))")

def tokenize(src):
    pos, out = 0, []
    while pos < len(src):
        m = TOKEN.match(src, pos)
        if not m:
            break
        pos = m.end()
        num, sym = m.group(1), m.group(2)
        if num is not None:
            out.append(float(num))       # число — ОДНА лексема, а не окремі цифри
        elif sym.strip():
            out.append(sym)
    return out

# Таблиця операторів — ЄДИНЕ місце, де живе пріоритет.
# (пріоритет, асоціативність, дія)
OPS = {
    '+': (1, 'left',  operator.add),
    '-': (1, 'left',  operator.sub),
    '*': (2, 'left',  operator.mul),
    '/': (2, 'left',  operator.truediv),
    '^': (3, 'right', operator.pow),
}

def apply_top(vals, ops):
    """Зняти один оператор і два його операнди — покласти назад результат."""
    op = ops.pop()
    if len(vals) < 2:
        raise SyntaxError("оператору «%s» бракує операнда" % op)
    b = vals.pop()                       # правий операнд зняли ПЕРШИМ…
    a = vals.pop()                       # …лівий другим: стек віддає у зворотному порядку
    vals.append(OPS[op][2](a, b))

def evaluate(src):
    vals, ops = [], []                   # порахувати вже можна / ще ні
    for t in tokenize(src):
        if isinstance(t, float):         # число — одразу готове
            vals.append(t)
        elif t == '(':                   # бар'єр: усередині своя зона пріоритету
            ops.append(t)
        elif t == ')':                   # згорнути все до бар'єра
            while ops and ops[-1] != '(':
                apply_top(vals, ops)
            if not ops:
                raise SyntaxError("зайва закривна дужка")
            ops.pop()                    # сам бар'єр геть — дужка зникла безслідно
        elif t in OPS:
            prec, assoc, _ = OPS[t]
            while ops and ops[-1] != '(':            # бар'єр зупиняє порівняння
                top_prec = OPS[ops[-1]][0]
                # ось воно, все правило — в одному if:
                if top_prec > prec or (top_prec == prec and assoc == 'left'):
                    apply_top(vals, ops)             # вершині вже ніхто не завадить
                else:
                    break                            # вершина чекає далі
            ops.append(t)
        else:
            raise SyntaxError("невідомий символ «%s»" % t)

    while ops:                           # вхід скінчився — доганяємо все відкладене
        if ops[-1] == '(':
            raise SyntaxError("незакрита дужка")
        apply_top(vals, ops)
    if len(vals) != 1:
        raise SyntaxError("вираз не склався")
    return vals[0]
