import math, random

NS = 4                              # 2² стани: два біти пам'яті
def rsc_step(state, u):
    m1, m2 = (state >> 1) & 1, state & 1
    a  = u ^ m1 ^ m2                # зворотний зв'язок 1+D+D² (7₈)
    p  = a ^ m2                     # прямий відвід    1+D² (5₈)
    ns = ((a << 1) | m1) & 3
    return ns, p                    # систематичний вихід = u; контроль = p

TRELLIS = [[rsc_step(s, u) for u in (0, 1)] for s in range(NS)]

def rsc_encode(bits):
    s, par = 0, []
    for u in bits:
        s, p = TRELLIS[s][u]
        par.append(p)
    return par
