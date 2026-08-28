# f — таблиця, запакована в біти: біт x числа f — це значення f(x)
MASK = [0x5555555555555555, 0x3333333333333333, 0x0f0f0f0f0f0f0f0f,
        0x00ff00ff00ff00ff, 0x0000ffff0000ffff, 0x00000000ffffffff]

def monotone_packed(f, n):
    full = (1 << (1 << n)) - 1
    for k in range(n):                       # MASK[k] позначає клітини, де k-й вхід = 0
        if f & ~(f >> (1 << k)) & MASK[k] & full:
            return False                     # десь f(x)=1, а f(x з піднятим k-м)=0
    return True
