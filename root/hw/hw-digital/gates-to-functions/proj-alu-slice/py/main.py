# Коди операцій АЛП
OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR = 0, 1, 2, 3, 4

# Прапорці стану (бітова маска)
FLAG_Z, FLAG_C, FLAG_N, FLAG_V = 1, 2, 4, 8

ALU_BITS = 8                                          # ширина слова


def alu_slice(a, b, cin, op):
    """одна скибка: розряд a,b + перенос cin, код op → (біт y, перенос cout)"""
    s     = a ^ b ^ cin                               # біт суми = непарність трьох
    carry = (a & b) | (cin & (a ^ b))                 # перенос = «більшість»
    if op == OP_AND:   y = a & b
    elif op == OP_OR:  y = a | b
    elif op == OP_XOR: y = a ^ b
    else:              y = s                           # ADD і SUB обидва йдуть сумою
    return y, carry


def alu(a, b, op):
    """n-бітний АЛП: повертає (result, flags)"""
    is_arith = op in (OP_ADD, OP_SUB)
    sub      = 1 if op == OP_SUB else 0
    cin      = sub                                    # SUB: початковий перенос = 1
    result   = 0
    cout = cprev = 0

    for i in range(ALU_BITS):
        ai = (a >> i) & 1
        bi = (b >> i) & 1
        bi ^= sub                                     # SUB інвертує b (доповняльний код)
        cprev = cout                                  # запам'ятати перенос ДО старшого біта
        yi, cout = alu_slice(ai, bi, cin, op)
        result |= yi << i
        cin = cout                                    # перенос біжить у наступний розряд

    # прапорці
    mask = (1 << ALU_BITS) - 1
    f = 0
    if (result & mask) == 0:                f |= FLAG_Z   # нуль
    if (result >> (ALU_BITS - 1)) & 1:      f |= FLAG_N   # знак
    if is_arith:
        if cout:            f |= FLAG_C                    # перенос за межі слова
        if cout != cprev:   f |= FLAG_V                    # знакове переповнення
    return result & mask, f
