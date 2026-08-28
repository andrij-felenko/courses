# один розряд АЛП: повертає (біт результату y, перенос-вихід cout)
# op: 0=ADD, 1=AND, 2=OR
def alu_bit(a, b, cin, op):
    sum_     = a ^ b ^ cin                   # біт суми: непарність трьох входів
    cout_add = (a & b) | (cin & (a ^ b))     # перенос: «більшість»
    and_     = a & b                         # a AND b
    or_      = a | b                          # a OR b

    cout = cout_add if op == 0 else 0        # перенос має сенс лише для ADD
    if op == 0:
        return sum_, cout                    # мультиплексор «3-в-1»
    if op == 1:
        return and_, cout                    # обирає один із трьох
    return or_, cout                         # op == 2 → OR
