# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Щуп осцилографа» (scope-probe).

Фігури:
  1) passive-probe-schematic.svg       — схема пасивного компенсованого щупа 10X (дільник, кабель із втратами, вхід осцилографа);
  2) probe-compensation-waveforms.svg  — калібрування компенсації на меандрі 1 кГц (недокомпенсація, оптимум, перекомпенсація);
  3) ground-lead-inductance-ringing.svg — LC-дзвін через індуктивність земляного крокодила проти пружинного заземлення;
  4) probe-input-impedance-vs-freq.svg — спад вхідного імпедансу |Z_in| від частоти для щупів 1X, 10X та активного FET;
  5) ground-clip-short-circuit.svg     — загроза КЗ через захисне заземлення (PE) осцилографа при вимірюванні в мережевих/силових колах.

Запуск: python figs.py
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD    = "#caa24a"
GREEN_F = "#eef6ef"
BLUE_F  = "#e9eefb"
GOLD_F  = "#fff6e0"
RED_F   = "#fdecea"


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw, d))


# ── 1. Схема пасивного щупа 10X ─────────────────────────────────────────────
def fig_schematic():
    W, H = 980, 440
    f = [
        text(W / 2, 28, "Схемотехніка пасивного щупа 10X: подільник і вхідний тракт", size=16, bold=True),
        text(W / 2, 48, "поділ напруги 10:1 задається парою паралельних RC-ланок: у вістрі щупа та на вході приладу", size=11, color=MUTED, italic=True)
    ]

    # Секції (блоки тла)
    f.append(fitbox(20, 70, 260, 310, "", fill=GOLD_F, stroke=GOLD, sw=1.5, rx=8))
    f.append(text(150, 92, "Вістря щупа (Probe Tip)", size=12, bold=True, color=GOLD))

    f.append(fitbox(300, 70, 270, 310, "", fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(435, 92, "Коаксіальний кабель (~1.2 м)", size=12, bold=True, color=INK))

    f.append(fitbox(590, 70, 370, 310, "", fill=BLUE_F, stroke=NEG, sw=1.5, rx=8))
    f.append(text(775, 92, "Компенсаційна коробка BNC + Вхід осцилографа", size=12, bold=True, color=NEG))

    # Вістря: верхня гілка R1 (9 МОм) і C1 (підстроювальний)
    # Вхідна клема (Vin)
    f.append(circle(45, 200, 4, fill=POS, stroke=POS))
    f.append(text(45, 185, "V_in", size=11, bold=True, color=POS))
    f.append(line(45, 200, 90, 200, color=INK, sw=2))

    # Розгалуження на R1 і C1
    f.append(line(90, 150, 90, 250, color=INK, sw=2))
    f.append(line(90, 150, 115, 150, color=INK, sw=2))
    f.append(line(90, 250, 115, 250, color=INK, sw=2))

    # Резистор R1
    f.append(rect(115, 138, 60, 24, fill=BG, stroke=INK, sw=1.8, rx=2))
    f.append(text(145, 154, "9 МОм", size=11, bold=True))
    f.append(text(145, 130, "R₁", size=11, color=MUTED))

    # Конденсатор C_comp (підстроювальний)
    f.append(line(115, 250, 138, 250, color=INK, sw=2))
    f.append(line(138, 238, 138, 262, color=INK, sw=2.5))
    f.append(line(146, 238, 146, 262, color=INK, sw=2.5))
    f.append(line(146, 250, 175, 250, color=INK, sw=2))
    # Стрілка підстроювання (триммер)
    f.append(arrow(130, 268, 158, 232, color=GOLD, sw=1.5))
    f.append(text(145, 284, "C_комп (10–15 пФ)", size=10, bold=True, color=GOLD))
    f.append(text(145, 230, "C₁", size=11, color=MUTED))

    # Зведення гілок
    f.append(line(175, 150, 200, 150, color=INK, sw=2))
    f.append(line(175, 250, 200, 250, color=INK, sw=2))
    f.append(line(200, 150, 200, 250, color=INK, sw=2))
    f.append(line(200, 200, 320, 200, color=INK, sw=2))

    # Кабель: модель з розподіленим опором (lossy cable) і ємністю
    f.append(rect(320, 188, 70, 24, fill=BG, stroke=INK, sw=1.8, rx=2))
    f.append(text(355, 204, "R_кабель", size=10, bold=True))
    f.append(text(355, 180, "200 Ом (ніхром)", size=9, color=MUTED))

    f.append(line(390, 200, 470, 200, color=INK, sw=2))
    f.append(circle(470, 200, 3, fill=INK, stroke=INK))

    # Ємність кабелю C_cable на землю
    f.append(line(470, 200, 470, 260, color=INK, sw=2))
    f.append(line(458, 260, 482, 260, color=INK, sw=2.5))
    f.append(line(458, 268, 482, 268, color=INK, sw=2.5))
    f.append(line(470, 268, 470, 330, color=INK, sw=2))
    f.append(text(515, 266, "C_кабель ≈ 80–100 пФ", size=10, color=MUTED, anchor="start"))

    f.append(line(470, 200, 620, 200, color=INK, sw=2))

    # Вхід осцилографа: R_in (1 МОм) || C_in (15 пФ)
    f.append(circle(620, 200, 3, fill=INK, stroke=INK))
    f.append(line(620, 200, 650, 200, color=INK, sw=2))

    # Розгалуження входу приладу
    f.append(line(650, 150, 650, 250, color=INK, sw=2))
    f.append(line(650, 150, 680, 150, color=INK, sw=2))
    f.append(line(650, 250, 680, 250, color=INK, sw=2))

    # Резистор R_scope
    f.append(rect(680, 138, 60, 24, fill=BG, stroke=INK, sw=1.8, rx=2))
    f.append(text(710, 154, "1 МОм", size=11, bold=True))
    f.append(text(710, 130, "R₂ (вхід)", size=11, color=MUTED))

    # Конденсатор C_scope
    f.append(line(680, 250, 703, 250, color=INK, sw=2))
    f.append(line(703, 238, 703, 262, color=INK, sw=2.5))
    f.append(line(711, 238, 711, 262, color=INK, sw=2.5))
    f.append(line(711, 250, 740, 250, color=INK, sw=2))
    f.append(text(710, 280, "C_вх ≈ 15 пФ", size=10, color=MUTED))
    f.append(text(710, 230, "C₂", size=11, color=MUTED))

    # Зведення входу осцилографа
    f.append(line(740, 150, 770, 150, color=INK, sw=2))
    f.append(line(740, 250, 770, 250, color=INK, sw=2))
    f.append(line(770, 150, 770, 250, color=INK, sw=2))
    f.append(line(770, 200, 840, 200, color=INK, sw=2))

    # Вихід на АЦП осцилографа
    f.append(rect(840, 175, 100, 50, fill=GREEN_F, stroke=FIELD, sw=1.8, rx=4))
    f.append(text(890, 196, "Підсилювач", size=11, bold=True, color=FIELD))
    f.append(text(890, 212, "+ АЦП (V_out)", size=10, color=FIELD))

    # Загальна шина Землі
    f.append(line(45, 330, 930, 330, color=LINE, sw=2))
    f.append(line(45, 200, 45, 280, color=LINE, sw=1.5, dash="4 3"))
    f.append(circle(45, 330, 4, fill=LINE, stroke=LINE))
    f.append(text(45, 352, "GND схеми", size=10, color=MUTED))

    # Земляний крокодил
    f.append(fitbox(80, 342, 160, 32, "Паразитна L_g (100–150 нГн)", size=10, bold=True, fill=RED_F, stroke=POS, sw=1.2))

    # Позначення заземлення BNC
    f.append(line(770, 250, 770, 330, color=LINE, sw=2))
    f.append(circle(770, 330, 3, fill=LINE, stroke=LINE))
    f.append(text(770, 355, "Земля BNC приладу", size=10, color=MUTED))

    # Пояснення умови компенсації внизу
    f.append(text(W / 2, 410, "Умова ідеальної компенсації: R₁ · C₁ = R₂ · C₂ (де C₂ = C_кабель + C_вх ≈ 100 + 15 = 115 пФ, C₁ ≈ 12 пФ)", size=12, bold=True, color=INK))

    return render(os.path.join(IMG, "passive-probe-schematic.svg"), W, H, *f)


# ── 2. Калібрування компенсації щупа ─────────────────────────────────────────
def fig_compensation():
    W, H = 980, 360
    f = [
        text(W / 2, 28, "Калібрування компенсації щупа на тестовому меандрі 1 кГц", size=16, bold=True),
        text(W / 2, 48, "форма прямокутного імпульсу CAL викриває дисбаланс низькочастотного та високочастотного поділу", size=11, color=MUTED, italic=True)
    ]

    panel_w = 280
    panel_h = 220
    py = 75

    panels = [
        (40,  "1. Недокомпенсація", "C_комп замала (C₁ < C₂/9)", "Завалений передній фронт,\nповільне експоненційне наростання", RED_F, POS),
        (350, "2. Ідеальна компенсація", "C_комп налаштовано (R₁C₁ = R₂C₂)", "Гострий перепад, плоска вершина,\nоднаковий поділ на всіх частотах", GREEN_F, FIELD),
        (660, "3. Перекомпенсація", "C_комп завелика (C₁ > C₂/9)", "Гострий викид (overshoot),\nпотім експоненційний спад до полички", GOLD_F, GOLD),
    ]

    for px, title, sub, desc, fill, stroke in panels:
        # Рамка екрана
        f.append(rect(px, py, panel_w, panel_h, fill=BG, stroke=LINE, sw=1.5, rx=6))
        # Заголовок панелі
        f.append(text(px + panel_w / 2, py + 22, title, size=13, bold=True, color=stroke))
        f.append(text(px + panel_w / 2, py + 38, sub, size=10, color=MUTED, italic=True))

        # Сітка осцилографа всередині панелі
        gx0, gy0, gw, gh = px + 20, py + 48, panel_w - 40, 110
        f.append(rect(gx0, gy0, gw, gh, fill="#fafafa", stroke="#e0e0e0", sw=1))
        # Горизонтальні лінії сітки
        for i in range(1, 4):
            f.append(line(gx0, gy0 + gh * i / 4, gx0 + gw, gy0 + gh * i / 4, color="#ebebeb", sw=1, dash="3 3"))
        # Вертикальні лінії сітки
        for i in range(1, 5):
            f.append(line(gx0 + gw * i / 5, gy0, gx0 + gw * i / 5, gy0 + gh, color="#ebebeb", sw=1, dash="3 3"))

        # Опис унизу панелі
        lines = desc.split("\n")
        f.append(mtext(px + panel_w / 2, py + 175, lines, size=10, color=INK, bold=False))

    # Осцилограма 1: Недокомпенсація (завалений фронт)
    pts1 = []
    x0, y_low, y_high = 40 + 20 + 10, py + 48 + 85, py + 48 + 25
    # Початок низу
    pts1.append((x0, y_low))
    pts1.append((x0 + 30, y_low))
    # Фронт з експоненційним завалом
    for t in range(50):
        frac = t / 50.0
        v = 1.0 - math.exp(-frac * 3.5)
        pts1.append((x0 + 30 + t, y_low - v * (y_low - y_high)))
    pts1.append((x0 + 120, y_high))
    # Спад з експоненційним завалом
    for t in range(50):
        frac = t / 50.0
        v = math.exp(-frac * 3.5)
        pts1.append((x0 + 120 + t, y_high + (1.0 - v) * (y_low - y_high)))
    pts1.append((x0 + 210, y_low))
    f.append(polyline(pts1, color=POS, sw=2.5))

    # Осцилограма 2: Ідеальна компенсація (прямокутник)
    pts2 = [
        (350 + 30, y_low),
        (350 + 60, y_low),
        (350 + 60, y_high),
        (350 + 150, y_high),
        (350 + 150, y_low),
        (350 + 240, y_low)
    ]
    f.append(polyline(pts2, color=FIELD, sw=2.5))

    # Осцилограма 3: Перекомпенсація (викид + спад)
    pts3 = []
    x3 = 660 + 30
    pts3.append((x3, y_low))
    pts3.append((x3 + 30, y_low))
    # Викид понад y_high
    y_spike = y_high - 22
    pts3.append((x3 + 30, y_spike))
    # Експоненційне повернення до y_high
    for t in range(1, 50):
        frac = t / 50.0
        decay = math.exp(-frac * 4.0)
        curr_y = y_high - (y_high - y_spike) * decay
        pts3.append((x3 + 30 + t, curr_y))
    pts3.append((x3 + 120, y_high))
    # Негативний викид унизу
    y_spike_down = y_low + 22
    pts3.append((x3 + 120, y_spike_down))
    for t in range(1, 50):
        frac = t / 50.0
        decay = math.exp(-frac * 4.0)
        curr_y = y_low + (y_spike_down - y_low) * decay
        pts3.append((x3 + 120 + t, curr_y))
    pts3.append((x3 + 210, y_low))
    f.append(polyline(pts3, color=GOLD, sw=2.5))

    # Підсумок внизу
    f.append(text(W / 2, 330, "Помилка компенсації створює хибні висновки: занижує виміряну амплітуду ВЧ або показує неіснуючий викид", size=11, color=MUTED, italic=True))

    return render(os.path.join(IMG, "probe-compensation-waveforms.svg"), W, H, *f)


# ── 3. Індуктивність земляного крокодила та LC-дзвін ────────────────────────
def fig_ground_ringing():
    W, H = 980, 420
    f = [
        text(W / 2, 28, "Індуктивність заземлення щупа: походження фальшивого LC-дзвону", size=16, bold=True),
        text(W / 2, 48, "довгий земляний провід (15 см ≈ 150 нГн) утворює коливальний RLC-контур із ємністю щупа (C_in ≈ 12 пФ)", size=11, color=MUTED, italic=True)
    ]

    # Ліва половина: Довгий крокодил (помилка)
    f.append(rect(30, 75, 445, 315, fill=BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(252, 100, "Довгий дріт заземлення (12–15 см)", size=13, bold=True, color=POS))
    f.append(text(252, 118, "L_g ≈ 150 нГн  →  f_res ≈ 118 МГц (добротність Q > 3)", size=10, color=MUTED))

    # Осцилограма з важким дзвоном
    gx1, gy1, gw1, gh1 = 50, 130, 405, 160
    f.append(rect(gx1, gy1, gw1, gh1, fill="#fafafa", stroke="#e0e0e0", sw=1))
    for i in range(1, 4):
        f.append(line(gx1, gy1 + gh1 * i / 4, gx1 + gw1, gy1 + gh1 * i / 4, color="#ebebeb", sw=1, dash="3 3"))

    # Справжній сигнал (пунктир) проти виміряного (суцільний червоний з дзвоном)
    y_base, y_top = gy1 + 130, gy1 + 45
    f.append(polyline([(gx1 + 20, y_base), (gx1 + 60, y_base), (gx1 + 70, y_top), (gx1 + 380, y_top)], color=MUTED, sw=1.5, dash="4 3"))
    f.append(text(gx1 + 120, y_top - 12, "Справжній чистий фронт 3.3 В (t_r = 1.5 нс)", size=9, color=MUTED, anchor="start"))

    ring_pts = [(gx1 + 20, y_base), (gx1 + 60, y_base)]
    # Крутий перепад з затухаючим синусоїдальним дзвоном
    for step in range(250):
        t = step / 250.0 * 25.0 # наносекунди умовно
        x = gx1 + 60 + step * 1.2
        if x > gx1 + gw1 - 15:
            break
        # Затухаючі коливання
        decay = math.exp(-0.22 * t)
        sine = math.sin(2.0 * math.pi * 0.45 * t)
        v = 1.0 - decay * math.cos(2.0 * math.pi * 0.45 * t) + 0.6 * decay * sine
        curr_y = y_base - v * (y_base - y_top)
        ring_pts.append((x, curr_y))
    f.append(polyline(ring_pts, color=POS, sw=2.2))

    f.append(text(252, 315, "Фальшивий викид до 5.1 В (+55%) та затухаючий дзвін 120 МГц!", size=10, bold=True, color=POS))
    f.append(text(252, 335, "Інженер витрачає тижні на пошук «шуму живлення», якого в схемі нема", size=9, color=MUTED, italic=True))
    f.append(text(252, 370, "❌ Велика індуктивна петля антени ловить наведення dI/dt", size=10, color=POS, bold=True))

    # Права половина: Коротке пружинне заземлення (Ground Spring)
    f.append(rect(505, 75, 445, 315, fill=BG, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(727, 100, "Пружинне заземлення (Ground Spring, 3–5 мм)", size=13, bold=True, color=FIELD))
    f.append(text(727, 118, "L_g < 3–5 нГн  →  f_res > 1.2 ГГц (поза смугою щупа)", size=10, color=MUTED))

    gx2, gy2, gw2, gh2 = 525, 130, 405, 160
    f.append(rect(gx2, gy2, gw2, gh2, fill="#fafafa", stroke="#e0e0e0", sw=1))
    for i in range(1, 4):
        f.append(line(gx2, gy2 + gh2 * i / 4, gx2 + gw2, gy2 + gh2 * i / 4, color="#ebebeb", sw=1, dash="3 3"))

    clean_pts = [(gx2 + 20, y_base), (gx2 + 60, y_base)]
    for step in range(250):
        t = step / 250.0 * 25.0
        x = gx2 + 60 + step * 1.2
        if x > gx2 + gw2 - 15:
            break
        # Ледь помітне демпфоване коливання
        decay = math.exp(-0.9 * t)
        v = 1.0 - decay * (1.0 + 0.05 * math.sin(4.0 * t))
        curr_y = y_base - v * (y_base - y_top)
        clean_pts.append((x, curr_y))
    f.append(polyline(clean_pts, color=FIELD, sw=2.2))

    f.append(text(727, 315, "Достовірне відображення: ідеальний фронт без перерегулювання", size=10, bold=True, color=FIELD))
    f.append(text(727, 335, "Резонанс витіснений далеко за межі смуги пропускання щупа", size=9, color=MUTED, italic=True))
    f.append(text(727, 370, "✓ Мінімальна площа петлі виключає магнітну заваду", size=10, color=FIELD, bold=True))

    return render(os.path.join(IMG, "ground-lead-inductance-ringing.svg"), W, H, *f)


# ── 4. Спад вхідного імпедансу від частоти ──────────────────────────────────
def fig_impedance():
    W, H = 980, 420
    f = [
        text(W / 2, 28, "Вхідний імпеданс щупа |Z_in| від частоти: динамічне навантаження схеми", size=16, bold=True),
        text(W / 2, 48, "на високих частотах ємність перемагає опір: пасивний щуп перетворюється на важке навантаження в сотні Ом", size=11, color=MUTED, italic=True)
    ]

    gx, gy, gw, gh = 100, 80, 810, 270
    f.append(rect(gx, gy, gw, gh, fill=BG, stroke=LINE, sw=1.5, rx=6))

    # Логарифмічна сітка: Частота від 10 Гц (10^1) до 1 ГГц (10^9) — 8 декад
    decades_f = [
        ("10 Гц", 0), ("100 Гц", 1), ("1 кГц", 2), ("10 кГц", 3),
        ("100 кГц", 4), ("1 МГц", 5), ("10 МГц", 6), ("100 МГц", 7), ("1 ГГц", 8)
    ]
    for label, d in decades_f:
        x = gx + gw * d / 8.0
        f.append(line(x, gy, x, gy + gh, color="#f0f0f0", sw=1))
        f.append(text(x, gy + gh + 18, label, size=10, color=MUTED))

    # Логарифмічна вісь Z: від 10 Ом (10^1) до 10 МОм (10^7) — 6 декад
    decades_z = [
        ("10 МОм", 6), ("1 МОм", 5), ("100 кОм", 4), ("10 кОм", 3),
        ("1 кОм", 2), ("100 Ом", 1), ("10 Ом", 0)
    ]
    for label, d in decades_z:
        y = gy + gh * (6 - d) / 6.0
        f.append(line(gx, y, gx + gw, y, color="#f0f0f0", sw=1))
        f.append(text(gx - 10, y + 4, label, size=10, color=MUTED, anchor="end"))

    def z_to_y(z_val):
        log_z = math.log10(max(10.0, z_val))
        return gy + gh * (7.0 - log_z) / 6.0

    def f_to_x(f_val):
        log_f = math.log10(max(10.0, f_val))
        return gx + gw * (log_f - 1.0) / 8.0

    # Будуємо криві
    pts_1x, pts_10x, pts_fet = [], [], []
    for step in range(300):
        log_f = 1.0 + step / 300.0 * 8.0
        freq = 10.0 ** log_f
        x = f_to_x(freq)

        # 1X
        xc_1x = 1.0 / (2.0 * math.pi * freq * 100e-12)
        z_1x = 1.0 / math.sqrt((1.0 / 1e6)**2 + (1.0 / xc_1x)**2)
        pts_1x.append((x, z_to_y(z_1x)))

        # 10X
        xc_10x = 1.0 / (2.0 * math.pi * freq * 12e-12)
        z_10x = 1.0 / math.sqrt((1.0 / 10e6)**2 + (1.0 / xc_10x)**2)
        pts_10x.append((x, z_to_y(z_10x)))

        # FET
        xc_fet = 1.0 / (2.0 * math.pi * freq * 0.8e-12)
        z_fet = 1.0 / math.sqrt((1.0 / 1e6)**2 + (1.0 / xc_fet)**2)
        pts_fet.append((x, z_to_y(z_fet)))

    f.append(polyline(pts_1x, color=POS, sw=2.5))
    f.append(polyline(pts_10x, color=GOLD, sw=2.5))
    f.append(polyline(pts_fet, color=FIELD, sw=2.5))

    # Підписи до кривих
    f.append(text(gx + 320, z_to_y(15000) + 24, "Щуп 1X (1 МОм || 100 пФ)", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(gx + 470, z_to_y(4000) - 10, "Щуп 10X (10 МОм || 12 пФ)", size=11, bold=True, color=GOLD, anchor="start"))
    f.append(text(gx + 560, z_to_y(25000) - 14, "Активний FET (1 МОм || 0.8 пФ)", size=11, bold=True, color=FIELD, anchor="start"))

    # Конкретні точки
    x_100m = f_to_x(100e6)
    y_100m = z_to_y(132.0)
    f.append(circle(x_100m, y_100m, 4, fill=GOLD, stroke=LINE))
    f.append(text(x_100m + 8, y_100m + 4, "130 Ом @ 100 МГц!", size=10, bold=True, color=GOLD, anchor="start"))

    x_10m = f_to_x(10e6)
    y_10m = z_to_y(160.0)
    f.append(circle(x_10m, y_10m, 4, fill=POS, stroke=LINE))
    f.append(text(x_10m - 8, y_10m + 16, "160 Ом @ 10 МГц", size=10, bold=True, color=POS, anchor="end"))

    f.append(text(W / 2, 395, "Висновок: пасивний щуп 10X на 100 МГц навантажує схему опором усього 130 Ом замість очікуваних 10 МОм", size=11, color=MUTED, italic=True))

    return render(os.path.join(IMG, "probe-input-impedance-vs-freq.svg"), W, H, *f)


# ── 5. Небезпека земляного крокодила в мережевих колах ───────────────────────
def fig_ground_short():
    W, H = 980, 420
    f = [
        text(W / 2, 28, "Небезпека вимірювань: коротке замикання через захисне заземлення (PE)", size=16, bold=True),
        text(W / 2, 48, "корпус BNC осцилографа жорстко з'єднаний із землею розетки; підключення крокодила до фази чи плаваючого ключа викличе вибух", size=11, color=MUTED, italic=True)
    ]

    # Лівий блок: Схема під напругою (Мережевий випрямляч / Інвертор)
    f.append(rect(40, 80, 320, 290, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(200, 105, "Досліджуваний пристрій (DUT)", size=13, bold=True))
    f.append(text(200, 125, "Імпульсний перетворювач 230 В / 400 В", size=10, color=MUTED))

    # Фаза і нуль
    f.append(line(70, 160, 140, 160, color=POS, sw=2))
    f.append(text(60, 164, "L (230 В)", size=10, bold=True, color=POS, anchor="end"))
    f.append(line(70, 240, 140, 240, color=NEG, sw=2))
    f.append(text(60, 244, "N (0 В)", size=10, bold=True, color=NEG, anchor="end"))

    # Випрямний міст / Плаваючий ключ
    f.append(rect(140, 140, 90, 120, fill=BG, stroke=LINE, sw=1.5, rx=4))
    f.append(mtext(185, 195, "Силовий\nміст / GaN", size=11, bold=True))

    # Плаваюча точка (Switching node)
    f.append(circle(270, 180, 4, fill=POS, stroke=POS))
    f.append(text(270, 165, "Плаваюча точка (+350 В)", size=10, bold=True, color=POS))
    f.append(line(230, 180, 270, 180, color=POS, sw=2))

    # Правий блок: Осцилограф
    f.append(rect(600, 80, 340, 290, fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    f.append(text(770, 105, "Осцилограф (Живлення від 230 В)", size=13, bold=True, color=NEG))
    f.append(text(770, 125, "Металевий корпус з'єднаний з PE", size=10, color=MUTED))

    # Гніздо BNC
    f.append(rect(630, 170, 50, 40, fill=BG, stroke=INK, sw=1.8, rx=2))
    f.append(text(655, 194, "BNC", size=11, bold=True))

    # Захисне заземлення осцилографа PE
    f.append(line(770, 210, 770, 310, color=FIELD, sw=3))
    f.append(line(680, 190, 770, 190, color=FIELD, sw=2))
    f.append(line(770, 310, 910, 310, color=FIELD, sw=3))
    f.append(text(840, 330, "Захисне заземлення PE (0 В)", size=11, bold=True, color=FIELD))

    # Щуп між пристроєм і осцилографом
    # Вістря підключено до сигналу
    f.append(line(270, 180, 450, 180, color=POS, sw=2))
    f.append(text(360, 170, "Вістря щупа", size=10, color=MUTED))

    # ЗЕМЛЯНИЙ КРОКОДИЛ помилково причеплено до плаваючої точки 350 В!
    f.append(line(270, 230, 450, 230, color=POS, sw=3, dash="6 3"))
    f.append(text(360, 250, "Земляний крокодил!", size=11, bold=True, color=POS))
    f.append(line(450, 230, 630, 190, color=POS, sw=3))

    # Контур катастрофічного струму КЗ
    f.append(fitbox(340, 270, 260, 80, "СТРУМ КЗ > 500 А!\nФаза 350 В → Крокодил →\nЕкран кабелю → Корпус BNC → PE\n(Вибух щупа, вибиті автомати)", size=11, bold=True, fill=RED_F, stroke=POS, sw=2))

    # Правильне рішення
    f.append(text(W / 2, 395, "Розв'язок: для плаваючих і силових вимірювань використовують лише ВИСОКОВОЛЬТНИЙ ДИФЕРЕНЦІАЛЬНИЙ ЩУП", size=11, bold=True, color=FIELD))

    return render(os.path.join(IMG, "ground-clip-short-circuit.svg"), W, H, *f)


def main():
    fig_schematic()
    fig_compensation()
    fig_ground_ringing()
    fig_impedance()
    fig_ground_short()
    print("Всі 5 фігур успішно згенеровано.")


if __name__ == "__main__":
    main()
