from math import log

def responsible_moment(p0, lam, C_r, c):
    x = lam * p0 * C_r / c          # вигода першого тижня, поділена на накладні
    if x <= 1:                      # навіть перший тиждень не окуповується
        return 0.0
    return log(x) / lam             # t* = (1/λ)·ln(λ·p₀·C_r / c)

def residual_error(lam, C_r, c):
    return c / (lam * C_r)          # p(t*) — залишкова похибка на моменті

print(round(responsible_moment(0.6, 1/6, 120, 4), 1))   # 6.6
print(round(residual_error(1/6, 120, 4), 2))            # 0.2
