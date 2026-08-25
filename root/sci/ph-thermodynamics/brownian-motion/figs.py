# -*- coding: utf-8 -*-
"""Фігури до теми «Броунівський рух».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Механізм молекулярного бомбардування ──────────────────────────
def fig_mechanism():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    # Заголовок
    f.append(text(W / 2, 28, "Мікроскопічний механізм броунівського руху", size=16, bold=True))
    f.append(text(W / 2, 48, "Некомпенсовані удари молекул середовища створюють випадкову силу", size=12, color=MUTED))

    # Дві панелі: (А) Локальні зіткнення, (Б) Сумарна траєкторія
    pw = 340
    ph = 280
    py = 68

    # --- Панель А ---
    px1 = 28
    f.append(rect(px1, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px1 + pw / 2, py + 22, "А. Миттєвий дисбаланс ударів", size=13, bold=True, color=INK))

    cx1, cy1 = px1 + pw / 2, py + ph / 2 + 10
    # Броунівська частинка (велика)
    f.append(circle(cx1, cy1, 42, fill="#e8f0fe", stroke="#1a73e8", sw=2.5))
    f.append(text(cx1, cy1 + 4, "броунівська\nчастинка", size=11, bold=True, color="#1557b0"))

    # Малі молекули з векторами швидкостей
    molecules = [
        (cx1 - 85, cy1 - 40, 24, 12, "#ea4335"),
        (cx1 - 70, cy1 + 55, 18, -15, "#ea4335"),
        (cx1 - 90, cy1 + 10, 28, -4, "#ea4335"),
        (cx1 - 60, cy1 - 75, 14, 22, "#ea4335"),
        (cx1 + 80, cy1 - 30, -16, 8, "#34a853"),
        (cx1 + 65, cy1 + 65, -12, -18, "#34a853"),
        (cx1 + 75, cy1 + 15, -15, -5, "#34a853"),
        (cx1 + 10, cy1 - 85, -5, 25, "#ea4335"),
        (cx1 - 15, cy1 + 90, 8, -26, "#ea4335"),
        (cx1 + 20, cy1 + 85, -6, -22, "#34a853"),
    ]
    for mx, my, vx, vy, col in molecules:
        f.append(circle(mx, my, 7, fill=col, stroke='none'))
        f.append(arrow(mx, my, mx + vx, my + vy, color=col, sw=1.6))

    # Результуючий вектор імпульсу / сили F_rnd(t)
    f.append(arrow(cx1, cy1, cx1 - 65, cy1 - 45, color="#d93025", sw=3.0))
    body, _, _ = textbox(cx1 - 95, cy1 - 60, "F_rnd(t)", size=12, bold=True, color="#d93025", pad=3, fill="#fce8e6", stroke="#f5c2c7", sw=1.0)
    f.append(body)

    # --- Панель Б ---
    px2 = 392
    f.append(rect(px2, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px2 + pw / 2, py + 22, "Б. Випадкова траєкторія (Random Walk)", size=13, bold=True, color=INK))

    # Траєкторія
    nodes = [
        (px2 + 40, py + ph - 40),
        (px2 + 80, py + ph - 80),
        (px2 + 65, py + ph - 130),
        (px2 + 120, py + ph - 110),
        (px2 + 150, py + ph - 170),
        (px2 + 110, py + ph - 210),
        (px2 + 180, py + ph - 230),
        (px2 + 230, py + ph - 190),
        (px2 + 210, py + ph - 130),
        (px2 + 270, py + ph - 100),
        (px2 + 300, py + ph - 140),
    ]
    for i in range(len(nodes) - 1):
        x1, y1 = nodes[i]
        x2, y2 = nodes[i + 1]
        f.append(line(x1, y1, x2, y2, color="#1a73e8", sw=2.0))
        f.append(circle(x1, y1, 4, fill="#1557b0", stroke='none'))
    f.append(circle(nodes[-1][0], nodes[-1][1], 4, fill="#1557b0", stroke='none'))

    # Початкова та кінцева точка
    f.append(circle(nodes[0][0], nodes[0][1], 7, fill="#34a853", stroke=INK, sw=1.2))
    f.append(text(nodes[0][0] + 18, nodes[0][1] + 12, "старт", size=11, bold=True, color="#188038"))

    f.append(circle(nodes[-1][0], nodes[-1][1], 7, fill="#d93025", stroke=INK, sw=1.2))
    f.append(text(nodes[-1][0] - 22, nodes[-1][1] - 10, "фініш", size=11, bold=True, color="#b31412"))

    # Вектор зсуву R
    f.append(arrow(nodes[0][0], nodes[0][1], nodes[-1][0], nodes[-1][1], color="#f9ab00", sw=2.2))
    body, _, _ = textbox((nodes[0][0] + nodes[-1][0]) / 2 + 15, (nodes[0][1] + nodes[-1][1]) / 2 + 15, "r(t)", size=12, bold=True, color="#b06000", pad=3, fill="#fef7e0", stroke="#fce8b2", sw=1.0)
    f.append(body)

    return render(os.path.join(IMG, "brownian-mechanism.svg"), W, H, *f)


# ── Фігура 2: Балістичний та дифузійний режими Ланжевена ───────────────────
def fig_regimes():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Динаміка зсуву: від інерційного польоту до дифузії", size=16, bold=True))
    f.append(text(W / 2, 45, "Залежність середнього квадрата зсуву <x²(t)> від часу t у логарифмічному масштабі", size=12, color=MUTED))

    # Вісі графіку
    ox, oy = 90, H - 50
    gx_w, gy_h = 560, 230

    f.append(arrow(ox, oy, ox + gx_w + 20, oy, color=LINE, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - gy_h - 20, color=LINE, sw=1.8))

    f.append(text(ox + gx_w + 30, oy + 4, "час t (log)", size=12, bold=True, anchor="start"))
    f.append(text(ox, oy - gy_h - 28, "<x²(t)> (log)", size=12, bold=True))

    # Вертикальна лінія релаксації імпульсу tau_p
    tau_x = ox + 220
    f.append(line(tau_x, oy, tau_x, oy - gy_h, color="#ea4335", sw=1.5, dash="5,5"))
    body, _, _ = textbox(tau_x, oy + 22, "t = τ_p = m/γ (час релаксації)", size=11, bold=True, color="#c5221f", pad=4, fill="#fce8e6", stroke="#f5c2c7", sw=1.0)
    f.append(body)

    # Крива MSD
    p1 = (ox, oy - 20)
    p2 = (tau_x, oy - 120)
    p3 = (ox + gx_w, oy - 210)

    f.append(line(p1[0], p1[1], p2[0], p2[1], color="#1a73e8", sw=3.0))
    f.append(line(p2[0], p2[1], p3[0], p3[1], color="#1a73e8", sw=3.0))

    # Позначення режимів
    body1, _, _ = textbox(ox + 100, oy - 100, "Балістичний режим\n<x²> ≈ v_th² · t²  (нахил 2)", size=11, bold=True, color="#1557b0", pad=6, fill="#e8f0fe", stroke="#aecbfa", sw=1.0)
    f.append(body1)

    body2, _, _ = textbox(ox + 410, oy - 180, "Дифузійний режим (закон Ейнштейна)\n<x²> = 2 D t  (нахил 1)", size=11, bold=True, color="#1557b0", pad=6, fill="#e8f0fe", stroke="#aecbfa", sw=1.0)
    f.append(body2)

    f.append(text(ox + 90, oy - 20, "короткі часи: t << τ_p", size=10, color=MUTED))
    f.append(text(ox + 420, oy - 110, "довгі часи: t >> τ_p", size=10, color=MUTED))

    return render(os.path.join(IMG, "langevin-regimes.svg"), W, H, *f)


# ── Фігура 3: Експеримент Перрена та розпливання розмитого ансамблю ─────────
def fig_perrin_diffusion():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Еволюція гаусового ансамблю та седиментаційна рівновага", size=16, bold=True))
    f.append(text(W / 2, 46, "Від точкового джерела до гаусової хмари й седиментаційного профілю Перрена", size=12, color=MUTED))

    pw = 340
    ph = 270
    py = 68

    # --- Панель А: Розпливання плями ---
    px1 = 28
    f.append(rect(px1, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px1 + pw / 2, py + 20, "А. Розширення розподілу P(x,t)", size=13, bold=True, color=INK))

    ox1, oy1 = px1 + 40, py + ph - 40
    f.append(arrow(ox1, oy1, ox1 + 270, oy1, color=LINE, sw=1.5))
    f.append(arrow(ox1, oy1, ox1, py + 45, color=LINE, sw=1.5))
    f.append(text(ox1 + 280, oy1 + 4, "x", size=12, bold=True))
    f.append(text(ox1 - 10, py + 40, "P(x)", size=12, bold=True))

    cx = ox1 + 130
    g1_pts = [(cx - 20, oy1 - 5), (cx - 10, oy1 - 40), (cx, oy1 - 140), (cx + 10, oy1 - 40), (cx + 20, oy1 - 5)]
    for i in range(len(g1_pts)-1):
        f.append(line(g1_pts[i][0], g1_pts[i][1], g1_pts[i+1][0], g1_pts[i+1][1], color="#d93025", sw=2.0))
    f.append(text(cx + 8, oy1 - 145, "t₁", size=11, bold=True, color="#d93025"))

    g2_pts = [(cx - 50, oy1 - 5), (cx - 25, oy1 - 30), (cx, oy1 - 80), (cx + 25, oy1 - 30), (cx + 50, oy1 - 5)]
    for i in range(len(g2_pts)-1):
        f.append(line(g2_pts[i][0], g2_pts[i][1], g2_pts[i+1][0], g2_pts[i+1][1], color="#f9ab00", sw=2.0))
    f.append(text(cx + 12, oy1 - 85, "t₂ > t₁", size=11, bold=True, color="#b06000"))

    g3_pts = [(cx - 90, oy1 - 5), (cx - 45, oy1 - 20), (cx, oy1 - 45), (cx + 45, oy1 - 20), (cx + 90, oy1 - 5)]
    for i in range(len(g3_pts)-1):
        f.append(line(g3_pts[i][0], g3_pts[i][1], g3_pts[i+1][0], g3_pts[i+1][1], color="#1a73e8", sw=2.0))
    f.append(text(cx + 20, oy1 - 48, "t₃ > t₂", size=11, bold=True, color="#1557b0"))

    # --- Панель Б: Дослід Перрена ---
    px2 = 392
    f.append(rect(px2, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px2 + pw / 2, py + 20, "Б. Граводіфузійна рівновага Перрена", size=13, bold=True, color=INK))

    vx, vy, vw, vh = px2 + 40, py + 50, 110, 170
    f.append(rect(vx, vy, vw, vh, fill="#e8f0fe", stroke="#aecbfa", sw=1.5, rx=4))
    f.append(line(vx, vy + 20, vx + vw, vy + 20, color="#76a7fa", sw=1.2, dash="4,4"))

    import random
    rng = random.Random(42)
    for _ in range(45):
        h_val = int(150 * (rng.random() ** 2.2))
        px = vx + 10 + rng.random() * (vw - 20)
        py_pt = vy + vh - 10 - h_val
        f.append(circle(px, py_pt, 3.5, fill="#ea4335", stroke='none'))

    ox2, oy2 = px2 + 185, py + ph - 40
    f.append(arrow(ox2, oy2, ox2 + 130, oy2, color=LINE, sw=1.5))
    f.append(arrow(ox2, oy2, ox2, py + 45, color=LINE, sw=1.5))
    f.append(text(ox2 + 140, oy2 + 4, "n(z)", size=11, bold=True))
    f.append(text(ox2 - 10, py + 40, "z", size=11, bold=True))

    exp_pts = []
    for step in range(11):
        fz = step / 10.0
        z_px = oy2 - fz * 160
        n_px = ox2 + 110 * math.exp(-2.3 * fz)
        exp_pts.append((n_px, z_px))
    for i in range(len(exp_pts) - 1):
        f.append(line(exp_pts[i][0], exp_pts[i][1], exp_pts[i+1][0], exp_pts[i+1][1], color="#34a853", sw=2.2))

    body, _, _ = textbox(px2 + pw / 2, py + ph - 16, "n(z) = n₀ · exp(−m_eff · g · z / k_B T)", size=11, bold=True, color="#137333", pad=4, fill="#e6f4ea", stroke="#ceead6", sw=1.0)
    f.append(body)

    return render(os.path.join(IMG, "einstein-perrin-diffusion.svg"), W, H, *f)


# ── Фігура 4: Флуктуаційно-дисипативна теорема ──────────────────────────────
def fig_fluctuation_dissipation():
    W, H = 720, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    f.append(text(W / 2, 26, "Універсальний місток: Флуктуаційно-дисипативна теорема", size=16, bold=True))
    f.append(text(W / 2, 46, "Розсіяння енергії (дисипація) неминуче породжує спонтанні теплові флуктуації", size=12, color=MUTED))

    pw = 320
    ph = 250
    py = 75

    px1 = 30
    f.append(rect(px1, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px1 + pw / 2, py + 22, "Механічна система (Рідина)", size=13, bold=True, color=INK))

    body_m1, _, _ = textbox(px1 + pw / 2, py + 65, "Дисипація: В'язке тертя γ = 6 π η a", size=11, bold=True, color="#1557b0", pad=5, fill="#e8f0fe", stroke="#aecbfa", sw=1.0)
    f.append(body_m1)
    f.append(arrow(px1 + pw / 2, py + 92, px1 + pw / 2, py + 128, color="#1a73e8", sw=2.0))
    body_m2, _, _ = textbox(px1 + pw / 2, py + 155, "Флуктуація: Випадкова сила F_rnd(t)\n<F_rnd²> = 2 γ k_B T", size=11, bold=True, color="#c5221f", pad=5, fill="#fce8e6", stroke="#f5c2c7", sw=1.0)
    f.append(body_m2)
    body_m3, _, _ = textbox(px1 + pw / 2, py + 215, "Наслідок: Дифузія D = k_B T / γ", size=11, bold=True, color="#137333", pad=5, fill="#e6f4ea", stroke="#ceead6", sw=1.0)
    f.append(body_m3)

    mid_x = W / 2
    f.append(text(mid_x, py + ph / 2, "≡", size=36, bold=True, color="#f9ab00"))
    f.append(text(mid_x, py + ph / 2 + 25, "ізоморфізм", size=11, color=MUTED))

    px2 = W - 30 - pw
    f.append(rect(px2, py, pw, ph, fill="#fcfdff", stroke=FIELD, sw=1.5, rx=10))
    f.append(text(px2 + pw / 2, py + 22, "Електрична система (Резистор)", size=13, bold=True, color=INK))

    body_e1, _, _ = textbox(px2 + pw / 2, py + 65, "Дисипація: Опір R (гальмування)", size=11, bold=True, color="#1557b0", pad=5, fill="#e8f0fe", stroke="#aecbfa", sw=1.0)
    f.append(body_e1)
    f.append(arrow(px2 + pw / 2, py + 92, px2 + pw / 2, py + 128, color="#1a73e8", sw=2.0))
    body_e2, _, _ = textbox(px2 + pw / 2, py + 155, "Флуктуація: Напруга шуму U_n(t)\n<U_n²> = 4 R k_B T B", size=11, bold=True, color="#c5221f", pad=5, fill="#fce8e6", stroke="#f5c2c7", sw=1.0)
    f.append(body_e2)
    body_e3, _, _ = textbox(px2 + pw / 2, py + 215, "Наслідок: Струмовий шум I_n² = 4 k_B T B / R", size=11, bold=True, color="#137333", pad=5, fill="#e6f4ea", stroke="#ceead6", sw=1.0)
    f.append(body_e3)

    return render(os.path.join(IMG, "fluctuation-dissipation.svg"), W, H, *f)


if __name__ == '__main__':
    fig_mechanism()
    fig_regimes()
    fig_perrin_diffusion()
    fig_fluctuation_dissipation()
    print("Всі 4 фігури успішно згенеровано у ./img/")

