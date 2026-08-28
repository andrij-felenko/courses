# -*- coding: utf-8 -*-
"""Фігури до теми «Імпеданс шини живлення (PDN)».
Генерує SVG-діаграми:
1. pdn-impedance-profile.svg — комплексний профіль імпедансу PDN від DC до 1 ГГц з лінією Z_target та 4 ярусами розв'язки.
2. pdn-anti-resonance.svg — утворення антирезонансного піку при паралельному з'єднанні конденсаторів та методи демпфування.
"""
import sys, os, math, cmath

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def head(cx, cy, ang_deg, color, size=7):
    a = math.radians(ang_deg)
    bx, by = math.cos(a), math.sin(a)
    px, py = -by, bx
    x1, y1 = cx - bx * size + px * size * 0.55, cy - by * size + py * size * 0.55
    x2, y2 = cx - bx * size - px * size * 0.55, cy - by * size - py * size * 0.55
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
            % (cx, cy, x1, y1, x2, y2, color))


# ── Фігура 1: Комплексний профіль імпедансу PDN ─────────────────────────────
def fig_pdn_profile():
    W, H = 940, 580
    P = []

    # Координатна сітка
    x_min, x_max = 95.0, 875.0
    y_min, y_max = 85.0, 480.0

    # Частоти: 100 Гц (10^2) до 1 ГГц (10^9) -> 7 декад
    f_log_min = 2.0
    f_log_max = 9.0

    def f_to_x(f_val):
        lf = math.log10(max(100.0, f_val))
        return x_min + (lf - f_log_min) / (f_log_max - f_log_min) * (x_max - x_min)

    # Імпеданс: 0.1 мОм (10^-4) до 10 Ом (10^1) -> 5 декад
    z_log_min = -4.0
    z_log_max = 1.0

    def z_to_y(z_val):
        lz = math.log10(max(1e-4, min(10.0, z_val)))
        return y_max - (lz - z_log_min) / (z_log_max - z_log_min) * (y_max - y_min)

    # Фонова сітка та осі
    f_ticks = [
        (1e2, "100 Гц"), (1e3, "1 кГц"), (1e4, "10 кГц"),
        (1e5, "100 кГц"), (1e6, "1 МГц"), (1e7, "10 МГц"),
        (1e8, "100 МГц"), (1e9, "1 ГГц")
    ]
    for ft, flab in f_ticks:
        xv = f_to_x(ft)
        P.append(line(xv, y_min, xv, y_max, color="#e5e9f0", sw=1.0))
        P.append(text(xv, y_max + 18, flab, size=11, color=MUTED, anchor="middle"))

    z_ticks = [
        (1e-4, "0.1 мОм"), (1e-3, "1 мОм"), (1e-2, "10 мОм"),
        (1e-1, "100 мОм"), (1.0, "1 Ом"), (10.0, "10 Ом")
    ]
    for zt, zlab in z_ticks:
        yv = z_to_y(zt)
        P.append(line(x_min, yv, x_max, yv, color="#e5e9f0", sw=1.0))
        P.append(text(x_min - 8, yv + 4, zlab, size=11, color=MUTED, anchor="end"))

    # Рамка графіка
    P.append(rect(x_min, y_min, x_max - x_min, y_max - y_min, fill="none", stroke="#b0b8c4", sw=1.2, rx=0))

    # Смуги частотних зон зверху
    zones = [
        (1e2, 1e5, "1. Стабілізатор (VRM)", "#edf4fc"),
        (1e5, 1e7, "2. Об'ємні C (Bulk)", "#fdf6ec"),
        (1e7, 2e8, "3. Кераміка MLCC", "#f2f9ec"),
        (2e8, 1e9, "4. Площини та кристал", "#fbf0f8")
    ]
    for f1, f2, ztitle, bgcol in zones:
        x1 = f_to_x(f1)
        x2 = f_to_x(f2)
        P.append(rect(x1, y_min - 32, x2 - x1, 24, fill=bgcol, stroke="#c8d2df", sw=1.0, rx=3))
        P.append(text((x1 + x2) / 2.0, y_min - 16, ztitle, size=11, color=INK, bold=True, anchor="middle"))

    # Розрахунок кривих компонентів
    num_pts = 350
    freqs = [10 ** (f_log_min + i * (f_log_max - f_log_min) / (num_pts - 1)) for i in range(num_pts)]

    # 1. VRM
    z_vrm_pts = []
    for f in freqs:
        w = 2.0 * math.pi * f
        zv = 0.0006 * math.sqrt(1.0 + (f / 70000.0) ** 2) + w * 2.5e-9
        z_vrm_pts.append((f_to_x(f), z_to_y(zv)))
    P.append(polyline(z_vrm_pts, color="#8a9ba8", sw=1.5, dash="4,3"))

    # 2. Bulk Capacitors
    z_bulk_pts = []
    c_bulk, esr_bulk, esl_bulk = 880e-6, 0.004, 0.4e-9
    for f in freqs:
        w = 2.0 * math.pi * f
        zc = complex(esr_bulk, w * esl_bulk - 1.0 / (w * c_bulk))
        z_bulk_pts.append((f_to_x(f), z_to_y(abs(zc))))
    P.append(polyline(z_bulk_pts, color="#d97706", sw=1.5, dash="5,3"))

    # 3. MLCCs
    z_mlcc_pts = []
    mlcc_list = [
        (10, 10e-6, 0.008, 0.6e-9),
        (20, 1e-6, 0.012, 0.4e-9),
        (40, 0.1e-6, 0.020, 0.35e-9),
        (30, 0.01e-6, 0.040, 0.25e-9)
    ]
    for f in freqs:
        w = 2.0 * math.pi * f
        y_total = complex(0.0, 0.0)
        for count, c_val, esr_val, esl_val in mlcc_list:
            z_single = complex(esr_val, w * esl_val - 1.0 / (w * c_val))
            y_total += count / z_single
        z_eq = abs(1.0 / y_total) if abs(y_total) > 0 else 10.0
        z_mlcc_pts.append((f_to_x(f), z_to_y(z_eq)))
    P.append(polyline(z_mlcc_pts, color="#16a34a", sw=1.5, dash="6,3"))

    # 4. Plane
    z_plane_pts = []
    c_plane, esr_plane, esl_plane = 8e-9, 0.002, 25e-12
    for f in freqs:
        w = 2.0 * math.pi * f
        zc = complex(esr_plane, w * esl_plane - 1.0 / (w * c_plane))
        z_plane_pts.append((f_to_x(f), z_to_y(abs(zc))))
    P.append(polyline(z_plane_pts, color="#9333ea", sw=1.5, dash="4,3"))

    # 5. Die
    z_die_pts = []
    c_die, r_die, l_pkg = 45e-9, 0.015, 45e-12
    for f in freqs:
        w = 2.0 * math.pi * f
        zc = complex(r_die, w * l_pkg - 1.0 / (w * c_die))
        z_die_pts.append((f_to_x(f), z_to_y(abs(zc))))
    P.append(polyline(z_die_pts, color="#ec4899", sw=1.5, dash="3,3"))

    # 6. Total PDN Z
    z_total_pts = []
    for f in freqs:
        w = 2.0 * math.pi * f
        z_v = complex(0.0006, w * 2.5e-9 + 0.0006 * (f / 70000.0))
        y_sum = 1.0 / z_v
        y_sum += 1.0 / complex(esr_bulk, w * esl_bulk - 1.0 / (w * c_bulk))
        for count, c_val, esr_val, esl_val in mlcc_list:
            y_sum += count / complex(esr_val, w * esl_val - 1.0 / (w * c_val))
        y_sum += 1.0 / complex(esr_plane, w * esl_plane - 1.0 / (w * c_plane))
        y_sum += 1.0 / complex(r_die, w * l_pkg - 1.0 / (w * c_die))

        zt = abs(1.0 / y_sum)
        z_total_pts.append((f_to_x(f), z_to_y(zt)))
    P.append(polyline(z_total_pts, color=NEG, sw=3.2))

    # Лінія Z_target = 5 мОм
    z_target = 0.005
    y_zt = z_to_y(z_target)
    P.append(line(x_min, y_zt, x_max, y_zt, color=POS, sw=2.2, dash="8,4"))
    P.append(rect(x_max - 180, y_zt - 22, 175, 20, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    P.append(text(x_max - 92, y_zt - 8, "Z_target = 5 мОм (макс)", size=11, color=POS, bold=True, anchor="middle"))

    # Підписи окремих кривих
    P.append(text(f_to_x(800.0), z_to_y(0.0012), "VRM", size=11, color="#5a6e7f", bold=True, anchor="middle"))
    P.append(text(f_to_x(6e4), z_to_y(0.008), "Bulk C", size=11, color="#b45309", bold=True, anchor="middle"))
    P.append(text(f_to_x(3e6), z_to_y(0.0018), "MLCC", size=11, color="#15803d", bold=True, anchor="middle"))
    P.append(text(f_to_x(7e7), z_to_y(0.0028), "Площини", size=11, color="#7e22ce", bold=True, anchor="middle"))
    P.append(text(f_to_x(5e8), z_to_y(0.0075), "On-Die", size=11, color="#be185d", bold=True, anchor="middle"))

    # Результуюча Z_PDN
    P.append(rect(f_to_x(2e5) - 65, z_to_y(0.0035) - 24, 130, 20, fill="#e0e7ff", stroke=NEG, sw=1.2, rx=4))
    P.append(text(f_to_x(2e5), z_to_y(0.0035) - 10, "Z_PDN (сумарний)", size=11, color=NEG, bold=True, anchor="middle"))

    # Підписи осей
    P.append(text((x_min + x_max) / 2.0, H - 24, "Частота струму перемикання (f)", size=13, color=INK, bold=True, anchor="middle"))
    P.append(text(30.0, (y_min + y_max) / 2.0, "Імпеданс |Z|", size=13, color=INK, bold=True, anchor="middle"))

    render(os.path.join(IMG, "pdn-impedance-profile.svg"), W, H, *P,
           title="Частотний профіль імпедансу PDN: ієрархія 4 рівнів розв'язки під лінією Z_target")


# ── Фігура 2: Утворення антирезонансного піку та демпфування ────────────────
def fig_anti_resonance():
    W, H = 940, 560
    P = []

    w_left = 370
    w_right = 530

    # ── Ліва панель ──
    x_l_mid = 185.0
    P.append(rect(20, 70, w_left - 10, 465, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    P.append(text(x_l_mid, 95, "Механізм утворення антирезонансу", size=13, color=INK, bold=True, anchor="middle"))

    # Верхня шина живлення VDD
    P.append(line(45, 130, 325, 130, color=POS, sw=3.0))
    P.append(text(45, 120, "VDD (Шина живлення)", size=11, color=POS, bold=True, anchor="start"))

    # Нижня шина землі GND
    P.append(line(45, 335, 325, 335, color=NEG, sw=3.0))
    P.append(text(45, 352, "GND (Площина землі)", size=11, color=NEG, bold=True, anchor="start"))

    # Гілка 1: C1 (10 мкФ)
    x_g1 = 115.0
    P.append(line(x_g1, 130, x_g1, 150, color=LINE, sw=1.8))
    P.append(rect(x_g1 - 32, 150, 64, 40, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    P.append(text(x_g1, 167, "L_eff1", size=11, color="#b45309", bold=True, anchor="middle"))
    P.append(text(x_g1, 182, "ESL=1.2 нГн", size=9.5, color=MUTED, anchor="middle"))

    P.append(rect(x_g1 - 32, 198, 64, 32, fill="#fff", stroke=LINE, sw=1.3, rx=4))
    P.append(text(x_g1, 218, "ESR1 (5 мОм)", size=10, color=INK, anchor="middle"))
    P.append(line(x_g1, 230, x_g1, 335, color=LINE, sw=1.8))

    # Підпис гілки 1 в окремому боксі ліворуч, щоб не перетинати провідники
    P.append(rect(30, 250, 75, 42, fill="#fff", stroke="#d97706", sw=1.0, rx=4))
    P.append(text(67.5, 267, "C1: 10 мкФ", size=10, color="#b45309", bold=True, anchor="middle"))
    P.append(text(67.5, 283, "індуктивна", size=9.0, color=MUTED, anchor="middle"))

    # Гілка 2: C2 (100 нФ)
    x_g2 = 255.0
    P.append(line(x_g2, 130, x_g2, 150, color=LINE, sw=1.8))
    P.append(rect(x_g2 - 32, 150, 64, 40, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    P.append(text(x_g2, 167, "C_eff2", size=11, color="#15803d", bold=True, anchor="middle"))
    P.append(text(x_g2, 182, "C = 100 нФ", size=9.5, color=MUTED, anchor="middle"))

    P.append(rect(x_g2 - 32, 198, 64, 32, fill="#fff", stroke=LINE, sw=1.3, rx=4))
    P.append(text(x_g2, 218, "ESR2 (10 мОм)", size=10, color=INK, anchor="middle"))
    P.append(line(x_g2, 230, x_g2, 335, color=LINE, sw=1.8))

    # Підпис гілки 2 в окремому боксі праворуч
    P.append(rect(265, 250, 75, 42, fill="#fff", stroke="#16a34a", sw=1.0, rx=4))
    P.append(text(302.5, 267, "C2: 100 нФ", size=10, color="#15803d", bold=True, anchor="middle"))
    P.append(text(302.5, 283, "ємнісна", size=9.0, color=MUTED, anchor="middle"))

    # Циркулюючий струм
    P.append(line(x_g1 + 36, 170, x_g2 - 36, 170, color=POS, sw=2.0, dash="4,3"))
    P.append(head(x_g2 - 36, 170, 0, POS, size=6))
    P.append(line(x_g2 - 36, 214, x_g1 + 36, 214, color=POS, sw=2.0, dash="4,3"))
    P.append(head(x_g1 + 36, 214, 180, POS, size=6))

    P.append(rect(x_l_mid - 85, 370, 170, 70, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    P.append(text(x_l_mid, 388, "Паралельний LC-контур:", size=11, color=POS, bold=True, anchor="middle"))
    P.append(text(x_l_mid, 406, "f_anti ≈ 1 / (2π√(L1 · C2))", size=10.5, color=INK, bold=True, anchor="middle"))
    P.append(text(x_l_mid, 424, "зовнішній імпеданс ЗРОСТАЄ", size=10, color=POS, bold=True, anchor="middle"))

    P.append(rect(x_l_mid - 110, 452, 220, 68, fill="#eff6ff", stroke=NEG, sw=1.0, rx=4))
    P.append(text(x_l_mid, 470, "Методи приборкання піка:", size=10.5, color=NEG, bold=True, anchor="middle"))
    P.append(text(x_l_mid, 488, "• Контрольований ESR (демпфування)", size=9.5, color=INK, anchor="middle"))
    P.append(text(x_l_mid, 506, "• Зближення номіналів або однакові C", size=9.5, color=INK, anchor="middle"))

    # ── Права панель: Графік ──
    gx_min, gx_max = 445.0, 905.0
    gy_min, gy_max = 85.0, 480.0

    gf_min, gf_max = 5.0, 8.5
    gz_min, gz_max = -3.5, 0.5

    def gfx_to_x(f_val):
        lf = math.log10(max(1e5, f_val))
        return gx_min + (lf - gf_min) / (gf_max - gf_min) * (gx_max - gx_min)

    def gfy_to_y(z_val):
        lz = math.log10(max(3e-4, min(3.0, z_val)))
        return gy_max - (lz - gz_min) / (gz_max - gz_min) * (gy_max - gy_min)

    # Сітка
    g_fticks = [(1e5, "100 кГц"), (1e6, "1 МГц"), (1e7, "10 МГц"), (1e8, "100 МГц")]
    for ft, flab in g_fticks:
        xv = gfx_to_x(ft)
        P.append(line(xv, gy_min, xv, gy_max, color="#e5e9f0", sw=1.0))
        P.append(text(xv, gy_max + 18, flab, size=11, color=MUTED, anchor="middle"))

    g_zticks = [(1e-3, "1 мОм"), (1e-2, "10 мОм"), (1e-1, "100 мОм"), (1.0, "1 Ом")]
    for zt, zlab in g_zticks:
        yv = gfy_to_y(zt)
        P.append(line(gx_min, yv, gx_max, yv, color="#e5e9f0", sw=1.0))
        P.append(text(gx_min - 8, yv + 4, zlab, size=11, color=MUTED, anchor="end"))

    P.append(rect(gx_min, gy_min, gx_max - gx_min, gy_max - gy_min, fill="none", stroke="#b0b8c4", sw=1.2, rx=0))

    g_freqs = [10 ** (gf_min + i * (gf_max - gf_min) / 300.0) for i in range(301)]

    # C1
    c1, esr1, esl1 = 10e-6, 0.005, 1.2e-9
    zc1_pts = []
    for f in g_freqs:
        w = 2.0 * math.pi * f
        zc1_pts.append((gfx_to_x(f), gfy_to_y(abs(complex(esr1, w * esl1 - 1.0 / (w * c1))))))
    P.append(polyline(zc1_pts, color="#d97706", sw=1.5, dash="4,3"))
    P.append(text(gfx_to_x(3e5), gfy_to_y(0.04), "Z_C1 (10 мкФ)", size=10.5, color="#b45309", bold=True, anchor="middle"))

    # C2
    c2, esr2, esl2 = 100e-9, 0.010, 0.6e-9
    zc2_pts = []
    for f in g_freqs:
        w = 2.0 * math.pi * f
        zc2_pts.append((gfx_to_x(f), gfy_to_y(abs(complex(esr2, w * esl2 - 1.0 / (w * c2))))))
    P.append(polyline(zc2_pts, color="#16a34a", sw=1.5, dash="4,3"))
    P.append(text(gfx_to_x(1.2e8), gfy_to_y(0.04), "Z_C2 (100 нФ)", size=10.5, color="#15803d", bold=True, anchor="middle"))

    # 1. Недемпфований
    z_undamped_pts = []
    for f in g_freqs:
        w = 2.0 * math.pi * f
        z1 = complex(esr1, w * esl1 - 1.0 / (w * c1))
        z2 = complex(esr2, w * esl2 - 1.0 / (w * c2))
        z_par = abs((z1 * z2) / (z1 + z2))
        z_undamped_pts.append((gfx_to_x(f), gfy_to_y(z_par)))
    P.append(polyline(z_undamped_pts, color=POS, sw=2.6))

    # 2. Демпфований
    z_damped_pts = []
    esr1_damped = 0.035
    c_mid, esr_mid, esl_mid = 1e-6, 0.020, 0.8e-9
    for f in g_freqs:
        w = 2.0 * math.pi * f
        y_d = 1.0 / complex(esr1_damped, w * esl1 - 1.0 / (w * c1))
        y_d += 1.0 / complex(esr2, w * esl2 - 1.0 / (w * c2))
        y_d += 1.0 / complex(esr_mid, w * esl_mid - 1.0 / (w * c_mid))
        z_damped_pts.append((gfx_to_x(f), gfy_to_y(abs(1.0 / y_d))))
    P.append(polyline(z_damped_pts, color=FIELD, sw=2.8))

    # Лінія Z_target = 15 мОм
    z_tgt = 0.015
    y_ztgt = gfy_to_y(z_tgt)
    P.append(line(gx_min, y_ztgt, gx_max, y_ztgt, color=LINE, sw=1.8, dash="6,4"))
    P.append(text(gx_min + 10, y_ztgt - 8, "Z_target = 15 мОм", size=11, color=LINE, bold=True, anchor="start"))

    # Позначення піка
    f_peak = 4.8e6
    x_pk = gfx_to_x(f_peak)
    y_pk = gfy_to_y(0.35)
    P.append(circle(x_pk, y_pk, 5.0, fill="#fee2e2", stroke=POS, sw=2.0))
    P.append(line(x_pk, y_pk - 8, x_pk, y_pk - 38, color=POS, sw=1.5))
    P.append(rect(x_pk - 80, y_pk - 64, 160, 26, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    P.append(text(x_pk, y_pk - 47, "Антирезонансний пік!", size=10.5, color=POS, bold=True, anchor="middle"))

    # Позначення згладженої кривої
    P.append(rect(gfx_to_x(1.2e7) - 75, gfy_to_y(0.004) - 22, 150, 22, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    P.append(text(gfx_to_x(1.2e7), gfy_to_y(0.004) - 7, "Демпфована крива (OK)", size=10.5, color=FIELD, bold=True, anchor="middle"))

    # Осі
    P.append(text((gx_min + gx_max) / 2.0, H - 24, "Частота (f)", size=13, color=INK, bold=True, anchor="middle"))

    render(os.path.join(IMG, "pdn-anti-resonance.svg"), W, H, *P,
           title="Утворення антирезонансного піку між двома конденсаторами та його демпфування")


if __name__ == '__main__':
    fig_pdn_profile()
    fig_anti_resonance()
    print("SVG figures generated in img/")
