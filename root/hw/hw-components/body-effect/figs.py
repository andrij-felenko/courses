# -*- coding: utf-8 -*-
"""Фігури до теми «Ефект підкладки (body effect)» (book/electronics/microelectronics/body-effect).
Запуск:  python figs.py   → пише 8 SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── Локальні відтінки напівпровідника ────────────────────────────────────────
P_BODY = "#eaf0e8"   # p-підкладка
P_EDGE = "#7a8a78"
NREG   = "#cfd9ea"   # n⁺-області
OXIDE  = "#fff3b0"   # оксид SiO2 / high-k
OX_EDG = "#e0a32e"
GATE   = "#cfd6dd"   # полікремній / метал затвора
CHAN   = "#cfe0f5"   # інверсійний n-канал
DEPL   = "#f3eef6"   # збіднена область
BOX_BG = "#fffbe0"   # buried oxide (BOX)
BOX_ED = "#d4b138"


def render_svg(fname, w, h, *elems):
    """Обгортка над svgkit.render() із правильним шляхом."""
    path = os.path.join(IMG, fname)
    render(path, w, h, *elems)


def axes(ox, oy, top, right, xlabel, ylabel):
    f = [arrow(ox, oy, ox, top, color=INK, sw=2),
         arrow(ox, oy, right, oy, color=INK, sw=2),
         text(right + 6, oy + 4, xlabel, size=12, color=INK, anchor="start", bold=True),
         text(ox - 4, top - 10, ylabel, size=12, color=INK, anchor="middle", bold=True)]
    return "".join(f)


def polyline(pts, color, sw=2.6):
    d = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ════════════════════════════════════════════════════════════════════════════
# 1. mosfet-four-terminals.svg — 4-термінальна структура MOSFET
# ════════════════════════════════════════════════════════════════════════════
def fig_four_terminals():
    W, H = 740, 320
    f = []

    # Заголовок / пояснення зверху
    tb, _, _ = textbox(370, 24, "MOSFET як чотириполюсник: вплив виводу підкладки (Bulk / Body)",
                       size=14, bold=True, pad=8, fill="#eef2f7", stroke="#8ba3c7")
    f.append(tb)

    # p-підкладка
    bx, by, bw, bh = 140, 80, 430, 150
    f.append(rect(bx, by, bw, bh, fill=P_BODY, stroke=P_EDGE, sw=1.8, rx=0))
    f.append(text(bx + 45, by + bh - 22, "p-підкладка (Body)", size=12, color="#445544", bold=True))
    f.append(text(bx + 45, by + bh - 6, "NA ≈ 10¹⁷ см⁻³", size=10, color=MUTED))

    # n⁺ витік (Source)
    f.append(rect(bx + 35, by, 85, 45, fill=NREG, stroke=NEG, sw=1.5, rx=0))
    f.append(text(bx + 77, by + 26, "n⁺ Витік (S)", size=11, color=NEG, bold=True))

    # n⁺ стік (Drain)
    f.append(rect(bx + bw - 120, by, 85, 45, fill=NREG, stroke=NEG, sw=1.5, rx=0))
    f.append(text(bx + bw - 77, by + 26, "n⁺ Стік (D)", size=11, color=NEG, bold=True))

    # Оксид затвора
    gx = bx + 150
    gw = bw - 300
    f.append(rect(gx, by - 12, gw, 12, fill=OXIDE, stroke=OX_EDG, sw=1.3, rx=0))
    f.append(text(gx + gw / 2, by - 4, "Оксид SiO₂", size=10, color="#8a6508"))

    # Затвор (Gate)
    f.append(rect(gx + 10, by - 36, gw - 20, 24, fill=GATE, stroke=INK, sw=1.5, rx=2))
    f.append(text(gx + gw / 2, by - 20, "Затвор (G)", size=12, bold=True))

    # Збіднена область під оксидом та n⁺ областями
    f.append(rect(bx + 25, by + 45, bw - 50, 45, fill=DEPL, stroke="#c2b0d4", sw=1.2, rx=0))
    f.append(text(bx + bw / 2, by + 72, "Збіднений шар (нерухомий заряд NA⁻)", size=11, color="#6a4985"))

    # Виводи з контактами
    # Gate lead
    f.append(line(gx + gw / 2, by - 36, gx + gw / 2, 50, color=INK, sw=2))
    f.append(circle(gx + gw / 2, 50, 4, fill=INK))
    f.append(text(gx + gw / 2, 44, "VG", size=12, bold=True))

    # Source lead
    sx = bx + 77
    f.append(line(sx, by, sx, 50, color=NEG, sw=2))
    f.append(circle(sx, 50, 4, fill=NEG))
    f.append(text(sx, 44, "VS", size=12, color=NEG, bold=True))

    # Drain lead
    dx = bx + bw - 77
    f.append(line(dx, by, dx, 50, color=POS, sw=2))
    f.append(circle(dx, 50, 4, fill=POS))
    f.append(text(dx, 44, "VD", size=12, color=POS, bold=True))

    # Body lead (знизу)
    bx_lead = bx + bw / 2
    f.append(rect(bx_lead - 40, by + bh - 14, 80, 14, fill="#b5c4b1", stroke="#5a6e57", sw=1.2, rx=0))
    f.append(text(bx_lead, by + bh - 4, "p⁺ контакт", size=10, bold=True))
    f.append(line(bx_lead, by + bh, bx_lead, by + bh + 30, color=INK, sw=2))
    f.append(circle(bx_lead, by + bh + 30, 4, fill=INK))
    f.append(text(bx_lead, by + bh + 46, "VB (Підкладка / Bulk)", size=12, bold=True))

    # Напруга VSB стрілка
    f.append(arrow(sx - 35, 50, sx - 35, by + bh + 30, color="#8e44ad", sw=1.8))
    f.append(text(sx - 42, (50 + by + bh + 30) / 2 - 8, "VSB = VS − VB", size=11, color="#8e44ad", bold=True, anchor="end"))
    f.append(text(sx - 42, (50 + by + bh + 30) / 2 + 8, "(Зворотне зміщення)", size=10, color=MUTED, anchor="end"))

    # Правий блок примітки
    tb_info, _, _ = textbox(645, 155, "Коли VS > VB:\nперехід витік-підкладка\nзворотно зміщений.\nЗбіднений шар росте!",
                            size=10, pad=6, fill="#fdfbf0", stroke="#dcd3a1")
    f.append(tb_info)

    render_svg("mosfet-four-terminals.svg", W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. depletion-widening.svg — розширення збідненої області при рості VSB
# ════════════════════════════════════════════════════════════════════════════
def fig_depletion_widening():
    W, H = 760, 320
    f = []

    # Ліва панель: VSB = 0
    lx0, ly0, pw, ph = 30, 40, 330, 260
    f.append(rect(lx0, ly0, pw, ph, fill="#ffffff", stroke="#ccd3dd", sw=1.5, rx=6))
    f.append(text(lx0 + pw / 2, ly0 + 20, "Випадок 1: VSB = 0 В (Витік з'єднаний з тілом)", size=11, bold=True))

    # MOSFET VSB=0
    mx, my, mw, mh = lx0 + 20, ly0 + 75, pw - 40, 150
    f.append(rect(mx, my, mw, mh, fill=P_BODY, stroke=P_EDGE, sw=1.5, rx=0))
    # n+ areas
    f.append(rect(mx + 10, my, 55, 35, fill=NREG, stroke=NEG, sw=1.2, rx=0))
    f.append(text(mx + 37, my + 22, "n⁺ (S)", size=10, bold=True))
    f.append(rect(mx + mw - 65, my, 55, 35, fill=NREG, stroke=NEG, sw=1.2, rx=0))
    f.append(text(mx + mw - 37, my + 22, "n⁺ (D)", size=10, bold=True))
    # Oxide + Gate
    gx = mx + 75
    gw = mw - 150
    f.append(rect(gx, my - 8, gw, 8, fill=OXIDE, stroke=OX_EDG, sw=1.1, rx=0))
    f.append(rect(gx + 10, my - 24, gw - 20, 16, fill=GATE, stroke=INK, sw=1.2, rx=0))
    f.append(text(gx + gw / 2, my - 13, "Затвор VG = Vth0", size=10, bold=True))
    # Inversion layer
    f.append(rect(gx, my, gw, 6, fill=CHAN, stroke=NEG, sw=1.0, rx=0))
    f.append(text(gx + gw / 2, my + 4, "Інверсійний шар e⁻", size=9, color=NEG))
    # Narrow depletion layer
    f.append(rect(gx - 10, my + 6, gw + 20, 32, fill=DEPL, stroke="#b9a0c8", sw=1.1, rx=0))
    f.append(text(gx + gw / 2, my + 24, "Збіднений шар Wdep0 (вузький)", size=10, color="#6a4985"))
    for i in range(4):
        f.append(text(gx + 15 + i * 28, my + 35, "−", size=12, color="#6a4985", bold=True))

    f.append(text(lx0 + pw / 2, ly0 + ph - 12, "Початковий поріг Vth0 ≈ 0.40 В", size=11, color=FIELD, bold=True))

    # Права панель: VSB > 0 (наприклад 2 В)
    rx0 = lx0 + pw + 40
    f.append(rect(rx0, ly0, pw, ph, fill="#ffffff", stroke="#ccd3dd", sw=1.5, rx=6))
    f.append(text(rx0 + pw / 2, ly0 + 20, "Випадок 2: VSB = 2.0 В (Зворотне зміщення)", size=11, bold=True))

    # MOSFET VSB=2
    mx2, my2 = rx0 + 20, ly0 + 75
    f.append(rect(mx2, my2, mw, mh, fill=P_BODY, stroke=P_EDGE, sw=1.5, rx=0))
    # n+ areas
    f.append(rect(mx2 + 10, my2, 55, 35, fill=NREG, stroke=NEG, sw=1.2, rx=0))
    f.append(text(mx2 + 37, my2 + 22, "n⁺ (S)", size=10, bold=True))
    f.append(rect(mx2 + mw - 65, my2, 55, 35, fill=NREG, stroke=NEG, sw=1.2, rx=0))
    f.append(text(mx2 + mw - 37, my2 + 22, "n⁺ (D)", size=10, bold=True))
    # Oxide + Gate
    gx2 = mx2 + 75
    f.append(rect(gx2, my2 - 8, gw, 8, fill=OXIDE, stroke=OX_EDG, sw=1.1, rx=0))
    f.append(rect(gx2 + 10, my2 - 24, gw - 20, 16, fill=GATE, stroke=INK, sw=1.2, rx=0))
    f.append(text(gx2 + gw / 2, my2 - 13, "Затвор VG = Vth > Vth0", size=10, bold=True))
    # Inversion layer
    f.append(rect(gx2, my2, gw, 6, fill=CHAN, stroke=NEG, sw=1.0, rx=0))
    f.append(text(gx2 + gw / 2, my2 + 4, "Інверсійний шар e⁻", size=9, color=NEG))
    # WIDE depletion layer
    f.append(rect(gx2 - 15, my2 + 6, gw + 30, 70, fill=DEPL, stroke="#b9a0c8", sw=1.2, rx=0))
    f.append(text(gx2 + gw / 2, my2 + 25, "Розширений шар Wdep (глибокий)", size=10, color="#6a4985", bold=True))
    f.append(text(gx2 + gw / 2, my2 + 42, "Великий нерухомий заряд QB", size=10, color="#6a4985"))
    for row in range(2):
        for i in range(5):
            f.append(text(gx2 + 10 + i * 24, my2 + 55 + row * 14, "−", size=12, color="#6a4985", bold=True))

    f.append(text(rx0 + pw / 2, ly0 + ph - 12, "Підвищений поріг Vth ≈ 0.75 В (+87%)", size=11, color=POS, bold=True))

    render_svg("depletion-widening.svg", W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. threshold-vs-vsb.svg — графік Vth від VSB
# ════════════════════════════════════════════════════════════════════════════
def fig_threshold_vs_vsb():
    W, H = 720, 340
    f = []

    # Рамка графіка
    ox, oy = 90, 270
    top, right = 45, 520
    f.append(axes(ox, oy, top, right, "Напруга VSB (В)", "Поріг Vth (В)"))

    # Сітка
    for v in [1.0, 2.0, 3.0]:
        gx = ox + v * 130
        f.append(line(gx, oy, gx, top + 15, color="#e5e7eb", sw=1.0, dash="3,3"))
        f.append(text(gx, oy + 18, "%.1f" % v, size=11, color=MUTED))

    f.append(text(ox, oy + 18, "0.0", size=11, color=MUTED))

    for th in [0.4, 0.6, 0.8, 1.0, 1.2]:
        gy = oy - (th - 0.2) * 220
        f.append(line(ox, gy, right, gy, color="#e5e7eb", sw=1.0, dash="3,3"))
        f.append(text(ox - 24, gy + 4, "%.1f" % th, size=11, color=MUTED))

    phi2 = 0.7
    sq0 = math.sqrt(phi2)
    vth0 = 0.40

    def calc_pts(gamma):
        pts = []
        for i in range(31):
            vsb = i * 0.1
            vth = vth0 + gamma * (math.sqrt(phi2 + vsb) - sq0)
            px = ox + vsb * 130
            py = oy - (vth - 0.2) * 220
            pts.append((px, py))
        return pts

    pts_high = calc_pts(0.70)
    pts_med  = calc_pts(0.45)
    pts_low  = calc_pts(0.20)

    f.append(polyline(pts_high, POS, sw=2.4))
    f.append(polyline(pts_med, "#8e44ad", sw=2.4))
    f.append(polyline(pts_low, FIELD, sw=2.4))

    # Підписи до кривих праворуч від графіка (щоб лінії не перетинали текст)
    leg_x = right + 20
    f.append(circle(leg_x, 70, 4, fill=POS))
    f.append(text(leg_x + 12, 74, "γ = 0.70 В¹/² (сильне NA)", size=11, color=POS, bold=True, anchor="start"))

    f.append(circle(leg_x, 125, 4, fill="#8e44ad"))
    f.append(text(leg_x + 12, 129, "γ = 0.45 В¹/² (bulk CMOS)", size=11, color="#8e44ad", bold=True, anchor="start"))

    f.append(circle(leg_x, 180, 4, fill=FIELD))
    f.append(text(leg_x + 12, 184, "γ = 0.20 В¹/² (тонкий оксид)", size=11, color=FIELD, bold=True, anchor="start"))

    # Позначка Vth0
    f.append(circle(ox, oy - (vth0 - 0.2) * 220, 5, fill=INK))
    f.append(text(ox + 45, oy - (vth0 - 0.2) * 220 + 14, "Vth0 = 0.40 В", size=11, bold=True))

    # Дельта Vth стрілка
    p_med_end = pts_med[20] # at VSB = 2.0
    f.append(line(ox + 260, oy - (vth0 - 0.2) * 220, ox + 260, p_med_end[1], color="#e67e22", sw=1.5, dash="4,2"))
    f.append(arrow(ox + 266, oy - (vth0 - 0.2) * 220, ox + 266, p_med_end[1], color="#e67e22", sw=1.6))
    f.append(text(ox + 275, (oy - (vth0 - 0.2) * 220 + p_med_end[1]) / 2, "ΔVth ∝ √VSB", size=11, color="#e67e22", bold=True, anchor="start"))

    render_svg("threshold-vs-vsb.svg", W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. cascode-body-effect.svg — ефект підкладки в каскодному підсилювачі
# ════════════════════════════════════════════════════════════════════════════
def fig_cascode_body_effect():
    W, H = 740, 360
    f = []

    # Заголовок
    tb, _, _ = textbox(370, 22, "Каскодний каскад: плаваючий витік каскода та втрата динамічного діапазону",
                       size=14, bold=True, pad=6, fill="#f4f6f8", stroke="#bac7d5")
    f.append(tb)

    # Ліва частина — принципова схема
    cx = 160
    # Навантаження RD зверху
    f.append(line(cx, 55, cx, 80, color=LINE, sw=2))
    f.append(rect(cx - 15, 80, 30, 35, fill="#f9f9f9", stroke=LINE, sw=1.5, rx=0))
    f.append(text(cx, 101, "RD", size=11, bold=True))
    f.append(text(cx, 48, "VDD", size=12, color=POS, bold=True))
    f.append(circle(cx, 55, 3, fill=POS))

    # Вихід Vout
    f.append(line(cx, 115, cx, 140, color=LINE, sw=2))
    f.append(line(cx, 128, cx + 45, 128, color=LINE, sw=1.8))
    f.append(circle(cx + 45, 128, 3, fill=LINE))
    f.append(text(cx + 52, 132, "Vout", size=11, bold=True, anchor="start"))

    # Верхній транзистор M2 (каскод)
    m2y = 150
    f.append(line(cx, 140, cx, m2y, color=LINE, sw=2))
    # NMOS символ M2
    f.append(line(cx - 20, m2y, cx + 20, m2y, color=LINE, sw=1.8))
    f.append(line(cx - 20, m2y + 16, cx + 20, m2y + 16, color=LINE, sw=1.8))
    f.append(line(cx - 25, m2y + 8, cx - 20, m2y + 8, color=LINE, sw=1.8)) # Gate lead
    f.append(line(cx - 45, m2y + 8, cx - 25, m2y + 8, color=LINE, sw=1.8))
    f.append(text(cx - 50, m2y + 12, "VBIAS", size=11, bold=True, anchor="end"))
    f.append(text(cx + 28, m2y + 8, "M2 (каскод)", size=10, bold=True, anchor="start"))

    # Bulk M2 підключений до землі (глобальна підкладка)
    f.append(line(cx + 10, m2y + 8, cx + 60, m2y + 8, color="#8e44ad", sw=1.5, dash="3,2"))
    f.append(line(cx + 60, m2y + 8, cx + 60, 305, color="#8e44ad", sw=1.5, dash="3,2"))
    f.append(line(cx + 60, 305, cx, 305, color="#8e44ad", sw=1.5, dash="3,2"))

    # Проміжний вузол VX
    f.append(line(cx, m2y + 16, cx, m2y + 40, color=LINE, sw=2))
    vxy = m2y + 40
    f.append(circle(cx, vxy, 3, fill=LINE))
    f.append(text(cx - 10, vxy + 4, "VX = 0.35 В (Витік M2)", size=10, color="#8e44ad", bold=True, anchor="end"))

    # Нижній транзистор M1 (вхідний)
    m1y = vxy + 25
    f.append(line(cx, vxy, cx, m1y, color=LINE, sw=2))
    f.append(line(cx - 20, m1y, cx + 20, m1y, color=LINE, sw=1.8))
    f.append(line(cx - 20, m1y + 16, cx + 20, m1y + 16, color=LINE, sw=1.8))
    f.append(line(cx - 45, m1y + 8, cx - 20, m1y + 8, color=LINE, sw=1.8))
    f.append(text(cx - 50, m1y + 12, "Vin", size=11, color=NEG, bold=True, anchor="end"))
    f.append(text(cx + 28, m1y + 8, "M1 (вхідний)", size=10, bold=True, anchor="start"))

    # Витік M1 на GND
    f.append(line(cx, m1y + 16, cx, 305, color=LINE, sw=2))
    # GND символ
    f.append(line(cx - 18, 305, cx + 18, 305, color=LINE, sw=2))
    f.append(line(cx - 11, 310, cx + 11, 310, color=LINE, sw=1.6))
    f.append(line(cx - 4, 315, cx + 4, 315, color=LINE, sw=1.2))
    f.append(text(cx, 330, "GND (0 В)", size=11, color=MUTED))

    # Права частина — порівняльні картки розрахунку
    rx = 400
    tb1, _, _ = textbox(rx + 150, 110,
                        "Транзистор M1 (Витік на GND):\n"
                        "• VSB1 = 0 В\n"
                        "• Поріг Vth1 = Vth0 = 0.40 В\n"
                        "• VDS,sat1 ≈ 0.15 В → VX = 0.35 В",
                        size=11, pad=8, fill="#f0faf0", stroke="#7bb87b")
    f.append(tb1)

    tb2, _, _ = textbox(rx + 150, 230,
                        "Каскодний транзистор M2 (Плаваючий витік):\n"
                        "• VSB2 = VX = 0.35 В\n"
                        "• Поріг зростає: Vth2 = 0.58 В (+45%!)\n"
                        "• Потрібна вища напруга VBIAS = VX + Vth2 + Vov\n"
                        "• Зменшується розмах виходу: Vout,min = VX + VDS,sat2",
                        size=11, pad=8, fill="#fdf0f0", stroke="#d97777")
    f.append(tb2)

    # Підсумкова примітка внизу
    f.append(text(370, 345, "Ефект підкладки «з'їдає» запас напруги (headroom) у низьковольтних аналогових схемах.",
                  size=11, color=LINE, italic=True))

    render_svg("cascode-body-effect.svg", W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. nand-stack-delay.svg — стек транзисторів у NAND
# ════════════════════════════════════════════════════════════════════════════
def fig_nand_stack_delay():
    W, H = 760, 360
    f = []

    # Заголовок
    tb, _, _ = textbox(380, 22, "Стек транзисторів у 3-NAND: послідовне зростання порогу та падіння струму",
                       size=14, bold=True, pad=6, fill="#f4f6f8", stroke="#bac7d5")
    f.append(tb)

    # Ліворуч: Схема 3-NMOS стеку
    cx = 140
    f.append(text(cx, 55, "Вихід Y (до ємності CL)", size=11, bold=True))
    f.append(line(cx, 63, cx, 80, color=LINE, sw=2))

    # M3 (верхній)
    m3y = 90
    f.append(rect(cx - 25, m3y, 50, 25, fill="#fed7d7", stroke=POS, sw=1.5, rx=3))
    f.append(text(cx, m3y + 16, "M3 (A)", size=11, bold=True))
    f.append(line(cx, m3y + 25, cx, m3y + 45, color=LINE, sw=2))

    # Вузол VN2
    vn2y = m3y + 45
    f.append(circle(cx, vn2y, 3, fill=LINE))
    f.append(text(cx + 10, vn2y + 4, "VN2 ≈ 0.6 В", size=10, color=POS, bold=True, anchor="start"))

    # M2 (середній)
    m2y = vn2y + 15
    f.append(rect(cx - 25, m2y, 50, 25, fill="#feebc8", stroke="#dd6b20", sw=1.5, rx=3))
    f.append(text(cx, m2y + 16, "M2 (B)", size=11, bold=True))
    f.append(line(cx, m2y + 25, cx, m2y + 45, color=LINE, sw=2))

    # Вузол VN1
    vn1y = m2y + 45
    f.append(circle(cx, vn1y, 3, fill=LINE))
    f.append(text(cx + 10, vn1y + 4, "VN1 ≈ 0.3 В", size=10, color="#dd6b20", bold=True, anchor="start"))

    # M1 (нижній)
    m1y = vn1y + 15
    f.append(rect(cx - 25, m1y, 50, 25, fill="#c6f6d5", stroke=FIELD, sw=1.5, rx=3))
    f.append(text(cx, m1y + 16, "M1 (C)", size=11, bold=True))
    f.append(line(cx, m1y + 25, cx, 290, color=LINE, sw=2))

    # GND
    f.append(line(cx - 16, 290, cx + 16, 290, color=LINE, sw=2))
    f.append(line(cx - 10, 295, cx + 10, 295, color=LINE, sw=1.5))
    f.append(line(cx - 4, 300, cx + 4, 300, color=LINE, sw=1.2))
    f.append(text(cx, 316, "GND (0 В, Bulk)", size=11, color=MUTED))

    # Спільна підкладка з'єднана з GND
    f.append(line(cx - 25, m3y + 12, cx - 55, m3y + 12, color="#8e44ad", sw=1.3, dash="2,2"))
    f.append(line(cx - 25, m2y + 12, cx - 55, m2y + 12, color="#8e44ad", sw=1.3, dash="2,2"))
    f.append(line(cx - 25, m1y + 12, cx - 55, m1y + 12, color="#8e44ad", sw=1.3, dash="2,2"))
    f.append(line(cx - 55, m3y + 12, cx - 55, 290, color="#8e44ad", sw=1.3, dash="2,2"))
    f.append(line(cx - 55, 290, cx, 290, color="#8e44ad", sw=1.3, dash="2,2"))

    # Праворуч: таблиця параметрів і діаграма затримки
    rx = 310
    f.append(rect(rx, 50, 420, 240, fill="#ffffff", stroke="#cbd5e0", sw=1.4, rx=6))
    f.append(text(rx + 210, 72, "Порівняння транзисторів у стеку (VDD = 1.0 В):", size=11, bold=True))

    # Рядки таблиці
    # Header
    f.append(rect(rx + 10, 85, 400, 24, fill="#edf2f7", stroke="#cbd5e0", sw=1.0, rx=2))
    f.append(text(rx + 35, 101, "Ключ", size=10, bold=True))
    f.append(text(rx + 90, 101, "VS (В)", size=10, bold=True))
    f.append(text(rx + 160, 101, "Vth (В)", size=10, bold=True))
    f.append(text(rx + 250, 101, "VGS − Vth (В)", size=10, bold=True))
    f.append(text(rx + 350, 101, "Струм ID", size=10, bold=True))

    # Row 1: M1
    f.append(text(rx + 35, 126, "M1", size=10, color=FIELD, bold=True))
    f.append(text(rx + 90, 126, "0.00", size=10))
    f.append(text(rx + 160, 126, "0.35 В", size=10, color=FIELD, bold=True))
    f.append(text(rx + 250, 126, "0.65 В", size=10))
    f.append(text(rx + 350, 126, "100% (базовий)", size=10, color=FIELD))

    # Row 2: M2
    f.append(text(rx + 35, 150, "M2", size=10, color="#dd6b20", bold=True))
    f.append(text(rx + 90, 150, "0.28", size=10))
    f.append(text(rx + 160, 150, "0.48 В", size=10, color="#dd6b20", bold=True))
    f.append(text(rx + 250, 150, "0.24 В", size=10))
    f.append(text(rx + 350, 150, "≈ 55%", size=10, color="#dd6b20"))

    # Row 3: M3
    f.append(text(rx + 35, 174, "M3", size=10, color=POS, bold=True))
    f.append(text(rx + 90, 174, "0.55", size=10))
    f.append(text(rx + 160, 174, "0.61 В", size=10, color=POS, bold=True))
    f.append(text(rx + 250, 174, "0.04 В (дуже мале!)", size=10, color=POS, bold=True))
    f.append(text(rx + 350, 174, "≈ 15% (задушений)", size=10, color=POS, bold=True))

    # Висновок у картці
    f.append(line(rx + 15, 196, rx + 405, 196, color="#e2e8f0", sw=1.0))
    f.append(text(rx + 210, 216, "Наслідок: затримка 3-NAND зростає не в 3 рази, а в 5-7 разів!",
                  size=11, color=POS, bold=True))
    f.append(text(rx + 210, 236, "Тому цифрові бібліотеки обмежують висоту стеку до ≤ 3–4 ключів.",
                  size=10, color=MUTED))

    # Нижній загальний підпис
    f.append(text(380, 345, "Ефект підкладки сповільнює розряд вихідного вузла через лавиноподібне зменшення овердрайву верхніх транзисторів.",
                  size=11, color=LINE, italic=True))

    render_svg("nand-stack-delay.svg", W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. pass-transistor-drop.svg — втрата напруги в Pass-Transistor Logic
# ════════════════════════════════════════════════════════════════════════════
def fig_pass_transistor_drop():
    W, H = 740, 320
    f = []

    # Заголовок
    tb, _, _ = textbox(370, 22, "Логіка на передавальних транзисторах: втрата рівня '1' через ефект підкладки",
                       size=14, bold=True, pad=6, fill="#f4f6f8", stroke="#bac7d5")
    f.append(tb)

    # Ліва схема: поодинокий NMOS ключ
    lx = 180
    f.append(rect(lx - 130, 50, 260, 230, fill="#ffffff", stroke="#cbd5e0", sw=1.4, rx=6))
    f.append(text(lx, 72, "Поодинокий NMOS-ключ", size=12, bold=True))

    # Вхід Vin = VDD
    f.append(circle(lx - 90, 130, 3, fill=POS))
    f.append(text(lx - 90, 115, "Vin = VDD", size=11, color=POS, bold=True))
    f.append(line(lx - 90, 130, lx - 40, 130, color=LINE, sw=2))

    # NMOS
    f.append(rect(lx - 40, 115, 80, 30, fill=NREG, stroke=NEG, sw=1.5, rx=3))
    f.append(text(lx, 133, "NMOS", size=11, color=NEG, bold=True))
    # Gate
    f.append(line(lx, 115, lx, 90, color=LINE, sw=1.8))
    f.append(text(lx, 85, "VG = VDD (1.2 В)", size=10, bold=True))

    # Bulk до GND
    f.append(line(lx, 145, lx, 170, color="#8e44ad", sw=1.5, dash="3,2"))
    f.append(text(lx, 185, "Bulk = 0 В", size=10, color="#8e44ad"))

    # Вихід
    f.append(line(lx + 40, 130, lx + 90, 130, color=LINE, sw=2))
    f.append(circle(lx + 90, 130, 3, fill=LINE))
    # Ємність навантаження
    f.append(line(lx + 75, 130, lx + 75, 150, color=LINE, sw=1.5))
    f.append(line(lx + 65, 150, lx + 85, 150, color=LINE, sw=2))
    f.append(line(lx + 65, 155, lx + 85, 155, color=LINE, sw=2))
    f.append(line(lx + 75, 155, lx + 75, 175, color=LINE, sw=1.5))
    f.append(text(lx + 100, 160, "CL", size=10, color=MUTED))

    # Пояснення деградації
    f.append(text(lx, 215, "Vout = VDD − Vth(Vout)", size=11, color=POS, bold=True))
    f.append(text(lx, 235, "Замість 1.2 В → лише ≈ 0.65 В!", size=10, color=POS))
    f.append(text(lx, 255, "(Vth зріс з 0.35 В до 0.55 В)", size=9, color=MUTED))

    # Права схема: CMOS Transmission Gate (вирішення проблеми)
    rx = 540
    f.append(rect(rx - 150, 50, 300, 230, fill="#ffffff", stroke="#cbd5e0", sw=1.4, rx=6))
    f.append(text(rx, 72, "Рішення: CMOS Transmission Gate", size=12, bold=True))

    # Вхід Vin
    f.append(circle(rx - 110, 130, 3, fill=POS))
    f.append(text(rx - 110, 115, "Vin = VDD", size=11, color=POS, bold=True))
    f.append(line(rx - 110, 130, rx - 65, 130, color=LINE, sw=2))

    # NMOS + PMOS паралельно
    f.append(line(rx - 65, 130, rx - 50, 105, color=LINE, sw=1.5))
    f.append(line(rx - 65, 130, rx - 50, 155, color=LINE, sw=1.5))

    # PMOS зверху
    f.append(rect(rx - 50, 90, 70, 26, fill="#fed7d7", stroke=POS, sw=1.3, rx=3))
    f.append(text(rx - 15, 107, "PMOS (EN)", size=10, color=POS, bold=True))
    f.append(text(rx - 15, 80, "Bulk = VDD", size=9, color=POS))

    # NMOS знизу
    f.append(rect(rx - 50, 142, 70, 26, fill=NREG, stroke=NEG, sw=1.3, rx=3))
    f.append(text(rx - 15, 159, "NMOS (EN)", size=10, color=NEG, bold=True))
    f.append(text(rx - 15, 182, "Bulk = GND", size=9, color=NEG))

    f.append(line(rx + 20, 105, rx + 35, 130, color=LINE, sw=1.5))
    f.append(line(rx + 20, 155, rx + 35, 130, color=LINE, sw=1.5))

    # Вихід
    f.append(line(rx + 35, 130, rx + 100, 130, color=LINE, sw=2))
    f.append(circle(rx + 100, 130, 3, fill=FIELD))
    f.append(text(rx + 100, 115, "Vout = VDD", size=11, color=FIELD, bold=True))

    f.append(text(rx, 215, "Повний розмах 0...VDD без втрати!", size=11, color=FIELD, bold=True))
    f.append(text(rx, 235, "PMOS дотягує '1' до повного VDD,", size=10, color=LINE))
    f.append(text(rx, 252, "NMOS дотягує '0' до чистого 0 В.", size=10, color=LINE))

    # Підпис внизу
    f.append(text(370, 305, "Ефект підкладки робить поодинокий NMOS нездатним передати повний логічний рівень «1».",
                  size=11, color=LINE, italic=True))

    render_svg("pass-transistor-drop.svg", W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. body-biasing-fbb-rbb.svg — адаптивне зміщення підкладки (FBB / RBB)
# ════════════════════════════════════════════════════════════════════════════
def fig_body_biasing():
    W, H = 780, 330
    f = []

    # Заголовок
    tb, _, _ = textbox(390, 22, "Адаптивне керування підкладкою (Adaptive Body Biasing): FBB проти RBB",
                       size=14, bold=True, pad=6, fill="#f4f6f8", stroke="#bac7d5")
    f.append(tb)

    card_w = 230
    card_h = 245
    card_y = 50

    # 1. Ліва колонка: FBB (Forward Body Bias)
    c1x = 20
    f.append(rect(c1x, card_y, card_w, card_h, fill="#f0fff4", stroke="#68d391", sw=1.5, rx=6))
    f.append(text(c1x + card_w / 2, card_y + 24, "Пряме зміщення (FBB)", size=12, color=FIELD, bold=True))
    f.append(text(c1x + card_w / 2, card_y + 44, "VBS = +0.3...+0.4 В > 0", size=11, color=FIELD, bold=True))

    f.append(line(c1x + 15, card_y + 58, c1x + card_w - 15, card_y + 58, color="#c6f6d5", sw=1.0))

    f.append(text(c1x + card_w / 2, card_y + 80, "Фізика процесу:", size=11, bold=True))
    f.append(text(c1x + card_w / 2, card_y + 98, "• Звуження збідненого шару", size=10))
    f.append(text(c1x + card_w / 2, card_y + 114, "• Зниження порогу: Vth ↓ (−100 мВ)", size=10, color=FIELD, bold=True))
    f.append(text(c1x + card_w / 2, card_y + 130, "• Збільшення струму: Ion ↑ (+30%)", size=10, color=FIELD, bold=True))

    f.append(line(c1x + 15, card_y + 148, c1x + card_w - 15, card_y + 148, color="#c6f6d5", sw=1.0))

    f.append(text(c1x + card_w / 2, card_y + 170, "Призначення:", size=11, bold=True))
    f.append(text(c1x + card_w / 2, card_y + 190, "Турбо-режим процесора,", size=10))
    f.append(text(c1x + card_w / 2, card_y + 206, "компенсація повільних кутів (SS),", size=10))
    f.append(text(c1x + card_w / 2, card_y + 222, "максимальна тактова частота.", size=10))

    # 2. Середня колонка: Zero Bias (Стандарт)
    c2x = c1x + card_w + 25
    f.append(rect(c2x, card_y, card_w, card_h, fill="#ffffff", stroke="#cbd5e0", sw=1.4, rx=6))
    f.append(text(c2x + card_w / 2, card_y + 24, "Нульове зміщення (ZBB)", size=12, bold=True))
    f.append(text(c2x + card_w / 2, card_y + 44, "VBS = 0 В (Витік = Тіло)", size=11, color=MUTED, bold=True))

    f.append(line(c2x + 15, card_y + 58, c2x + card_w - 15, card_y + 58, color="#e2e8f0", sw=1.0))

    f.append(text(c2x + card_w / 2, card_y + 80, "Фізика процесу:", size=11, bold=True))
    f.append(text(c2x + card_w / 2, card_y + 98, "• Стандартна ширина Wdep0", size=10))
    f.append(text(c2x + card_w / 2, card_y + 114, "• Номінальний поріг Vth0", size=10, bold=True))
    f.append(text(c2x + card_w / 2, card_y + 130, "• Номінальні Ion та Ioff", size=10))

    f.append(line(c2x + 15, card_y + 148, c2x + card_w - 15, card_y + 148, color="#e2e8f0", sw=1.0))

    f.append(text(c2x + card_w / 2, card_y + 170, "Призначення:", size=11, bold=True))
    f.append(text(c2x + card_w / 2, card_y + 190, "Стандартний робочий режим,", size=10))
    f.append(text(c2x + card_w / 2, card_y + 206, "збалансована енергоефективність", size=10))
    f.append(text(c2x + card_w / 2, card_y + 222, "та швидкодія за нормальної T.", size=10))

    # 3. Права колонка: RBB (Reverse Body Bias)
    c3x = c2x + card_w + 25
    f.append(rect(c3x, card_y, card_w, card_h, fill="#fffaf0", stroke="#ed8936", sw=1.5, rx=6))
    f.append(text(c3x + card_w / 2, card_y + 24, "Зворотне зміщення (RBB)", size=12, color="#c05621", bold=True))
    f.append(text(c3x + card_w / 2, card_y + 44, "VBS = −0.5...−1.5 В < 0", size=11, color="#c05621", bold=True))

    f.append(line(c3x + 15, card_y + 58, c3x + card_w - 15, card_y + 58, color="#feebc8", sw=1.0))

    f.append(text(c3x + card_w / 2, card_y + 80, "Фізика процесу:", size=11, bold=True))
    f.append(text(c3x + card_w / 2, card_y + 98, "• Розширення збідненого шару", size=10))
    f.append(text(c3x + card_w / 2, card_y + 114, "• Зростання порогу: Vth ↑ (+150 мВ)", size=10, color="#c05621", bold=True))
    f.append(text(c3x + card_w / 2, card_y + 130, "• Придушення витоку: Ioff ↓↓ (10-100×)", size=10, color=POS, bold=True))

    f.append(line(c3x + 15, card_y + 148, c3x + card_w - 15, card_y + 148, color="#feebc8", sw=1.0))

    f.append(text(c3x + card_w / 2, card_y + 170, "Призначення:", size=11, bold=True))
    f.append(text(c3x + card_w / 2, card_y + 190, "Режим глибокого сну (Deep Sleep),", size=10))
    f.append(text(c3x + card_w / 2, card_y + 206, "радикальна економія батареї,", size=10))
    f.append(text(c3x + card_w / 2, card_y + 222, "компенсація гарячих кутів (FF).", size=10))

    # Загальний підпис
    f.append(text(390, 315, "Динамічне зміщення підкладки перетворює ефект підкладки з паразитного явища на інструмент керування енергоспоживанням.",
                  size=11, color=LINE, italic=True))

    render_svg("body-biasing-fbb-rbb.svg", W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 8. fd-soi-isolation.svg — порівняння технологій: Bulk, Deep N-Well, FD-SOI, FinFET
# ════════════════════════════════════════════════════════════════════════════
def fig_fd_soi_isolation():
    W, H = 800, 350
    f = []

    # Заголовок
    tb, _, _ = textbox(400, 22, "Архітектурні методи усунення ефекту підкладки в напівпровідникових технологіях",
                       size=14, bold=True, pad=6, fill="#f4f6f8", stroke="#bac7d5")
    f.append(tb)

    panel_w = 175
    panel_h = 265
    py = 50

    # 1. Bulk CMOS
    p1x = 20
    f.append(rect(p1x, py, panel_w, panel_h, fill="#ffffff", stroke="#cbd5e0", sw=1.4, rx=4))
    f.append(text(p1x + panel_w / 2, py + 18, "1. Planar Bulk CMOS", size=11, bold=True))
    # Drawing Bulk
    bx, by, bw, bh = p1x + 10, py + 35, panel_w - 20, 110
    f.append(rect(bx, by, bw, bh, fill=P_BODY, stroke=P_EDGE, sw=1.2, rx=0))
    f.append(rect(bx + 10, by, 35, 25, fill=NREG, stroke=NEG, sw=1.0, rx=0))
    f.append(rect(bx + bw - 45, by, 35, 25, fill=NREG, stroke=NEG, sw=1.0, rx=0))
    f.append(rect(bx + 48, by - 6, bw - 96, 6, fill=OXIDE, stroke=OX_EDG, sw=1.0, rx=0))
    f.append(rect(bx + 52, by - 16, bw - 104, 10, fill=GATE, stroke=INK, sw=1.0, rx=0))
    f.append(rect(bx + 25, by + 25, bw - 50, 45, fill=DEPL, stroke="#c2b0d4", sw=1.0, rx=0))
    f.append(text(bx + bw / 2, by + bh - 10, "Спільна p-підкладка", size=9, color=MUTED))

    # Notes
    f.append(text(p1x + panel_w / 2, py + 165, "• Сильний ефект підкладки", size=10, color=POS, bold=True))
    f.append(text(p1x + panel_w / 2, py + 182, "• Спільне тіло на GND", size=9))
    f.append(text(p1x + panel_w / 2, py + 199, "• Високий γ ≈ 0.4–0.6 В¹/²", size=9))
    f.append(text(p1x + panel_w / 2, py + 216, "• Деградація стеків і каскодів", size=9))
    f.append(text(p1x + panel_w / 2, py + 242, "Найдешевший процес", size=10, color=MUTED, italic=True))

    # 2. Triple-Well / Deep N-Well
    p2x = p1x + panel_w + 15
    f.append(rect(p2x, py, panel_w, panel_h, fill="#ffffff", stroke="#cbd5e0", sw=1.4, rx=4))
    f.append(text(p2x + panel_w / 2, py + 18, "2. Deep N-Well (Ізоляція)", size=11, bold=True))
    # Drawing Deep N-Well
    bx2 = p2x + 10
    f.append(rect(bx2, by, bw, bh, fill=P_BODY, stroke=P_EDGE, sw=1.2, rx=0))
    f.append(rect(bx2 + 5, by + 15, bw - 10, bh - 20, fill="#e8ecf8", stroke="#788ac0", sw=1.0, rx=0)) # Deep N-Well
    f.append(rect(bx2 + 15, by + 15, bw - 30, bh - 35, fill=P_BODY, stroke=P_EDGE, sw=1.0, rx=0))     # Isolated P-Well
    f.append(rect(bx2 + 25, by + 15, 25, 20, fill=NREG, stroke=NEG, sw=1.0, rx=0))
    f.append(rect(bx2 + bw - 50, by + 15, 25, 20, fill=NREG, stroke=NEG, sw=1.0, rx=0))
    f.append(rect(bx2 + 52, by + 9, bw - 104, 6, fill=OXIDE, stroke=OX_EDG, sw=1.0, rx=0))
    f.append(rect(bx2 + 55, by, bw - 110, 9, fill=GATE, stroke=INK, sw=1.0, rx=0))
    f.append(text(bx2 + bw / 2, by + bh - 8, "Ізольована кишеня", size=9, color=MUTED))

    # Notes
    f.append(text(p2x + panel_w / 2, py + 165, "• Локальне VSB = 0", size=10, color=FIELD, bold=True))
    f.append(text(p2x + panel_w / 2, py + 182, "• Можна з'єднати S з B", size=9))
    f.append(text(p2x + panel_w / 2, py + 199, "• Ізоляція від шуму підкладки", size=9))
    f.append(text(p2x + panel_w / 2, py + 216, "• Велика площа кристала (+40%)", size=9, color="#dd6b20"))
    f.append(text(p2x + panel_w / 2, py + 242, "Для чутливого аналогу", size=10, color=MUTED, italic=True))

    # 3. FD-SOI
    p3x = p2x + panel_w + 15
    f.append(rect(p3x, py, panel_w, panel_h, fill="#f0fff4", stroke="#68d391", sw=1.5, rx=4))
    f.append(text(p3x + panel_w / 2, py + 18, "3. FD-SOI (22 нм / 28 нм)", size=11, color=FIELD, bold=True))
    # Drawing FD-SOI
    bx3 = p3x + 10
    f.append(rect(bx3, by + 45, bw, bh - 45, fill=P_BODY, stroke=P_EDGE, sw=1.2, rx=0)) # Substrate
    f.append(rect(bx3, by + 30, bw, 15, fill=BOX_BG, stroke=BOX_ED, sw=1.2, rx=0))      # BOX
    f.append(text(bx3 + bw / 2, by + 41, "BOX (Оксид 20 нм)", size=9, color="#8a6508"))

    # Ultra-thin Si channel with non-overlapping Source and Drain
    f.append(rect(bx3 + 5, by + 12, 32, 18, fill=NREG, stroke=NEG, sw=1.0, rx=0))
    f.append(rect(bx3 + 37, by + 22, bw - 74, 8, fill=CHAN, stroke=NEG, sw=1.0, rx=0))
    f.append(rect(bx3 + bw - 37, by + 12, 32, 18, fill=NREG, stroke=NEG, sw=1.0, rx=0))

    f.append(rect(bx3 + 45, by + 16, bw - 90, 6, fill=OXIDE, stroke=OX_EDG, sw=1.0, rx=0))
    f.append(rect(bx3 + 48, by + 6, bw - 96, 10, fill=GATE, stroke=INK, sw=1.0, rx=0))
    f.append(text(bx3 + bw / 2, by + bh - 8, "Back-Gate під BOX", size=9, color=FIELD, bold=True))

    # Notes
    f.append(text(p3x + panel_w / 2, py + 165, "• Немає паразитного p-n", size=10, color=FIELD, bold=True))
    f.append(text(p3x + panel_w / 2, py + 182, "• Канал повністю збіднений", size=9))
    f.append(text(p3x + panel_w / 2, py + 199, "• Широкий Back-Bias (±2 В)", size=9, color=FIELD, bold=True))
    f.append(text(p3x + panel_w / 2, py + 216, "• Нульовий класичний γ", size=9))
    f.append(text(p3x + panel_w / 2, py + 242, "Ідеально для IoT / RF", size=10, color=FIELD, italic=True))

    # 4. FinFET / GAA
    p4x = p3x + panel_w + 15
    f.append(rect(p4x, py, panel_w, panel_h, fill="#ffffff", stroke="#cbd5e0", sw=1.4, rx=4))
    f.append(text(p4x + panel_w / 2, py + 18, "4. FinFET (3D Gate)", size=11, bold=True))
    # Drawing FinFET
    bx4 = p4x + 10
    f.append(rect(bx4, by + 50, bw, bh - 50, fill=P_BODY, stroke=P_EDGE, sw=1.2, rx=0)) # Substrate
    f.append(rect(bx4 + 10, by + 40, bw - 20, 10, fill=OXIDE, stroke=OX_EDG, sw=1.0, rx=0)) # STI oxide
    # Vertical Fin
    f.append(rect(bx4 + bw / 2 - 12, by + 10, 24, 40, fill=CHAN, stroke=NEG, sw=1.2, rx=0))
    # 3D Gate wrapped around
    f.append(rect(bx4 + bw / 2 - 24, by, 48, 12, fill=GATE, stroke=INK, sw=1.2, rx=0))
    f.append(rect(bx4 + bw / 2 - 24, by + 10, 10, 30, fill=GATE, stroke=INK, sw=1.0, rx=0))
    f.append(rect(bx4 + bw / 2 + 14, by + 10, 10, 30, fill=GATE, stroke=INK, sw=1.0, rx=0))
    f.append(text(bx4 + bw / 2, by + bh - 8, "Підкладка екранована", size=9, color=MUTED))

    # Notes
    f.append(text(p4x + panel_w / 2, py + 165, "• 3D-контроль з трьох боків", size=10, color=FIELD, bold=True))
    f.append(text(p4x + panel_w / 2, py + 182, "• Підкладка не керує каналом", size=9))
    f.append(text(p4x + panel_w / 2, py + 199, "• Практично нульовий γ", size=9, color=FIELD, bold=True))
    f.append(text(p4x + panel_w / 2, py + 216, "• Висока щільність (< 7 нм)", size=9))
    f.append(text(p4x + panel_w / 2, py + 242, "Стандарт передових CPU", size=10, color=MUTED, italic=True))

    f.append(text(400, 335, "Еволюція структури транзистора звела паразитний вплив підкладки до мінімуму в передових технологіях.",
                  size=11, color=LINE, italic=True))

    render_svg("fd-soi-isolation.svg", W, H, *f)


if __name__ == "__main__":
    fig_four_terminals()
    fig_depletion_widening()
    fig_threshold_vs_vsb()
    fig_cascode_body_effect()
    fig_nand_stack_delay()
    fig_pass_transistor_drop()
    fig_body_biasing()
    fig_fd_soi_isolation()
    print("Згенеровано 8 фігур у ./img/")
