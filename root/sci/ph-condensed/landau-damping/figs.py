# -*- coding: utf-8 -*-
"""Фігури до теми «Загасання Ландау в плазмі».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Фізичний механізм загасання Ландау (резонанс хвиля-частинка) ──────
def gen_fig1():
    w, h = 760, 380
    frags = []
    
    # Заголовок / Загальна рамка
    frags.append(text(w / 2, 25, "Фізичний механізм загасання Ландау", size=16, bold=True))
    
    # ── Ліва частина: Графік функції розподілу f_0(v) ──
    ox, oy = 80, 310
    gw, gh = 280, 230
    
    # Осі
    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.5))
    frags.append(text(ox + gw + 15, oy + 20, "v", size=13, italic=True))
    frags.append(text(ox - 25, oy - gh - 10, "f₀(v)", size=13, italic=True))
    
    # Крива Максвелла
    pts = []
    v_ph_val = 1.4
    for i in range(101):
        v = i / 100.0 * 3.0
        # Maxwellian-like
        f_val = math.exp(-v * v / 1.2)
        px = ox + (v / 3.0) * gw
        py = oy - f_val * (gh - 20)
        pts.append(f"{px:.1f},{py:.1f}")
    
    frags.append(path_svg("M " + " L ".join(pts), fill="none", stroke=NEG, sw=2.5))
    
    # Пунктир фазової швидкості v_ph
    vx_ph = ox + (v_ph_val / 3.0) * gw
    vy_ph = oy - math.exp(-v_ph_val * v_ph_val / 1.2) * (gh - 20)
    frags.append(line(vx_ph, oy, vx_ph, oy - gh, color=POS, sw=1.5, dash="4,4"))
    frags.append(circle(vx_ph, vy_ph, 5, fill=POS, stroke=LINE, sw=1.5))
    frags.append(text(vx_ph, oy + 20, "v_ph = ω/k", size=12, bold=True, color=POS))
    
    # Точки v1 (slower) та v2 (faster)
    dv = 0.35
    v1 = v_ph_val - dv
    v2 = v_ph_val + dv
    vx1 = ox + (v1 / 3.0) * gw
    vy1 = oy - math.exp(-v1 * v1 / 1.2) * (gh - 20)
    vx2 = ox + (v2 / 3.0) * gw
    vy2 = oy - math.exp(-v2 * v2 / 1.2) * (gh - 20)
    
    frags.append(circle(vx1, vy1, 4, fill=FIELD, stroke=LINE, sw=1.2))
    frags.append(circle(vx2, vy2, 4, fill=NEG, stroke=LINE, sw=1.2))
    
    # Стрілки поглинання/віддачі
    frags.append(arrow(vx1, vy1 - 5, vx1 + 18, vy1 - 15, color=FIELD, sw=2.0))
    frags.append(arrow(vx2, vy2 - 5, vx2 - 18, vy2 + 10, color=NEG, sw=2.0))
    
    # Нахил df0/dv < 0
    t_tang, _, _ = textbox(vx_ph + 75, vy_ph - 35, "df₀/dv < 0\n(більше частинок\nпоглинають енергію)", size=11, pad=6, fill="#fef9e7", stroke="#f39c12")
    frags.append(t_tang)
    
    # ── Права частина: Схема серфінгу частинок у хвилі E(x) ──
    rx_start = 430
    frags.append(text(rx_start + 140, 65, "Взаємодія частинок із хвилею в СК хвилі", size=13, bold=True))
    
    # Синусоїда потенціалу U(x)
    wave_pts = []
    for i in range(101):
        x = i / 100.0
        wx = rx_start + x * 280
        wy = 160 + 35 * math.sin(2 * math.pi * x * 1.5)
        wave_pts.append(f"{wx:.1f},{wy:.1f}")
    
    frags.append(path_svg("M " + " L ".join(wave_pts), fill="none", stroke="#8e44ad", sw=2.2))
    frags.append(text(rx_start + 295, 160, "U(x)", size=12, bold=True, color="#8e44ad"))
    
    # Частинка v < v_ph (доганяється хвилею -> прискорюється)
    p1_x = rx_start + 50
    p1_y = 160 + 35 * math.sin(2 * math.pi * 0.18 * 1.5)
    frags.append(circle(p1_x, p1_y, 7, fill=FIELD, stroke=LINE, sw=1.5))
    frags.append(arrow(p1_x, p1_y - 12, p1_x + 25, p1_y - 12, color=FIELD, sw=2.0))
    t_p1, _, _ = textbox(p1_x + 20, p1_y + 28, "v < v_ph: прискорюється\n(бере енергію хвилі)", size=10, pad=5, fill="#e8f8f5", stroke=FIELD)
    frags.append(t_p1)
    
    # Частинка v > v_ph (обганяє хвилю -> гальмується)
    p2_x = rx_start + 210
    p2_y = 160 + 35 * math.sin(2 * math.pi * 0.75 * 1.5)
    frags.append(circle(p2_x, p2_y, 7, fill=NEG, stroke=LINE, sw=1.5))
    frags.append(arrow(p2_x, p2_y - 12, p2_x - 25, p2_y - 12, color=NEG, sw=2.0))
    t_p2, _, _ = textbox(p2_x - 10, p2_y + 28, "v > v_ph: гальмується\n(віддає енергію хвилі)", size=10, pad=5, fill="#eaf2f8", stroke=NEG)
    frags.append(t_p2)
    
    # Підсумковий текстовий блок знизу
    t_sum, _, _ = textbox(w / 2, 345, "Оскільки df₀/dv < 0, частинок з v < v_ph завжди більше, ніж з v > v_ph.\nРезультуючий потік енергії іде від хвилі до частинок -> хвиля загасає (exp(-γt)).", size=12, pad=7, fill=FILL, stroke=LINE)
    frags.append(t_sum)
    
    return render(os.path.join(IMG_DIR, "fig1-landau-mechanism.svg"), w, h, *frags)

# ── Фігура 2: Дисперсія та декремент загасання Ландау ──────────────────────
def gen_fig2():
    w, h = 760, 360
    frags = []
    
    frags.append(text(w / 2, 25, "Дисперсія ω_r(k) та декремент загасання |γ(k)|", size=16, bold=True))
    
    ox, oy = 90, 290
    gw, gh = 580, 220
    
    # Осі
    frags.append(arrow(ox, oy, ox + gw + 35, oy, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.5))
    frags.append(text(ox + gw + 20, oy + 22, "k · λ_D", size=13, bold=True))
    frags.append(text(ox - 35, oy - gh - 5, "ω / ω_p", size=13, bold=True))
    
    # Сітка та засічки по k
    k_ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    for kt in k_ticks:
        kx = ox + kt * gw
        frags.append(line(kx, oy, kx, oy - gh, color="#e5e7eb", sw=1.0))
        frags.append(line(kx, oy, kx, oy + 5, color=LINE, sw=1.2))
        frags.append(text(kx, oy + 20, f"{kt:.1f}", size=11))
    
    # Засічки по y (ліва вісь - реальна частота ω_r/ω_p)
    w_ticks = [(1.0, 0.0), (1.2, 0.33), (1.5, 0.83)]
    for wt, rel_y in w_ticks:
        wy = oy - rel_y * gh
        frags.append(line(ox - 5, wy, ox, wy, color=LINE, sw=1.2))
        frags.append(text(ox - 18, wy + 4, f"{wt:.1f}", size=11, color=FIELD))
    
    # Крива 1: Реальна частота ω_r = ω_p * sqrt(1 + 3 (k λ_D)^2)
    wr_pts = []
    gamma_pts = []
    for i in range(101):
        k = i / 100.0
        kx = ox + k * gw
        
        # Dispersion: wr ≈ 1 + 1.5 * k^2
        wr = math.sqrt(1.0 + 3.0 * k * k)
        # Scale to graph: wr ranges 1.0 -> 2.0
        w_scaled = (wr - 1.0) / 0.6 * (gh * 0.5)
        w_y = oy - w_scaled
        wr_pts.append(f"{kx:.1f},{w_y:.1f}")
        
        # Landau damping rate: gamma = sqrt(pi/8) / (k^3) * exp(-1/(2 k^2) - 1.5)
        if k < 0.08:
            gamma = 0.0
        else:
            gamma = math.sqrt(math.pi / 8.0) / (k**3) * math.exp(-1.0 / (2.0 * k * k) - 1.5)
        
        # Cap gamma for plotting
        gamma_capped = min(gamma, 0.8)
        g_y = oy - (gamma_capped / 0.8) * (gh * 0.85)
        gamma_pts.append(f"{kx:.1f},{g_y:.1f}")
    
    frags.append(path_svg("M " + " L ".join(wr_pts), fill="none", stroke=FIELD, sw=2.5))
    frags.append(path_svg("M " + " L ".join(gamma_pts), fill="none", stroke=POS, sw=2.5, dash="6,3"))
    
    # Легенда та пояснювальні блоки
    t_wr, _, _ = textbox(ox + 130, oy - gh + 30, "Реальна частота ω_r/ω_p\n(хвилі Бома — Гросса)", size=11, pad=6, fill="#e8f8f5", stroke=FIELD)
    t_gamma, _, _ = textbox(ox + 480, oy - gh + 30, "Декремент загасання |γ|/ω_p\n(експоненціальне зростання)", size=11, pad=6, fill="#fadbd8", stroke=POS)
    frags.append(t_wr)
    frags.append(t_gamma)
    
    # Межа слабкого / сильного загасання
    k_crit_x = ox + 0.4 * gw
    frags.append(line(k_crit_x, oy, k_crit_x, oy - gh, color=MUTED, sw=1.2, dash="3,3"))
    t_zone1, _, _ = textbox(ox + 0.2 * gw, oy - 30, "Слабке загасання\n(k·λ_D << 1)", size=10, pad=4, fill=FILL, stroke=MUTED)
    t_zone2, _, _ = textbox(ox + 0.7 * gw, oy - 30, "Сильне (катастрофічне) загасання\n(k·λ_D ≳ 0.5, хвиля зникає за T)", size=10, pad=4, fill="#fdebd0", stroke="#e67e22")
    frags.append(t_zone1)
    frags.append(t_zone2)
    
    return render(os.path.join(IMG_DIR, "fig2-dispersion-damping.svg"), w, h, *frags)

# ── Фігура 3: Фазове перемішування та плазмове ехо ──────────────────────────
def gen_fig3():
    w, h = 760, 360
    frags = []
    
    frags.append(text(w / 2, 25, "Фазове перемішування та виникнення плазмового ехо", size=16, bold=True))
    
    # ── Ліва панель: Спіралізація/перемішування у фазовому просторі ──
    lx, ly = 40, 55
    lw, lh = 330, 240
    frags.append(rect(lx, ly, lw, lh, fill="#fafafa", stroke=LINE, sw=1.2))
    frags.append(text(lx + lw / 2, ly + 20, "Фазовий простір (x, v): закручування f₁(x,v,t)", size=12, bold=True))
    
    # Схематичні фазові смуги для t=0, t=1, t=3
    # t=0: вертикальні смуги f1 ~ cos(k x)
    frags.append(text(lx + 40, ly + 45, "t = 0", size=11, bold=True, color=FIELD))
    for i in range(4):
        sx = lx + 20 + i * 20
        frags.append(rect(sx, ly + 55, 10, 50, fill="#a3e4d7", stroke="none"))
    
    # t > 0: нахилені смуги через x -> x + v*t
    frags.append(text(lx + 140, ly + 45, "t > 0 (фазовий зсув)", size=11, bold=True, color=NEG))
    for i in range(5):
        sy = ly + 55 + i * 10
        d_shear = f"M {lx+120+i*6} {sy} L {lx+170+i*6} {sy+8} L {lx+165+i*6} {sy+8} Z"
        frags.append(path_svg(d_shear, fill=NEG, stroke="none"))
        frags.append(line(lx + 120, ly + 55 + i * 10, lx + 190, ly + 60 + i * 10, color=NEG, sw=1.5))
        
    # t >> 0: тонкі густі смуги (фазове перемішування, <f1> -> 0)
    frags.append(text(lx + 240, ly + 45, "t >> 0 (перемішування)", size=11, bold=True, color=POS))
    for i in range(12):
        sy = ly + 55 + i * 4
        frags.append(line(lx + 225, sy, lx + 305, sy + 2, color=POS, sw=1.0))
        
    # Пояснення розміщено всередині лівої панелі акуратно
    frags.append(text(lx + lw / 2, ly + lh - 40, "Макроскопічне поле E(t) = ∫ f₁ dv -> 0,", size=10, bold=True, color=INK))
    frags.append(text(lx + lw / 2, ly + lh - 22, "але мікроскопічні фази f₁ зберігаються!", size=10, color=MUTED))
    
    # ── Права панель: Експеримент із плазмовим ехо E(t) ──
    rx, ry = 390, 55
    rw, rh = 340, 240
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(rx + rw / 2, ry + 20, "Сигнал електричного поля E(t)", size=12, bold=True))
    
    # Осі E(t) vs t
    e_ox, e_oy = rx + 30, ry + rh - 40
    frags.append(arrow(e_ox, e_oy, e_ox + rw - 30, e_oy, color=LINE, sw=1.5))
    frags.append(arrow(e_ox, e_oy, e_ox, ry + 35, color=LINE, sw=1.5))
    frags.append(text(e_ox + rw - 25, e_oy + 18, "t", size=12, italic=True))
    frags.append(text(e_ox - 15, ry + 35, "E(t)", size=12, italic=True))
    
    # Імпульс 1 при t=0
    frags.append(line(e_ox, e_oy, e_ox, e_oy - 60, color=FIELD, sw=2.0))
    # Damping envelope 1
    env1 = []
    for i in range(40):
        t_val = i / 40.0 * 50
        ev = 60 * math.exp(-t_val / 12.0) * math.cos(2 * math.pi * t_val / 8.0)
        env1.append(f"{e_ox + t_val:.1f},{e_oy - ev:.1f}")
    frags.append(path_svg("M " + " L ".join(env1), fill="none", stroke=FIELD, sw=1.8))
    frags.append(text(e_ox + 5, e_oy - 70, "Імпульс 1 (k₁)", size=10, bold=True, color=FIELD))
    
    # Імпульс 2 при t=T
    t_T = 100
    frags.append(line(e_ox + t_T, e_oy, e_ox + t_T, e_oy - 60, color=NEG, sw=2.0))
    env2 = []
    for i in range(40):
        t_val = i / 40.0 * 50
        ev = 60 * math.exp(-t_val / 12.0) * math.cos(2 * math.pi * t_val / 6.0)
        env2.append(f"{e_ox + t_T + t_val:.1f},{e_oy - ev:.1f}")
    frags.append(path_svg("M " + " L ".join(env2), fill="none", stroke=NEG, sw=1.8))
    frags.append(text(e_ox + t_T + 5, e_oy - 70, "Імпульс 2 (k₂)", size=10, bold=True, color=NEG))
    
    # Плазмове ЕХО при t = 2T (якщо k2 = 2 k1)
    t_echo = 200
    env3 = []
    for i in range(60):
        t_val = (i - 30) / 30.0 * 30
        ev = 45 * math.exp(-(t_val**2) / 120.0) * math.cos(2 * math.pi * t_val / 7.0)
        env3.append(f"{e_ox + t_echo + t_val:.1f},{e_oy - ev:.1f}")
    frags.append(path_svg("M " + " L ".join(env3), fill="none", stroke=POS, sw=2.2))
    
    t_echo_lbl, _, _ = textbox(e_ox + t_echo, e_oy - 70, "Спонтанне ЕХО!\nt_echo = T·k₂/(k₂-k₁)", size=10, pad=4, fill="#fdebd0", stroke=POS)
    frags.append(t_echo_lbl)
    
    # Загальний підпис під фігурою
    t_bot, _, _ = textbox(w / 2, 335, "Плазмове ехо доводить оборотність рівняння Власова: фазове перемішування розкручується назад нелінійною хвилею.", size=11, pad=5, fill=FILL, stroke=LINE)
    frags.append(t_bot)
    
    return render(os.path.join(IMG_DIR, "fig3-phase-mixing-echo.svg"), w, h, *frags)

# ── Фігура 4: Захоплення частинок та баунс-коливання ────────────────────────
def gen_fig4():
    w, h = 760, 360
    frags = []
    
    frags.append(text(w / 2, 25, "Захоплення частинок у нелінійній хвилі та баунс-коливання", size=16, bold=True))
    
    # ── Ліва панель: Фазовий портрет захоплених частинок ──
    lx, ly = 40, 60
    lw, lh = 330, 250
    frags.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(lx + lw / 2, ly + 20, "Фазовий портрет у СК хвилі (x', v')", size=12, bold=True))
    
    cx, cy = lx + lw / 2, ly + lh / 2 + 10
    
    # Замкнені траєкторії захоплених частинок (еліпси/овали)
    for r_x, r_y in [(40, 20), (70, 35), (95, 50)]:
        pts = []
        for i in range(61):
            ang = i / 60.0 * 2 * math.pi
            px = cx + r_x * math.cos(ang)
            py = cy + r_y * math.sin(ang)
            pts.append(f"{px:.1f},{py:.1f}")
        frags.append(path_svg("M " + " L ".join(pts), fill="none", stroke=FIELD, sw=1.4))
    
    # Сепаратриса
    sep_pts_top = []
    sep_pts_bot = []
    for i in range(81):
        x_norm = (i - 40) / 40.0
        px = cx + x_norm * 120
        # Cosine-like separatrix
        v_sep = 65 * math.cos(x_norm * math.pi / 2.0) if abs(x_norm) <= 1.0 else 0
        sep_pts_top.append(f"{px:.1f},{cy - v_sep:.1f}")
        sep_pts_bot.append(f"{px:.1f},{cy + v_sep:.1f}")
    
    frags.append(path_svg("M " + " L ".join(sep_pts_top), fill="none", stroke=POS, sw=2.0))
    frags.append(path_svg("M " + " L ".join(sep_pts_bot), fill="none", stroke=POS, sw=2.0))
    
    # Незахоплені частинки (пролітні, хвилясті лінії зверху й знизу)
    for offset_y in [-80, -70, 70, 80]:
        pts_pass = []
        for i in range(81):
            x_norm = (i - 40) / 40.0
            px = cx + x_norm * 145
            py = cy + offset_y + 6 * math.sin(x_norm * math.pi)
            pts_pass.append(f"{px:.1f},{py:.1f}")
        frags.append(path_svg("M " + " L ".join(pts_pass), fill="none", stroke=NEG, sw=1.2, dash="4,3"))
        
    t_sep, _, _ = textbox(cx, cy, "Захоплені частинки\n(коливання з ω_b)", size=10, pad=4, fill="#e8f8f5", stroke=FIELD)
    frags.append(t_sep)
    frags.append(text(cx + 100, cy - 65, "Сепаратриса", size=10, bold=True, color=POS))
    frags.append(text(cx + 100, cy + 85, "Пролітні частинки", size=10, color=NEG))
    
    # ── Права панель: Насичення загасання E_0(t) та баунс-коливання ──
    rx, ry = 400, 60
    rw, rh = 330, 250
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=LINE, sw=1.2))
    frags.append(text(rx + rw / 2, ry + 20, "Амплітуда нелінійної хвилі E₀(t)", size=12, bold=True))
    
    e_ox, e_oy = rx + 30, ry + rh - 40
    frags.append(arrow(e_ox, e_oy, e_ox + rw - 40, e_oy, color=LINE, sw=1.5))
    frags.append(arrow(e_ox, e_oy, e_ox, ry + 35, color=LINE, sw=1.5))
    frags.append(text(e_ox + rw - 35, e_oy + 18, "t", size=12, italic=True))
    frags.append(text(e_ox - 15, ry + 35, "E₀", size=12, italic=True))
    
    # Лінійне експоненціальне загасання (пунктир)
    lin_pts = []
    for i in range(80):
        t_val = i / 80.0 * 240
        ev = 140 * math.exp(-t_val / 45.0)
        lin_pts.append(f"{e_ox + t_val:.1f},{e_oy - ev:.1f}")
    frags.append(path_svg("M " + " L ".join(lin_pts), fill="none", stroke=MUTED, sw=1.5, dash="4,4"))
    
    # Нелінійна крива з баунс-коливаннями та плато
    nonlin_pts = []
    for i in range(101):
        t_val = i / 100.0 * 250
        # Linear decay then bounce oscillations around plateau
        decay = math.exp(-t_val / 50.0)
        bounce = 0.25 * math.cos(2 * math.pi * t_val / 45.0) * math.exp(-t_val / 120.0)
        plateau = 0.35
        amp = 140 * (decay * (1.0 - plateau) + plateau + bounce)
        nonlin_pts.append(f"{e_ox + t_val:.1f},{e_oy - amp:.1f}")
        
    frags.append(path_svg("M " + " L ".join(nonlin_pts), fill="none", stroke=POS, sw=2.2))
    
    # Позначки періоду баунсу τ_b
    tb_x1 = e_ox + 45
    tb_x2 = e_ox + 90
    frags.append(line(tb_x1, e_oy - 85, tb_x1, e_oy - 105, color=FIELD, sw=1.2))
    frags.append(line(tb_x2, e_oy - 85, tb_x2, e_oy - 105, color=FIELD, sw=1.2))
    frags.append(arrow(tb_x1, e_oy - 95, tb_x2, e_oy - 95, color=FIELD, sw=1.5))
    frags.append(text((tb_x1 + tb_x2) / 2, e_oy - 105, "τ_b = 2π/ω_b", size=10, bold=True, color=FIELD))
    
    t_sat, _, _ = textbox(e_ox + 170, e_oy - 65, "Плато E_∞ (df/dv -> 0)\nзагасання припиняється!", size=10, pad=4, fill="#fdebd0", stroke=POS)
    frags.append(t_sat)
    
    t_bot, _, _ = textbox(w / 2, 340, "При τb < τL захоплені частинки сплющують плато у f(v), вимикаючи загасання Ландау.", size=11, pad=5, fill=FILL, stroke=LINE)
    frags.append(t_bot)
    
    return render(os.path.join(IMG_DIR, "fig2-dispersion-damping.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_fig1()
    gen_fig2()
    gen_fig3()
    gen_fig4()
    print("Усі 4 фігури для теми landau-damping успішно згенеровано!")
