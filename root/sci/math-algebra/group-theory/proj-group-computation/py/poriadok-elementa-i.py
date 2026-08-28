def order(g, op, e):
    x, m = g, 1
    while x != e:
        x = op(x, g)
        m += 1
    return m

def cyclic(g, op, e):              # ⟨g⟩ — усі степені g
    sub, x = {e}, g
    while x != e:
        sub.add(x)
        x = op(x, g)
    return sub
