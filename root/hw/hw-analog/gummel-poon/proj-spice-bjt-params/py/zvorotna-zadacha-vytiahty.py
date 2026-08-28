# «виміряні» криві синтезуємо з відомого приладу — щоб було з чим звіряти
true = dict(IS=1e-14, BF=250.0, NF=1.0, VAF=80.0, IKF=80e-3, ISE=8e-13, NE=2.0)
vbe = np.arange(0.30, 0.85, 0.01)
ic0, ib0, _ = gummel_poon(vbe, p=true)
rng = np.random.default_rng(0)
ic_m = ic0 * np.exp(0.01 * rng.standard_normal(vbe.size))   # ±1% шуму виміру
ib_m = ib0 * np.exp(0.01 * rng.standard_normal(vbe.size))
beta_m = ic_m / ib_m

def fit_log_line(v, y, lo, hi):
    """нахил a та перетин b для ln y = a·v + b на відрізку [lo, hi]"""
    m = (v >= lo) & (v <= hi)
    a, b = np.polyfit(v[m], np.log(y[m]), 1)
    return a, b

# I_S та NF — із СЕРЕДНЬОЇ прямої I_К (де q_b≈1 і витік уже позаду)
a, b = fit_log_line(vbe, ic_m, 0.50, 0.62)
NF_x = 1.0 / (a * Vt);   IS_x = np.exp(b)

# ISE та NE — із НИЗЬКОСТРУМОВОГО коліна I_Б (там панує лише витік)
a, b = fit_log_line(vbe, ib_m, 0.30, 0.40)
NE_x = 1.0 / (a * Vt);   ISE_x = np.exp(b)

# BF — це ПЛАТО β (де обидві прямі йдуть в унісон, проміжок сталий)
BF_x = beta_m.max()

# IKF — струм, де β впало до 0.618 плато з боку ВЕЛИКИХ струмів
peak = beta_m.argmax()
tail = np.arange(peak, vbe.size)
j = tail[np.argmax(beta_m[tail] < 0.618 * BF_x)]
IKF_x = 1.618 * ic_m[j]

# VAF — з ОКРЕМОГО знімка: I_К проти V_CE при сталому V_BE (нахил плато)
vce = np.arange(1.0, 6.0, 0.5)
ic_out = np.array([gummel_poon(0.62, vbc=0.62 - v, p=true)[0] for v in vce])
slope, _ = np.polyfit(vce, ic_out, 1)
VAF_x = ic_out[0] / slope - vce[0]

for name, got, ref in [("IS ", IS_x, true['IS']), ("NF ", NF_x, true['NF']),
                       ("BF ", BF_x, true['BF']), ("VAF", VAF_x, true['VAF']),
                       ("IKF", IKF_x*1e3, true['IKF']*1e3),
                       ("ISE", ISE_x, true['ISE']), ("NE ", NE_x, true['NE'])]:
    print(f"{name}:  видобуто {got:10.4g}   істина {ref:10.4g}")
