def pv(fv, r, n):
    """Теперішня вартість суми fv, яку заплатять/отримають через n років."""
    return fv / (1 + r) ** n

def npv(flows, r):
    """flows[t] — потік у рік t (t = 0, 1, 2, …). Зводить усе до сьогодні."""
    return sum(cf / (1 + r) ** t for t, cf in enumerate(flows))

def annuity_factor(r, n):
    """A(r) = Σ 1/(1+r)^t за t = 1..n — замкнутий вигляд, без циклу."""
    if r == 0:                      # границя: дисконтувати нічого
        return float(n)
    return (1 - (1 + r) ** (-n)) / r

# Рівний потік 60 тис. на рік п'ять років під 10 % — одним множенням:
print(60 * annuity_factor(0.10, 5))   # 227.45 тис.
