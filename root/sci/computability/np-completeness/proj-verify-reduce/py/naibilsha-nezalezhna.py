def verify_independent(n, edges, cert, k):
    """True, якщо cert — незалежна множина розміру щонайменше k."""
    S = set(cert)
    if len(S) != len(cert) or any(v < 0 or v >= n for v in S):
        return False                      # дублікати чи неіснуючі вершини
    if len(S) < k:
        return False                      # замала
    for (u, v) in edges:
        if u in S and v in S:
            return False                  # обидва кінці ребра обрано — не незалежна
    return True
