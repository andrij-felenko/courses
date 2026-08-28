# Цифровий двійник RC-диференціатора: вихід ∝ швидкості зміни входу.
DT  = 0.1e-3       # крок 0.1 мс
TAU = 5.0e-3       # та сама стала часу

_v_prev = 0.0

def rc_differentiate(v_in):
    global _v_prev
    deriv = TAU * (v_in - _v_prev) / DT   # τ · dV/dt
    _v_prev = v_in
    return deriv                          # сплеск на зміні, нуль на сталому вході
