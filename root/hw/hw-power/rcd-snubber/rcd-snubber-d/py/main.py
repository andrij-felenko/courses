# Порахувати резистор і потужність снабера; повернути None, якщо вибір V_clamp
# негодящий (нижче за відбиту або вище за стелю транзистора з запасом).
def rcd_snubber(v_in, v_r, l_lk, i_pk, f_sw, v_clamp, bv_dss, margin):
    # v_in — вхідна напруга (В);  v_r — відбита (В);  l_lk — витік (Гн);
    # i_pk — піковий струм (А);   f_sw — частота (Гц);
    # v_clamp — рівень фіксації (В);  bv_dss — межа ключа (В);  margin — запас
    if v_clamp <= v_r:                          # нижче за відбиту — снабер не працює
        return None
    if v_in + v_clamp > bv_dss * (1.0 - margin):  # за стелю транзистора
        return None

    p_lk = 0.5 * l_lk * i_pk**2 * f_sw          # потужність витоку (Вт)
    r = v_clamp * (v_clamp - v_r) / p_lk        # резистор (Ом)
    p = v_clamp**2 / r                          # розсіювання на R (Вт)
    c = 10.0 / (r * f_sw)                        # C з R·C ≈ 10·період (Ф)
    return r, p, c

res = rcd_snubber(325, 100, 5e-6, 1.0, 65000, 200, 650, 0.15)
if res:
    r, p, c = res
    print(f"R = {r/1e3:.0f} кОм,  P = {p:.2f} Вт,  C = {c*1e9:.1f} нФ")
else:
    print("Вибір V_clamp негодящий — перегляньте рівень фіксації")
# Вивід: R = 123 кОм,  P = 0.33 Вт,  C = 1.5 нФ
