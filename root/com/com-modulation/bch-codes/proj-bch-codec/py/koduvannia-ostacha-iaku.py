def encode(msg):                         # msg: K бітів, msg[0] = коеф. при x^(n−1)
    reg = 0
    for i, b in enumerate(msg):          # покласти дані у старші позиції x¹⁴…x⁸
        if b:
            reg |= 1 << (N - 1 - i)
    rem = reg
    for s in range(N - 1, DEG - 1, -1):  # ділення стовпчиком над GF(2)
        if rem & (1 << s):
            rem ^= GINT << (s - DEG)
    return reg | rem                     # дані у старших бітах, остача — у молодших
