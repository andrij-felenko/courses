from collections import namedtuple

Code = namedtuple("Code", "bits len")           # (код, довжина); довжина 0 → символ не трапляється

def canonical_codes(length):                    # length[s] — довжина коду символу s
    bl_count = [0] * (MAXLEN + 1)
    for s in range(SYMS):
        if length[s]:
            bl_count[length[s]] += 1

    nxt = [0] * (MAXLEN + 1)
    c = 0
    for bits in range(1, MAXLEN + 1):           # стартовий код довжини bits
        c = (c + bl_count[bits - 1]) << 1
        nxt[bits] = c

    code = [Code(0, 0)] * SYMS
    for s in range(SYMS):                        # роздати по порядку символів
        if not length[s]:
            continue
        code[s] = Code(nxt[length[s]], length[s])
        nxt[length[s]] += 1
    return code
