# -*- coding: utf-8 -*-
"""Фігури до теми «Потужність у трифазній мережі».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_A = "#c0392b"  # Фаза A (червоний)
COLOR_B = "#27ae60"  # Фаза B (зелений)
COLOR_C = "#2457d6"  # Фаза C (синій)
COLOR_N = "#7f8c8d"  # Нейтраль (сірий)
COLOR_SUM = "#8e44ad" # Сумарна потужність (пурпуровий)
COLOR_ORANGE = "#d35400"

def path_element(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    st = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{st}/>'

# ── Фігура 1: Трифазні синусоїдні напруги ─────────────────────────────────────
def fig_three_phase_waveforms():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Трифазна система напруг зі зсувом фаз 120° (2π/3)", size=16, bold=True))

    x0, y0 = 70, 190
    x_max = 680
    w_px = x_max - x0
    amp = 110

    # Осі
    f.append(line(x0 - 20, y0, x_max + 20, y0, color=LINE, sw=1.5))
    f.append(text(x_max + 30, y0 + 4, "ωt", size=13, bold=True, color=INK))

    f.append(line(x0, 45, x0, 330, color=LINE, sw=1.5))
    f.append(text(x0, 36, "v(t)", size=13, bold=True, color=INK))

    # Лінії піків
    f.append(line(x0, y0 - amp, x_max, y0 - amp, color=MUTED, sw=1, dash="3,3"))
    f.append(text(x0 - 32, y0 - amp + 4, "+Vm", size=11, color=MUTED))

    f.append(line(x0, y0 + amp, x_max, y0 + amp, color=MUTED, sw=1, dash="3,3"))
    f.append(text(x0 - 32, y0 + amp + 4, "−Vm", size=11, color=MUTED))

    # Вертикальні позначки фаз (0, 120°, 240°, 360°)
    angles = [(0, "0"), (math.pi*2/3, "120°"), (math.pi*4/3, "240°"), (math.pi*2, "360°")]
    for rad, label in angles:
        px = x0 + (rad / (2 * math.pi)) * (w_px * 0.75)
        f.append(line(px, y0 - 6, px, y0 + 6, color=LINE, sw=1.2))
        f.append(text(px, y0 + 22, label, size=11, color=MUTED))
        f.append(line(px, y0 - amp, px, y0 + amp, color="#e5e7eb", sw=1, dash="2,2"))

    # Побудова трьох синусоїд
    pts_a, pts_b, pts_c = [], [], []
    steps = 150
    for i in range(steps + 1):
        t = (i / steps) * (2.4 * math.pi)
        px = x0 + (t / (2 * math.pi)) * (w_px * 0.75)
        
        va = y0 - amp * math.sin(t)
        vb = y0 - amp * math.sin(t - 2 * math.pi / 3)
        vc = y0 - amp * math.sin(t - 4 * math.pi / 3)
        
        pts_a.append(f"{px:.1f},{va:.1f}")
        pts_b.append(f"{px:.1f},{vb:.1f}")
        pts_c.append(f"{px:.1f},{vc:.1f}")

    f.append(path_element("M " + " L ".join(pts_a), stroke=COLOR_A, sw=2.5))
    f.append(path_element("M " + " L ".join(pts_b), stroke=COLOR_B, sw=2.5))
    f.append(path_element("M " + " L ".join(pts_c), stroke=COLOR_C, sw=2.5))

    # Легенда
    f.append(rect(550, 48, 180, 85, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(line(560, 64, 585, 64, color=COLOR_A, sw=2.5))
    f.append(text(595, 68, "vA(t) = Vm·sin(ωt)", size=11, color=COLOR_A, anchor="start", bold=True))

    f.append(line(560, 88, 585, 88, color=COLOR_B, sw=2.5))
    f.append(text(595, 92, "vB(t) = Vm·sin(ωt−120°)", size=11, color=COLOR_B, anchor="start", bold=True))

    f.append(line(560, 112, 585, 112, color=COLOR_C, sw=2.5))
    f.append(text(595, 116, "vC(t) = Vm·sin(ωt−240°)", size=11, color=COLOR_C, anchor="start", bold=True))

    # Пояснювальний бокс під графіком
    b, w, h = textbox(W / 2, 345, "Сума миттєвих напруг симетричної трифазної системи завжди дорівнює нулю: vA(t) + vB(t) + vC(t) = 0",
                      size=12, pad=7, fill="#eef6ff", stroke="#99ccff", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "three-phase-waveforms.svg"), W, H, *f)


# ── Фігура 2: Схеми підключення «Зірка» та «Трикутник» ────────────────────────
def fig_star_delta_connections():
    W, H = 760, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Схеми з'єднання трифазного навантаження: «Зірка» (Y) та «Трикутник» (Δ)", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 48, midx, H - 15, color="#d6dde6", sw=1.4, dash="5,5"))

    # --- ЛІВА ЧАСТИНА: Зірка (Y) ---
    f.append(text(midx / 2, 52, "З'єднання «Зірка» (Y)", size=14, bold=True, color=COLOR_A))

    # Нейтральна точка N у центрі
    nx, ny = 190, 190
    f.append(circle(nx, ny, 5, fill=COLOR_N, stroke=LINE, sw=1.2))
    f.append(text(nx - 14, ny + 4, "N", size=12, bold=True, color=COLOR_N))

    # Три фазні опори Z_A, Z_B, Z_C під кутами 120°
    # Фаза A (вгору)
    f.append(line(nx, ny, nx, ny - 30, color=LINE, sw=1.8))
    f.append(rect(nx - 12, ny - 70, 24, 40, fill='#fee2e2', stroke=COLOR_A, sw=1.8, rx=3))
    f.append(text(nx, ny - 50, "ZA", size=11, bold=True, color=COLOR_A))
    f.append(line(nx, ny - 70, nx, ny - 100, color=COLOR_A, sw=2))
    f.append(line(nx, ny - 100, nx - 120, ny - 100, color=COLOR_A, sw=2))
    f.append(text(nx - 130, ny - 100 + 4, "A", size=13, bold=True, color=COLOR_A))

    # Фаза B (ліво-вниз 120°)
    bx, by = nx - 50, ny + 30
    f.append(line(nx, ny, bx, by, color=LINE, sw=1.8))
    f.append(rect(bx - 20, by + 5, 40, 24, fill='#dcfce7', stroke=COLOR_B, sw=1.8, rx=3))
    f.append(text(bx, by + 17, "ZB", size=11, bold=True, color=COLOR_B))
    f.append(line(bx - 20, by + 17, nx - 120, ny + 60, color=COLOR_B, sw=2))
    f.append(text(nx - 130, ny + 60 + 4, "B", size=13, bold=True, color=COLOR_B))

    # Фаза C (право-вниз 120°)
    cx, cy = nx + 50, ny + 30
    f.append(line(nx, ny, cx, cy, color=LINE, sw=1.8))
    f.append(rect(cx - 20, cy + 5, 40, 24, fill='#dbeafe', stroke=COLOR_C, sw=1.8, rx=3))
    f.append(text(cx, cy + 17, "ZC", size=11, bold=True, color=COLOR_C))
    f.append(line(cx + 20, cy + 17, nx - 120, ny + 110, color=COLOR_C, sw=2))
    f.append(text(nx - 130, ny + 110 + 4, "C", size=13, bold=True, color=COLOR_C))

    # Провідник нейтралі N
    f.append(line(nx, ny, nx - 120, ny + 10, color=COLOR_N, sw=1.8, dash="4,4"))
    f.append(text(nx - 130, ny + 10 + 4, "N", size=12, bold=True, color=COLOR_N))

    # Формули для Зірки
    b1, w1, h1 = textbox(midx / 2, 335, "Vлінійне = √3 · Vфазне (400 В vs 230 В)\nІлінійне = Іфазне  |  P = √3 · Vл · Iл · cosφ",
                         size=11, pad=8, fill="#f8fafc", stroke="#cbd5e1", sw=1.2)
    f.append(b1)


    # --- ПРАВА ЧАСТИНА: Трикутник (Δ) ---
    f.append(text(midx + midx / 2, 52, "З'єднання «Трикутник» (Δ)", size=14, bold=True, color=COLOR_C))

    # Три вершини трикутника
    p_a = (midx + 190, 100)
    p_b = (midx + 100, 240)
    p_c = (midx + 280, 240)

    # Опір Z_AB (між A і B)
    f.append(line(p_a[0], p_a[1], p_a[0] - 25, p_a[1] + 40, color=LINE, sw=1.8))
    f.append(rect(p_a[0] - 45, p_a[1] + 40, 40, 24, fill='#fee2e2', stroke=COLOR_A, sw=1.8, rx=3))
    f.append(text(p_a[0] - 25, p_a[1] + 52, "ZAB", size=10, bold=True, color=COLOR_A))
    f.append(line(p_a[0] - 45, p_a[1] + 64, p_b[0], p_b[1], color=LINE, sw=1.8))

    # Опір Z_BC (між B і C)
    f.append(line(p_b[0], p_b[1], p_b[0] + 40, p_b[1], color=LINE, sw=1.8))
    f.append(rect(p_b[0] + 40, p_b[1] - 12, 40, 24, fill='#dcfce7', stroke=COLOR_B, sw=1.8, rx=3))
    f.append(text(p_b[0] + 60, p_b[1], "ZBC", size=10, bold=True, color=COLOR_B))
    f.append(line(p_b[0] + 80, p_b[1], p_c[0], p_c[1], color=LINE, sw=1.8))

    # Опір Z_CA (між C і A)
    f.append(line(p_c[0], p_c[1], p_c[0] - 25, p_c[1] - 40, color=LINE, sw=1.8))
    f.append(rect(p_c[0] - 15, p_c[1] - 64, 40, 24, fill='#dbeafe', stroke=COLOR_C, sw=1.8, rx=3))
    f.append(text(p_c[0] + 5, p_c[1] - 52, "ZCA", size=10, bold=True, color=COLOR_C))
    f.append(line(p_c[0] - 15, p_c[1] - 64, p_a[0], p_a[1], color=LINE, sw=1.8))

    # Підведення ліній A, B, C
    f.append(line(p_a[0], p_a[1], p_a[0] + 50, p_a[1], color=COLOR_A, sw=2))
    f.append(text(p_a[0] + 62, p_a[1] + 4, "A", size=13, bold=True, color=COLOR_A))

    f.append(line(p_b[0], p_b[1], p_b[0] - 50, p_b[1], color=COLOR_B, sw=2))
    f.append(text(p_b[0] - 62, p_b[1] + 4, "B", size=13, bold=True, color=COLOR_B))

    f.append(line(p_c[0], p_c[1], p_c[0] + 50, p_c[1], color=COLOR_C, sw=2))
    f.append(text(p_c[0] + 62, p_c[1] + 4, "C", size=13, bold=True, color=COLOR_C))

    # Формули для Трикутника
    b2, w2, h2 = textbox(midx + midx / 2, 335, "Vлінійне = Vфазне (400 В)\nІлінійне = √3 · Іфазне  |  P = √3 · Vл · Iл · cosφ",
                         size=11, pad=8, fill="#f8fafc", stroke="#cbd5e1", sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "star-delta-connections.svg"), W, H, *f)


# ── Фігура 3: Постійність миттєвої потужності ───────────────────────────────
def fig_instantaneous_power_constancy():
    W, H = 760, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Постійність сумарної миттєвої потужності p_total(t) у трифазній мережі", size=15, bold=True))

    x0, y0 = 70, 230
    x_max = 680
    w_px = x_max - x0
    amp = 70

    # Осі
    f.append(line(x0 - 15, y0, x_max + 20, y0, color=LINE, sw=1.5))
    f.append(text(x_max + 30, y0 + 4, "ωt", size=13, bold=True, color=INK))

    f.append(line(x0, 45, x0, 280, color=LINE, sw=1.5))
    f.append(text(x0, 36, "p(t)", size=13, bold=True, color=INK))

    # Рівень нульової потужності
    f.append(line(x0, y0, x_max, y0, color=MUTED, sw=1, dash="3,3"))
    f.append(text(x0 - 20, y0 + 4, "0", size=11, color=MUTED))

    # Сумарна потужність P_total = 3 * Vph * Iph * cos(φ) (стала горизонтальна лінія!)
    p_sum_y = y0 - 1.5 * amp
    f.append(line(x0, p_sum_y, x_max, p_sum_y, color=COLOR_SUM, sw=3))
    f.append(text(x_max - 140, p_sum_y - 12, "ptotal(t) = Ptotal = const!", size=13, bold=True, color=COLOR_SUM))

    # Окремі фазні потужності pA(t), pB(t), pC(t) з подвоєною частотою 2ω
    steps = 150
    pts_pa, pts_pb, pts_pc = [], [], []
    phi = math.pi / 6  # cos(phi) = cos(30 deg)
    
    for i in range(steps + 1):
        t = (i / steps) * (2 * math.pi)
        px = x0 + (t / (2 * math.pi)) * w_px
        
        # p_A(t) = Vph*Iph*cos(phi) - Vph*Iph*cos(2wt - phi)
        pa = y0 - amp * (math.cos(phi) - math.cos(2 * t - phi))
        pb = y0 - amp * (math.cos(phi) - math.cos(2 * t - 2 * math.pi / 3 - phi))
        pc = y0 - amp * (math.cos(phi) - math.cos(2 * t - 4 * math.pi / 3 - phi))
        
        pts_pa.append(f"{px:.1f},{pa:.1f}")
        pts_pb.append(f"{px:.1f},{pb:.1f}")
        pts_pc.append(f"{px:.1f},{pc:.1f}")

    f.append(path_element("M " + " L ".join(pts_pa), stroke=COLOR_A, sw=1.6, dash="4,3"))
    f.append(path_element("M " + " L ".join(pts_pb), stroke=COLOR_B, sw=1.6, dash="4,3"))
    f.append(path_element("M " + " L ".join(pts_pc), stroke=COLOR_C, sw=1.6, dash="4,3"))

    # Пояснення компенсації пульсацій
    b, w, h = textbox(W / 2, 315, "Хоча потужність кожної окремої фази пульсує з подвоєною частотою 2ω, їхня сума pA(t)+pB(t)+pC(t) є суворо постійною величиною!\nЦе забезпечує відсутність вібрацій у трифазних електродвигунах та стабільний потік енергії.",
                      size=11, pad=8, fill="#faf5ff", stroke="#e9d5ff", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "instantaneous-power-constancy.svg"), W, H, *f)


# ── Фігура 4: Метод двох ватметрів (Схема Арона) ────────────────────────────
def fig_two_wattmeter_method():
    W, H = 760, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Вимірювання трифазної потужності методом двох ватметрів (схема Арона)", size=15, bold=True))

    # Три силові лінії A, B, C
    f.append(line(50, 80, 520, 80, color=COLOR_A, sw=2))
    f.append(text(35, 84, "A", size=14, bold=True, color=COLOR_A))

    f.append(line(50, 180, 520, 180, color=COLOR_B, sw=2))
    f.append(text(35, 184, "B", size=14, bold=True, color=COLOR_B))

    f.append(line(50, 280, 520, 280, color=COLOR_C, sw=2))
    f.append(text(35, 284, "C", size=14, bold=True, color=COLOR_C))

    # Ватметр W1 на лінії A
    f.append(rect(150, 55, 60, 50, fill='#fff', stroke=COLOR_A, sw=1.8, rx=4))
    f.append(text(180, 80, "W1", size=13, bold=True, color=COLOR_A))
    # Струмова обмотка W1 (послідовно в лінію A)
    f.append(line(150, 80, 210, 80, color=COLOR_A, sw=3))
    # Напругова обмотка W1 (від лінії A до лінії C)
    f.append(line(180, 105, 180, 280, color=COLOR_A, sw=1.4, dash="3,3"))
    f.append(circle(180, 280, 3, fill=COLOR_A, stroke=LINE, sw=1))

    # Ватметр W2 на лінії B
    f.append(rect(300, 155, 60, 50, fill='#fff', stroke=COLOR_B, sw=1.8, rx=4))
    f.append(text(330, 180, "W2", size=13, bold=True, color=COLOR_B))
    # Струмова обмотка W2 (послідовно в лінію B)
    f.append(line(300, 180, 360, 180, color=COLOR_B, sw=3))
    # Напругова обмотка W2 (від лінії B до лінії C)
    f.append(line(330, 205, 330, 280, color=COLOR_B, sw=1.4, dash="3,3"))
    f.append(circle(330, 280, 3, fill=COLOR_B, stroke=LINE, sw=1))

    # Трифазне навантаження справа
    f.append(rect(520, 60, 100, 240, fill='#f1f5f9', stroke='#64748b', sw=2, rx=6))
    f.append(text(570, 180, "3-фазне\nнавантаження\n(3 провідники)", size=12, bold=True, color=INK))

    # Блок обчислень показів ватметрів
    b, w, h = textbox(W / 2, 335, "Рактивна = P1 + P2 = VAC·IA·cos(30°−φ) + VBC·IB·cos(30°+φ) = √3·Vл·Iл·cosφ\nQреактивна = √3 · (P1 − P2)  |  tanφ = √3 · (P1 − P2) / (P1 + P2)",
                      size=11, pad=8, fill="#eef6ff", stroke="#99ccff", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "two-wattmeter-method.svg"), W, H, *f)


# ── Фігура 5: Векторна діаграма напруг і струмів ─────────────────────────────
def fig_phasor_diagram_power():
    W, H = 720, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Векторна діаграма фазних і лінійних напруг та струмів", size=15, bold=True))

    cx, cy = 240, 190
    r_ph = 110

    # Нульові координатні осі
    f.append(line(cx - 150, cy, cx + 180, cy, color="#e2e8f0", sw=1.2))
    f.append(line(cx, cy - 150, cx, cy + 150, color="#e2e8f0", sw=1.2))

    # Фазні напруги VA, VB, VC (зсув 120°)
    # VA вгору (90 deg або 0 deg у стандартній геометрії, візьмемо 90 deg вверх)
    va_x, va_y = cx, cy - r_ph
    vb_x, vb_y = cx - r_ph * math.cos(math.pi / 6), cy + r_ph * math.sin(math.pi / 6)
    vc_x, vc_y = cx + r_ph * math.cos(math.pi / 6), cy + r_ph * math.sin(math.pi / 6)

    f.append(arrow(cx, cy, va_x, va_y, color=COLOR_A, sw=2.2))
    f.append(text(va_x, va_y - 12, "VA", size=13, bold=True, color=COLOR_A))

    f.append(arrow(cx, cy, vb_x, vb_y, color=COLOR_B, sw=2.2))
    f.append(text(vb_x - 16, vb_y + 12, "VB", size=13, bold=True, color=COLOR_B))

    f.append(arrow(cx, cy, vc_x, vc_y, color=COLOR_C, sw=2.2))
    f.append(text(vc_x + 16, vc_y + 12, "VC", size=13, bold=True, color=COLOR_C))

    # Лінійна напруга VAB = VA - VB
    f.append(arrow(vb_x, vb_y, va_x, va_y, color=COLOR_ORANGE, sw=2))
    f.append(text((va_x + vb_x) / 2 - 20, (va_y + vb_y) / 2 - 6, "VAB = √3·Vph", size=11, bold=True, color=COLOR_ORANGE))

    # Струми IA, IB, IC з кутом відставання φ
    phi = math.pi / 6  # 30 градусів
    r_i = 75

    ia_x = cx + r_i * math.sin(phi)
    ia_y = cy - r_i * math.cos(phi)
    f.append(arrow(cx, cy, ia_x, ia_y, color="#991b1b", sw=1.8))
    f.append(text(ia_x + 14, ia_y, "IA", size=12, bold=True, color="#991b1b"))

    # Пояснення зсуву фаз і співвідношення довжин вектора справа
    b, w, h = textbox(530, 190, "Векторні співвідношення:\n• Vлінійне = VA − VB = √3 · Vфазне · e^(j30°)\n• Струм I відстає від напруги V на кут φ\n• Потужність P = 3 · Vфаз · Іфаз · cosφ\n• Потужність P = √3 · Vлін · Ілін · cosφ",
                      size=12, pad=10, fill="#f8fafc", stroke="#cbd5e1", sw=1.2)
    f.append(b)

    return render(os.path.join(IMG, "phasor-diagram-power.svg"), W, H, *f)


if __name__ == '__main__':
    fig_three_phase_waveforms()
    fig_star_delta_connections()
    fig_instantaneous_power_constancy()
    fig_two_wattmeter_method()
    fig_phasor_diagram_power()
    print("Усі 5 фігур згенеровано успішно у ./img/")
