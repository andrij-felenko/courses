import math
from dataclasses import dataclass

ABS_TOL = 1e-6     # долішній поріг: трохи нижчий за найменший осмислений показ
REL_TOL = 1e-9     # відносний: на кілька порядків вищий за шум коми, нижчий за дрейф

@dataclass(frozen=True)
class Part:
    home_id: int
    day: str

def load_totals(cur, sql, params):
    cur.execute(sql, params)
    # партиція → (кількість, сума)
    return {Part(r[0], str(r[1])): (r[2], float(r[3] or 0.0)) for r in cur.fetchall()}

def sums_close(a, b) -> bool:
    # НІКОЛИ не порівнюй суми рухомої коми через ==; лише в межах допуску.
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)

def reconcile(cur, src_sql, der_sql, params):
    src = load_totals(cur, src_sql, params)   # джерело — істина
    der = load_totals(cur, der_sql, params)   # похідне — що бачить користувач
    drift = []
    for p in src.keys() | der.keys():
        n_s, kwh_s = src.get(p, (0, 0.0))
        n_d, kwh_d = der.get(p, (0, 0.0))
        if p not in der:                       # факти є, агрегата нема → ВТРАТА
            drift.append((p, "ВІДСУТНЯ", f"джерело n={n_s}, Σ={kwh_s:.4f}; похідного нема"))
        elif p not in src:                     # агрегат є, фактів нема → підозріло
            drift.append((p, "СИРОТА",  f"похідне n={n_d}, Σ={kwh_d:.4f}; джерела нема"))
        elif n_s != n_d:                       # кількість — точна рівність
            drift.append((p, "COUNT",   f"джерело n={n_s} ≠ похідне n={n_d}"))
        elif not sums_close(kwh_s, kwh_d):     # сума — у межах допуску
            drift.append((p, "SUM",     f"Δ={abs(kwh_s - kwh_d):.6f} кВт·год"))
    return drift
