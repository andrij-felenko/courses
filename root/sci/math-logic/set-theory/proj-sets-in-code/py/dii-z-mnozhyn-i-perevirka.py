def intersect(A, B):
    out = set()
    for x in A:            # йдемо по A (розумно — по меншій із двох)
        if x in B:         # x ∈ A і x ∈ B  → лишаємо
            out.add(x)
    return out

def union(A, B):
    out = set(A)           # усе з A
    for x in B:
        out.add(x)         # плюс усе з B; повтори множина відкине сама
    return out

def difference(A, B):
    return {x for x in A if x not in B}   # x ∈ A і x ∉ B
