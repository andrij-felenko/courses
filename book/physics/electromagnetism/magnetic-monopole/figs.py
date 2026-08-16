# -*- coding: utf-8 -*-
"""Фігури до теми «Магнітний монополь».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Асиметрія рівнянь Максвелла та її відновлення монополем ──────────
def fig_duality():
    W, H = 740, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Асиметрія рівнянь Максвелла та дуальне розширення", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 48, midx, H - 44, color="#d6dde6", sw=1.4, dash="5,5"))

    # Зліва: Класичні рівняння (без монополів)
    cx1 = midx / 2
    f.append(text(cx1, 54, "Класичні рівняння (без монополів)", size=13, bold=True, color=INK))

    eqs_left = [
        "∇ · E = ρ_e / ε₀",
        "∇ · B = 0   [немає магнітних зарядів]",
        "∇ × E = − ∂B / ∂t",
        "∇ × B = μ₀ J_e + μ₀ ε₀ ∂E / ∂t"
    ]
    y_start = 85
    for i, eq in enumerate(eqs_left):
        bg = "#fff5f5" if i == 1 else "#f4f6f9"
        st = "#e53e3e" if i == 1 else "#cbd5e1"
        b, w, h = textbox(cx1, y_start + i * 48, eq, size=12, pad=7, fill=bg, stroke=st, sw=1.2)
        f.append(b)

    # Справа: Симетричні дуальні рівняння (з магнітним зарядом)
    cx2 = midx + midx / 2
    f.append(text(cx2, 54, "Дуально-симетричні (з магнітним зарядом)", size=13, bold=True, color=INK))

    eqs_right = [
        "∇ · E = ρ_e / ε₀",
        "∇ · B = μ₀ ρ_m   [магнітна густина ρ_m]",
        "∇ × E = − μ₀ J_m − ∂B / ∂t   [магнітний струм J_m]",
        "∇ × B = μ₀ J_e + μ₀ ε₀ ∂E / ∂t"
    ]
    for i, eq in enumerate(eqs_right):
        bg = "#edf2ff" if i in (1, 2) else "#f4f6f9"
        st = "#3b82f6" if i in (1, 2) else "#cbd5e1"
        b, w, h = textbox(cx2, y_start + i * 48, eq, size=12, pad=7, fill=bg, stroke=st, sw=1.2)
        f.append(b)

    b_bot, w_b, h_b = textbox(W / 2, H - 18, "Симетрія дуальності: E → B, B → −E, ρ_e → ρ_m, ρ_m → −ρ_e", size=11, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.2)
    f.append(b_bot)

    return render(os.path.join(IMG, "fig1-duality-asymmetry.svg"), W, H, *f)


# ── Фігура 2: Струна Дірака та перекриття потенціалів ───────────────────────
def fig_dirac_string():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Геометрія струни Дірака та калібрувальні патчі UN, US", size=16, bold=True))

    cx, cy = 230, 190
    r_sphere = 100

    # Сфера і соленоїдна струна
    f.append(circle(cx, cy, r_sphere, fill="#f8fafc", stroke=LINE, sw=1.6))

    # Радіальні лінії магнітного поля
    angles = [0, 45, 90, 135, 180, 225, 315]
    for a in angles:
        rad = math.radians(a)
        x1 = cx + 18 * math.cos(rad)
        y1 = cy - 18 * math.sin(rad)
        x2 = cx + (r_sphere + 22) * math.cos(rad)
        y2 = cy - (r_sphere + 22) * math.sin(rad)
        f.append(arrow(x1, y1, x2, y2, color=POS, sw=1.4))

    # Струна Дірака уздовж від'ємної осі z (донизу)
    f.append(line(cx, cy, cx, cy + r_sphere + 50, color=NEG, sw=3.5))
    f.append(circle(cx, cy, 14, fill="#ef4444", stroke=INK, sw=1.5))
    f.append(text(cx, cy + 4, "g", size=12, bold=True, color="#ffffff"))

    # Підпис струни
    b_str, w_s, h_s = textbox(cx, cy + r_sphere + 68, "Струна Дірака (сингулярність A_N)", size=11, pad=5, fill="#fee2e2", stroke=NEG, sw=1.2)
    f.append(b_str)

    # Північний та південний патчі
    f.append(text(cx - r_sphere - 30, cy - 40, "Патч UN", size=12, bold=True, color="#2563eb"))
    f.append(text(cx - r_sphere - 30, cy - 25, "(без струни донизу)", size=10, color=MUTED))

    f.append(text(cx - r_sphere - 30, cy + 40, "Патч US", size=12, bold=True, color="#059669"))
    f.append(text(cx - r_sphere - 30, cy + 55, "(без струни догори)", size=10, color=MUTED))

    # Права панель: умови квантування
    px = 530
    f.append(rect(px - 140, 52, 270, 295, fill="#f8fafc", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(px, 74, "Калібрувальне узгодження", size=13, bold=True, color=INK))

    lines_info = [
        "У зоні перекриття (екватор):",
        "A_N − A_S = ∇ Λ",
        "",
        "Фазовий множник хвильової функції:",
        "exp(i q Λ / ℏ) мусить бути",
        "однозначним при 2π обході:",
        "",
        "q · g = 2 · π · ℏ · n",
        "",
        "Отже, існування хоча б одного g",
        "пояснює квантування заряду q!"
    ]
    for i, line_txt in enumerate(lines_info):
        if line_txt == "q · g = 2 · π · ℏ · n":
            b_q, w_q, h_q = textbox(px, 98 + i * 21, line_txt, size=13, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
            f.append(b_q)
        else:
            is_bold = "існування" in line_txt or "однозначним" in line_txt
            col = INK if is_bold else MUTED
            f.append(text(px, 98 + i * 21, line_txt, size=11, bold=is_bold, color=col))

    return render(os.path.join(IMG, "fig2-dirac-string.svg"), W, H, *f)


# ── Фігура 3: Солітонний монополь 'т Гоофта — Полякова ─────────────────────
def fig_thooft_polyakov():
    W, H = 720, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Топологічний монополь 'т Гоофта — Полякова (GUT-солітон)", size=16, bold=True))

    gx, gy = 60, 265
    gw, gh = 310, 190

    # Осі координат
    f.append(arrow(gx, gy, gx + gw + 20, gy, color=LINE, sw=1.5))
    f.append(arrow(gx, gy, gx, gy - gh - 15, color=LINE, sw=1.5))
    f.append(text(gx + gw + 25, gy + 4, "r", size=13, bold=True))
    f.append(text(gx - 10, gy - gh - 10, "Величина", size=11, bold=True))

    # Лінія r = rc
    rc_x = gx + 75
    f.append(line(rc_x, gy, rc_x, gy - gh, color="#cbd5e1", sw=1.2, dash="4,4"))
    f.append(text(rc_x, gy + 18, "r_c ≈ 1/M_W", size=11, color=MUTED))

    # Крива Хіггса φ(r) та крива поля B(r)
    pts_phi = []
    pts_b = []
    for i in range(101):
        r_val = i / 100.0 * 3.2
        x_p = gx + (r_val / 3.2) * gw
        y_phi_val = math.tanh(r_val / 0.8)
        y_p_phi = gy - y_phi_val * (gh * 0.75)
        pts_phi.append(f"{x_p:.1f},{y_p_phi:.1f}")

        y_b_val = 1.0 / (1.0 + (r_val / 0.8)**2)
        y_p_b = gy - y_b_val * (gh * 0.85)
        pts_b.append(f"{x_p:.1f},{y_p_b:.1f}")

    def path_tag(d, fill="none", stroke=LINE, sw=1.5):
        return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)

    f.append(path_tag(f"M {pts_phi[0]} L " + " L ".join(pts_phi[1:]), fill="none", stroke="#2563eb", sw=2.2))
    f.append(path_tag(f"M {pts_b[0]} L " + " L ".join(pts_b[1:]), fill="none", stroke="#ef4444", sw=2.2))

    f.append(text(gx + gw - 30, gy - gh * 0.75 - 10, "Поле Хіггса ⟨φ(r)⟩", size=11, bold=True, color="#2563eb"))
    f.append(text(gx + gw - 30, gy - gh * 0.20, "Поле B(r) ∝ 1/r²", size=11, bold=True, color="#ef4444"))

    # Схема структури ядра зліва / справа
    sx, sy = 540, 165
    f.append(circle(sx, sy, 85, fill="#edf2ff", stroke="#3b82f6", sw=1.5))
    f.append(circle(sx, sy, 28, fill="#fee2e2", stroke="#ef4444", sw=1.5))

    f.append(text(sx, sy - 5, "Ядро r < r_c", size=11, bold=True, color="#b91c1c"))
    f.append(text(sx, sy + 10, "SU(2) симетрія", size=10, color="#b91c1c"))

    f.append(text(sx, sy - 55, "Асимптотика r ≫ r_c", size=11, bold=True, color="#1e40af"))
    f.append(text(sx, sy - 40, "U(1) поле Дірака", size=10, color="#1e40af"))

    b_info, w_i, h_i = textbox(W / 2, H - 18, "Маса монополя M_m ≈ M_X / α ≈ 10¹⁶ GeV — гладка солітонна конфігурація без сингулярностей!", size=11, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.2)
    f.append(b_info)

    return render(os.path.join(IMG, "fig3-thooft-polyakov.svg"), W, H, *f)


# ── Фігура 4: Квазічастинкові монополі у спіновому льоду ───────────────────
def fig_spin_ice():
    W, H = 740, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Утворення емерджентних магнітних монополів у спіновому льоду", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 48, midx, H - 44, color="#d6dde6", sw=1.4, dash="5,5"))

    # Зліва: Основний стан ("Правило льоду" 2-in / 2-out)
    cx1 = midx / 2
    f.append(text(cx1, 52, "Основний стан (правило льоду: 2-in / 2-out)", size=13, bold=True, color=INK))

    tx1, ty1 = cx1, 145
    f.append(circle(tx1, ty1, 45, fill="#f1f5f9", stroke=LINE, sw=1.5))
    f.append(circle(tx1, ty1, 6, fill=INK, stroke=INK, sw=1))

    f.append(arrow(tx1 - 40, ty1 - 40, tx1 - 12, ty1 - 12, color=POS, sw=2.0))
    f.append(arrow(tx1 + 40, ty1 - 40, tx1 + 12, ty1 - 12, color=POS, sw=2.0))
    f.append(arrow(tx1 + 12, ty1 + 12, tx1 + 40, ty1 + 40, color=NEG, sw=2.0))
    f.append(arrow(tx1 - 12, ty1 + 12, tx1 - 40, ty1 + 40, color=NEG, sw=2.0))

    b_l1, w1, h1 = textbox(cx1, 235, "Заряд вузла q_m = 0", size=12, pad=6, fill="#f4f6f9", stroke="#cbd5e1", sw=1.2)
    f.append(b_l1)
    f.append(text(cx1, 275, "Тетраедр нейтральний", size=11, color=MUTED))

    # Справа: Перевертання спіну -> два квазічастинкові монополі (+q_m та -q_m)
    cx2 = midx + midx / 2
    f.append(text(cx2, 52, "Збуджений стан (перевертання спіну)", size=13, bold=True, color=INK))

    txA, tyA = cx2 - 65, 145
    txB, tyB = cx2 + 65, 145

    f.append(circle(txA, tyA, 42, fill="#fee2e2", stroke="#ef4444", sw=1.5))
    f.append(circle(txB, tyB, 42, fill="#dbeafe", stroke="#2563eb", sw=1.5))

    f.append(line(txA, tyA, txB, tyB, color=NEG, sw=2.5, dash="4,3"))
    f.append(arrow(txA + 10, tyA, txB - 10, tyB, color=NEG, sw=2.2))

    f.append(circle(txA, tyA, 14, fill="#ef4444", stroke=INK, sw=1.2))
    f.append(text(txA, tyA + 4, "+q_m", size=11, bold=True, color="#ffffff"))

    f.append(circle(txB, tyB, 14, fill="#2563eb", stroke=INK, sw=1.2))
    f.append(text(txB, tyB + 4, "−q_m", size=11, bold=True, color="#ffffff"))

    b_l2, w2, h2 = textbox(cx2, 235, "3-in / 1-out (+q_m)   і   1-in / 3-out (−q_m)", size=11, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.2, bold=True)
    f.append(b_l2)
    f.append(text(cx2, 275, "Монополі розділяються, розтягуючи струну Дірака", size=11, color=MUTED))

    return render(os.path.join(IMG, "fig4-spin-ice-quasiparticle.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_duality()
    p2 = fig_dirac_string()
    p3 = fig_thooft_polyakov()
    p4 = fig_spin_ice()
    print("written:")
    for p in (p1, p2, p3, p4):
        print("  ", p)
