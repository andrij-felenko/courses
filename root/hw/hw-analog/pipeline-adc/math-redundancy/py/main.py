# 1.5-бітний щабель: два пороги ±Vref/4 (тут Vref=1, шкала −1..+1).
# Повертає (цифру D∈{0,1,2}, залишок для наступного щабля).
def stage_15bit(vin, thr_hi, thr_lo):
    if   vin >= thr_hi: d = 2      # вище верхнього порога
    elif vin >= thr_lo: d = 1      # між порогами — коридор
    else:               d = 0      # нижче нижнього порога
    res = 2.0 * vin - (d - 1)      # залишок = 2·Vвх − (D−1)·Vref, Vref=1
    return d, res


# Зібрати код N щаблів зсувним додаванням: код = Σ Dᵢ·2^(N−1−i)
def assemble(D):
    n = len(D)
    return sum(d << (n - 1 - i) for i, d in enumerate(D))  # зсув = вага щабля


def demo():
    N = 4
    vin = 0.30                     # вхід у частках Vref

    # — чесні пороги: ±0.25 на всіх щаблях —
    D = []
    r = vin
    for _ in range(N):
        d, r = stage_15bit(r, +0.25, -0.25)
        D.append(d)
    code_ok = assemble(D)          # еталонний код

    # — той самий вхід, але верхній поріг ПЕРШОГО щабля зсунуто на +0.15 —
    D = []
    r = vin
    d, r = stage_15bit(r, +0.25 + 0.15, -0.25)   # поріг 0.40 замість 0.25
    D.append(d)
    for _ in range(N - 1):
        d, r = stage_15bit(r, +0.25, -0.25)
        D.append(d)
    code_bad = assemble(D)         # код зі зсунутим компаратором

    # code_ok == code_bad — зсувне додавання скасувало похибку порога
