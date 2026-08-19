# -*- coding: utf-8 -*-
"""Фігури до теми «Збіднений MOSFET (depletion-mode)» (book/electronics/microelectronics).
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Локальні кольори напівпровідникових областей
P_BODY = "#eaf0e8"   # p-підкладка
P_EDGE = "#7a8a78"
N_PLUS = "#cfd9ea"   # n⁺ області
OXIDE  = "#fff3b0"   # діелектрик оксиду
OX_EDG = "#d49a24"
GATE   = "#cfd6dd"   # полікремній / метал затвора
CHAN_N = "#bdd7f4"   # імплантований n-канал
DEPL_Z = "#f0e6f6"   # збіднена область без вільних носіїв
DEPL_E = "#9b6bb0"

def carrier(cx, cy, kind, r=4.5):
    if kind == "e":
        return (circle(cx, cy, r, fill="#dfe7f0", stroke=NEG, sw=1.2) +
                line(cx - r * 0.5, cy, cx + r * 0.5, cy, color=NEG, sw=1.2))
    return (circle(cx, cy, r, fill="#fdecea", stroke=POS, sw=1.2) +
            text(cx, cy + r * 0.5, "+", size=int(r * 1.6), color=POS, bold=True))

def polyline(pts, color, sw=2.2, dash=None):
    d = "M " + " L ".join("%.1f,%.1f" % p for p in pts)
    dsh = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, color, sw, dsh)

# ════════════════════════════════════════════════════════════════════════════
# 1. cross-section-depletion.svg: Порівняння збагаченого та збідненого MOSFET
# ════════════════════════════════════════════════════════════════════════════
def fig1_cross_section():
    w, h = 820, 370
    f = []

    # Заголовки двох панелей
    f.append(text(210, 36, "Збагачений nMOS (Enhancement)", size=15, bold=True))
    f.append(text(210, 56, "Vgs = 0 В: каналу немає (вимкнено)", size=12, color=MUTED))

    f.append(text(610, 36, "Збіднений nMOS (Depletion)", size=15, bold=True))
    f.append(text(610, 56, "Vgs = 0 В: вбудований n-канал (увімкнено)", size=12, color=MUTED))

    # --- Ліва панель (Enhancement) ---
    lx, ly, pw, ph = 40, 95, 340, 195
    # p-підкладка
    f.append(rect(lx, ly, pw, ph, fill=P_BODY, stroke=P_EDGE, sw=1.5, rx=0))
    f.append(text(lx + pw/2, ly + ph - 22, "p-кремнієва підкладка (дірки)", size=12, color=P_EDGE, bold=True))
    # n+ витік і стік
    nw = 65
    f.append(rect(lx + 15, ly, nw, 55, fill=N_PLUS, stroke=NEG, sw=1.3, rx=0))
    f.append(text(lx + 15 + nw/2, ly + 32, "n⁺ витік", size=11, bold=True))

    f.append(rect(lx + pw - 15 - nw, ly, nw, 55, fill=N_PLUS, stroke=NEG, sw=1.3, rx=0))
    f.append(text(lx + pw - 15 - nw/2, ly + 32, "n⁺ стік", size=11, bold=True))

    # оксид
    ox_w = 160
    ox_x = lx + (pw - ox_w)/2
    f.append(rect(ox_x, ly - 14, ox_w, 14, fill=OXIDE, stroke=OX_EDG, sw=1.3, rx=0))
    f.append(text(ox_x + ox_w/2, ly - 4, "SiO₂ оксид", size=10, color="#8a5a00"))

    # затвор
    gw = 140
    gx = lx + (pw - gw)/2
    f.append(rect(gx, ly - 36, gw, 22, fill=GATE, stroke=INK, sw=1.3, rx=0))
    f.append(text(gx + gw/2, ly - 21, "Затвор (Vgs = 0 В)", size=11, bold=True))

    # бар'єр між витоком і стоком
    f.append(text(lx + pw/2, ly + 28, "провідного шляху нема", size=11, color=POS, italic=True))
    f.append(line(lx + 80, ly + 42, lx + pw - 80, ly + 42, color=POS, sw=1.5, dash="4,3"))

    # Підпис знизу лівої панелі
    tb1, _, _ = textbox(210, 325, "Нормально закритий (Normally-OFF)\nДля появи каналу потрібна Vgs > Vth > 0 В", size=11, pad=7, fill="#fff5f5", stroke=POS)
    f.append(tb1)

    # --- Права панель (Depletion) ---
    rx, ry = 440, 95
    # p-підкладка
    f.append(rect(rx, ry, pw, ph, fill=P_BODY, stroke=P_EDGE, sw=1.5, rx=0))
    f.append(text(rx + pw/2, ry + ph - 22, "p-кремнієва підкладка", size=12, color=P_EDGE, bold=True))

    # n+ витік і стік
    f.append(rect(rx + 15, ry, nw, 55, fill=N_PLUS, stroke=NEG, sw=1.3, rx=0))
    f.append(text(rx + 15 + nw/2, ry + 32, "n⁺ витік", size=11, bold=True))

    f.append(rect(rx + pw - 15 - nw, ry, nw, 55, fill=N_PLUS, stroke=NEG, sw=1.3, rx=0))
    f.append(text(rx + pw - 15 - nw/2, ry + 32, "n⁺ стік", size=11, bold=True))

    # вбудований n-канал (імплантований місток між n+ областями)
    cw = pw - 30 - 2*nw
    cx = rx + 15 + nw
    f.append(rect(cx, ry, cw, 24, fill=CHAN_N, stroke=NEG, sw=1.4, rx=0))
    f.append(text(rx + pw/2, ry + 16, "вбудований n-канал", size=10, color="#123b96", bold=True))

    # електрони у каналі
    for i in range(5):
        f.append(carrier(cx + cw * (i + 0.5) / 5, ry + 36, "e", r=4))

    # оксид
    f.append(rect(rx + (pw - ox_w)/2, ry - 14, ox_w, 14, fill=OXIDE, stroke=OX_EDG, sw=1.3, rx=0))
    f.append(text(rx + pw/2, ry - 4, "SiO₂ оксид", size=10, color="#8a5a00"))

    # затвор
    f.append(rect(rx + (pw - gw)/2, ry - 36, gw, 22, fill=GATE, stroke=INK, sw=1.3, rx=0))
    f.append(text(rx + pw/2, ry - 21, "Затвор (Vgs = 0 В)", size=11, bold=True))

    # Підпис знизу правої панелі
    tb2, _, _ = textbox(610, 325, "Нормально відкритий (Normally-ON)\nСтрум Idss тече самочинно при Vgs = 0 В", size=11, pad=7, fill="#eff6ff", stroke=NEG)
    f.append(tb2)

    render(os.path.join(IMG, "cross-section-depletion.svg"), w, h, *f)

# ════════════════════════════════════════════════════════════════════════════
# 2. depletion-modes-physics.svg: Три стани збідненого MOSFET
# ════════════════════════════════════════════════════════════════════════════
def fig2_modes():
    w, h = 860, 340
    f = []

    f.append(text(430, 24, "Фізичні режими збідненого nMOS під різною напругою затвора", size=15, bold=True))

    col_w = 260
    col_h = 160
    col_y = 65

    # 1. Режим збіднення / відсікання
    c1_x = 20
    f.append(rect(c1_x, col_y, col_w, col_h, fill=P_BODY, stroke=P_EDGE, sw=1.3, rx=0))
    f.append(rect(c1_x + 8, col_y, 45, 45, fill=N_PLUS, stroke=NEG, sw=1.1, rx=0))
    f.append(text(c1_x + 30, col_y + 26, "n⁺", size=11, bold=True))
    f.append(rect(c1_x + col_w - 53, col_y, 45, 45, fill=N_PLUS, stroke=NEG, sw=1.1, rx=0))
    f.append(text(c1_x + col_w - 30, col_y + 26, "n⁺", size=11, bold=True))

    # збіднена область під затвором перекриває весь канал
    f.append(rect(c1_x + 53, col_y, col_w - 106, 38, fill=DEPL_Z, stroke=DEPL_E, sw=1.2, rx=0))
    f.append(text(c1_x + col_w/2, col_y + 18, "збіднена зона", size=10, color=DEPL_E, bold=True))
    f.append(text(c1_x + col_w/2, col_y + 30, "канал перекрито", size=9.5, color=DEPL_E))

    # затвор з мінусом
    f.append(rect(c1_x + 45, col_y - 28, col_w - 90, 18, fill=GATE, stroke=POS, sw=1.4, rx=0))
    f.append(text(c1_x + col_w/2, col_y - 15, "Vgs < Vth < 0 В (−)", size=10.5, color=POS, bold=True))
    f.append(rect(c1_x + 45, col_y - 10, col_w - 90, 10, fill=OXIDE, stroke=OX_EDG, sw=1.0, rx=0))

    tb_a, _, _ = textbox(c1_x + col_w/2, 275, "Режим збіднення (Depletion)\nПоле виштовхує електрони вглиб.\nКанал перекритий, струм Id = 0.", size=10.5, pad=6, fill="#fdf2f2", stroke=POS)
    f.append(tb_a)

    # 2. Нульовий зсув (Normal ON)
    c2_x = 300
    f.append(rect(c2_x, col_y, col_w, col_h, fill=P_BODY, stroke=P_EDGE, sw=1.3, rx=0))
    f.append(rect(c2_x + 8, col_y, 45, 45, fill=N_PLUS, stroke=NEG, sw=1.1, rx=0))
    f.append(text(c2_x + 30, col_y + 26, "n⁺", size=11, bold=True))
    f.append(rect(c2_x + col_w - 53, col_y, 45, 45, fill=N_PLUS, stroke=NEG, sw=1.1, rx=0))
    f.append(text(c2_x + col_w - 30, col_y + 26, "n⁺", size=11, bold=True))

    # вбудований канал
    f.append(rect(c2_x + 53, col_y, col_w - 106, 26, fill=CHAN_N, stroke=NEG, sw=1.2, rx=0))
    f.append(text(c2_x + col_w/2, col_y + 16, "вбудований n-канал", size=10, color="#123b96", bold=True))
    for i in range(4):
        f.append(carrier(c2_x + 68 + i * 28, col_y + 36, "e", r=3.8))

    # затвор 0 В
    f.append(rect(c2_x + 45, col_y - 28, col_w - 90, 18, fill=GATE, stroke=INK, sw=1.4, rx=0))
    f.append(text(c2_x + col_w/2, col_y - 15, "Vgs = 0 В (земля)", size=10.5, color=INK, bold=True))
    f.append(rect(c2_x + 45, col_y - 10, col_w - 90, 10, fill=OXIDE, stroke=OX_EDG, sw=1.0, rx=0))

    tb_b, _, _ = textbox(c2_x + col_w/2, 275, "Нульовий зсув (Zero Bias)\nКанал проводить номінальний струм.\nСтрум насичення = Idss.", size=10.5, pad=6, fill="#f4f6f8", stroke=LINE)
    f.append(tb_b)

    # 3. Режим збагачення (Enhancement)
    c3_x = 580
    f.append(rect(c3_x, col_y, col_w, col_h, fill=P_BODY, stroke=P_EDGE, sw=1.3, rx=0))
    f.append(rect(c3_x + 8, col_y, 45, 45, fill=N_PLUS, stroke=NEG, sw=1.1, rx=0))
    f.append(text(c3_x + 30, col_y + 26, "n⁺", size=11, bold=True))
    f.append(rect(c3_x + col_w - 53, col_y, 45, 45, fill=N_PLUS, stroke=NEG, sw=1.1, rx=0))
    f.append(text(c3_x + col_w - 30, col_y + 26, "n⁺", size=11, bold=True))

    # розширений канал з накопиченням електронів
    f.append(rect(c3_x + 53, col_y, col_w - 106, 36, fill=CHAN_N, stroke=NEG, sw=1.4, rx=0))
    f.append(text(c3_x + col_w/2, col_y + 15, "накопичення електронів", size=10, color="#123b96", bold=True))
    for i in range(5):
        f.append(carrier(c3_x + 65 + i * 22, col_y + 27, "e", r=3.5))
        f.append(carrier(c3_x + 65 + i * 22, col_y + 44, "e", r=3.5))

    # затвор з плюсом
    f.append(rect(c3_x + 45, col_y - 28, col_w - 90, 18, fill=GATE, stroke=NEG, sw=1.4, rx=0))
    f.append(text(c3_x + col_w/2, col_y - 15, "Vgs > 0 В (+)", size=10.5, color=NEG, bold=True))
    f.append(rect(c3_x + 45, col_y - 10, col_w - 90, 10, fill=OXIDE, stroke=OX_EDG, sw=1.0, rx=0))

    tb_c, _, _ = textbox(c3_x + col_w/2, 275, "Режим збагачення (Enhancement)\nПоле притягує додаткові електрони.\nПровідність зростає: Id > Idss.", size=10.5, pad=6, fill="#eff6ff", stroke=NEG)
    f.append(tb_c)

    render(os.path.join(IMG, "depletion-modes-physics.svg"), w, h, *f)

# ════════════════════════════════════════════════════════════════════════════
# 3. iv-curves.svg: Вихідні та передатна характеристики
# ════════════════════════════════════════════════════════════════════════════
def fig3_iv_curves():
    w, h = 820, 360
    f = []

    f.append(text(410, 24, "Вольт-амперні характеристики збідненого nMOS", size=15, bold=True))

    # Лівий графік: Вихідні характеристики Id(Vds)
    ox1, oy1 = 70, 280
    f.append(arrow(ox1, oy1, ox1, 55, color=INK, sw=1.6))
    f.append(arrow(ox1, oy1, 390, oy1, color=INK, sw=1.6))
    f.append(text(395, oy1 + 4, "Vds", size=12, bold=True, anchor="start"))
    f.append(text(ox1 - 6, 50, "Id", size=12, bold=True, anchor="middle"))

    # Криві Id(Vds) для різних Vgs
    # Vgs = +1V
    f.append(polyline([(ox1, oy1), (130, 130), (170, 95), (370, 85)], color=FIELD, sw=2.2))
    f.append(text(375, 85, "Vgs = +1 В", size=10.5, color=FIELD, anchor="start", bold=True))

    # Vgs = 0V (Idss)
    f.append(polyline([(ox1, oy1), (120, 175), (150, 145), (370, 138)], color=NEG, sw=2.4))
    f.append(text(375, 138, "Vgs = 0 В (Idss)", size=10.5, color=NEG, anchor="start", bold=True))

    # Vgs = -1V
    f.append(polyline([(ox1, oy1), (110, 220), (135, 195), (370, 190)], color="#4f46e5", sw=2.0))
    f.append(text(375, 190, "Vgs = −1 В", size=10.5, color="#4f46e5", anchor="start"))

    # Vgs = -2V
    f.append(polyline([(ox1, oy1), (100, 255), (120, 240), (370, 237)], color="#7c3aed", sw=1.8))
    f.append(text(375, 237, "Vgs = −2 В", size=10.5, color="#7c3aed", anchor="start"))

    # Vgs = Vth = -3V
    f.append(line(ox1, oy1, 370, oy1, color=POS, sw=2.0))
    f.append(text(375, oy1 - 6, "Vgs ≤ −3 В (Vth, відсічка)", size=10, color=POS, anchor="start"))

    # Пунктирна межа насичення
    f.append(polyline([(ox1, oy1), (120, 240), (135, 195), (150, 145), (170, 95)], color=MUTED, sw=1.4, dash="3,3"))
    f.append(text(150, 80, "межа насичення", size=9.5, color=MUTED, italic=True))

    f.append(text(210, 315, "Сімейство вихідних кривих Id(Vds)", size=11, bold=True))

    # Правий графік: Передатна характеристика Id(Vgs)
    ox2, oy2 = 590, 280
    f.append(arrow(ox2, oy2, ox2, 55, color=INK, sw=1.6))
    f.append(arrow(430, oy2, 770, oy2, color=INK, sw=1.6))
    f.append(text(775, oy2 + 4, "Vgs", size=12, bold=True, anchor="start"))
    f.append(text(ox2 - 6, 50, "Id", size=12, bold=True, anchor="middle"))

    # Параболічна крива передатної характеристики
    pts_trans = [(480, 280), (510, 268), (540, 235), (590, 160), (640, 90)]
    f.append(polyline(pts_trans, color=NEG, sw=2.5))

    # Точки Vth, Idss, Vgs=0
    f.append(circle(480, 280, 3.5, fill=POS, stroke=POS))
    f.append(text(480, 298, "Vth = −3 В", size=10.5, color=POS, bold=True))

    f.append(circle(590, 160, 3.5, fill=NEG, stroke=NEG))
    f.append(line(ox2 - 30, 160, ox2 + 30, 160, color=NEG, sw=1.2, dash="3,2"))
    f.append(text(ox2 - 38, 160, "Idss", size=11, color=NEG, bold=True, anchor="end"))
    f.append(text(590, 298, "0 В", size=10.5, color=INK, bold=True))

    # Зони збіднення та збагачення
    f.append(rect(440, 68, 140, 38, fill="#fdf2f2", stroke=POS, sw=1.0))
    f.append(text(510, 84, "Збіднення (Vgs < 0)", size=9.5, color=POS, bold=True))
    f.append(text(510, 98, "Id < Idss", size=9.5, color=POS))

    f.append(rect(605, 68, 145, 38, fill="#eff6ff", stroke=NEG, sw=1.0))
    f.append(text(677, 84, "Збагачення (Vgs > 0)", size=9.5, color=NEG, bold=True))
    f.append(text(677, 98, "Id > Idss", size=9.5, color=NEG))

    f.append(text(600, 315, "Передатна крива Id(Vgs) при Vds = const", size=11, bold=True))

    render(os.path.join(IMG, "iv-curves.svg"), w, h, *f)

# ════════════════════════════════════════════════════════════════════════════
# 4. depletion-load-inverter.svg: Інвертор зі збідненим навантаженням
# ════════════════════════════════════════════════════════════════════════════
def fig4_inverter():
    w, h = 820, 370
    f = []

    f.append(text(410, 24, "NMOS інвертор зі збідненим динамічним навантаженням", size=15, bold=True))

    # Ліва частина: Схема інвертора
    sx = 150
    f.append(line(sx, 55, sx, 85, color=INK, sw=1.8))
    f.append(text(sx, 48, "+Vdd (+5 В)", size=11.5, bold=True))

    # Збіднений транзистор навантаження Q_L
    ly = 115
    f.append(rect(sx - 18, ly - 22, 36, 44, fill="#f4f6f8", stroke=LINE, sw=1.4))
    f.append(text(sx, ly - 4, "QL", size=11.5, bold=True))
    f.append(text(sx, ly + 10, "збіднений", size=9.5, color=NEG))

    # Затвор Q_L замкнений на власний витік
    f.append(line(sx - 18, ly, sx - 35, ly, color=NEG, sw=1.6))
    f.append(line(sx - 35, ly, sx - 35, ly + 36, color=NEG, sw=1.6))
    f.append(line(sx - 35, ly + 36, sx, ly + 36, color=NEG, sw=1.6))
    f.append(circle(sx, ly + 36, 3, fill=NEG, stroke=NEG))
    f.append(text(sx - 42, ly + 18, "Vgs = 0 В", size=9.5, color=NEG, bold=True, anchor="end"))

    # Вихідний вузол Vout
    vy = ly + 36
    f.append(line(sx, ly + 22, sx, vy + 40, color=INK, sw=1.8))
    f.append(line(sx, vy, sx + 75, vy, color=INK, sw=1.8))
    f.append(circle(sx + 75, vy, 3.5, fill=INK, stroke=INK))
    f.append(text(sx + 85, vy + 4, "Vout", size=12, bold=True, anchor="start"))

    # Драйверний збагачений транзистор Q_D
    dy = vy + 65
    f.append(rect(sx - 18, dy - 22, 36, 44, fill="#f4f6f8", stroke=LINE, sw=1.4))
    f.append(text(sx, dy - 4, "QD", size=11.5, bold=True))
    f.append(text(sx, dy + 10, "збагачений", size=9.5, color=POS))

    # Вхід Vin
    f.append(line(sx - 18, dy, sx - 60, dy, color=INK, sw=1.8))
    f.append(circle(sx - 60, dy, 3.5, fill=INK, stroke=INK))
    f.append(text(sx - 68, dy + 4, "Vin", size=12, bold=True, anchor="end"))

    # Земля
    f.append(line(sx, dy + 22, sx, dy + 45, color=INK, sw=1.8))
    f.append(line(sx - 16, dy + 45, sx + 16, dy + 45, color=INK, sw=2.2))
    f.append(line(sx - 10, dy + 49, sx + 10, dy + 49, color=INK, sw=1.8))
    f.append(line(sx - 4, dy + 53, sx + 4, dy + 53, color=INK, sw=1.4))

    # Права частина: Порівняння передатної характеристики VTC
    gx, gy = 440, 280
    f.append(arrow(gx, gy, gx, 55, color=INK, sw=1.6))
    f.append(arrow(gx, gy, 760, gy, color=INK, sw=1.6))
    f.append(text(765, gy + 4, "Vin", size=12, bold=True, anchor="start"))
    f.append(text(gx - 6, 50, "Vout", size=12, bold=True, anchor="middle"))

    # Позначки Vdd на осях
    f.append(text(gx - 12, 75, "Vdd", size=11, bold=True, anchor="end"))
    f.append(line(gx - 4, 75, gx + 4, 75, color=INK, sw=1.4))

    f.append(text(680, gy + 18, "Vdd", size=11, bold=True, anchor="middle"))
    f.append(line(680, gy - 4, 680, gy + 4, color=INK, sw=1.4))

    # Крива 1: Збіднене навантаження (ідеальний крутий перехід, Voh = Vdd)
    f.append(polyline([(gx, 75), (510, 75), (530, 240), (680, 265)], color=NEG, sw=2.6))
    f.append(text(545, 95, "Збіднене QL: Voh = Vdd, високе підсилення", size=10.5, color=NEG, bold=True))

    # Крива 2: Збагачене навантаження (Voh = Vdd - Vth, втрата рівня)
    f.append(polyline([(gx, 125), (495, 125), (525, 245), (680, 268)], color=POS, sw=1.8, dash="5,3"))
    f.append(text(545, 135, "Збагачене QL: Voh = Vdd − Vth (втрата 1.5 В)", size=10, color=POS))
    f.append(line(gx - 4, 125, gx + 4, 125, color=POS, sw=1.4))
    f.append(text(gx - 10, 125, "Vdd−Vth", size=9.5, color=POS, anchor="end"))

    # Крива 3: Пасивне резистивне навантаження (пологий перехід, повільний заряд)
    f.append(polyline([(gx, 75), (470, 75), (570, 235), (680, 265)], color=MUTED, sw=1.6, dash="3,2"))
    f.append(text(545, 165, "Резистивне навантаження: пологий схил", size=10, color=MUTED))

    # Пояснення переваг унизу
    tb, _, _ = textbox(590, 330, "Збіднене навантаження працює як генератор струму: заряджає ємність виходу лінійно,\nзабезпечує повний логічний розмах Voh = Vdd і вдесятеро більше підсилення каскаду.", size=10.5, pad=6, fill="#f4f6f8", stroke=LINE)
    f.append(tb)

    render(os.path.join(IMG, "depletion-load-inverter.svg"), w, h, *f)

# ════════════════════════════════════════════════════════════════════════════
# 5. hv-startup-circuit.svg: Схема холодного високовольтного старту SMPS
# ════════════════════════════════════════════════════════════════════════════
def fig5_hv_startup():
    w, h = 820, 360
    f = []

    f.append(text(410, 24, "Високовольтний старт-ап блок живлення на збідненому MOSFET", size=15, bold=True))

    # Шина +400 В DC
    f.append(line(60, 60, 420, 60, color=POS, sw=2.2))
    f.append(text(70, 50, "Шина постійної напруги +400 В DC (після випрямляча)", size=11, color=POS, bold=True, anchor="start"))

    # Збіднений MOSFET Q_start
    qx, qy = 220, 125
    f.append(line(qx, 60, qx, qy - 25, color=POS, sw=1.8))
    f.append(rect(qx - 25, qy - 25, 50, 50, fill="#eff6ff", stroke=NEG, sw=1.6))
    f.append(text(qx, qy - 8, "Q_start", size=11.5, color=NEG, bold=True))
    f.append(text(qx, qy + 7, "HV Depletion", size=9.5, color=MUTED))
    f.append(text(qx, qy + 18, "600 В, Vth=−3 В", size=9.5, color=MUTED))

    # Затвор Q_start на землю
    f.append(line(qx - 25, qy, qx - 60, qy, color=INK, sw=1.5))
    f.append(line(qx - 60, qy, qx - 60, qy + 40, color=INK, sw=1.5))
    f.append(line(qx - 70, qy + 40, qx - 50, qy + 40, color=INK, sw=2.0))
    f.append(line(qx - 66, qy + 44, qx - 54, qy + 44, color=INK, sw=1.5))
    f.append(line(qx - 62, qy + 48, qx - 58, qy + 48, color=INK, sw=1.0))
    f.append(text(qx - 75, qy + 20, "Затвор = 0 В", size=10, bold=True, anchor="end"))

    # Витік Q_start іде до Vcc конденсатора
    cy = 225
    f.append(line(qx, qy + 25, qx, cy, color=INK, sw=1.8))
    f.append(circle(qx, cy, 3.5, fill=INK, stroke=INK))
    f.append(text(qx + 12, cy - 8, "Вузол Vcc", size=11, bold=True, anchor="start"))

    # Конденсатор C_vcc на землю
    f.append(line(qx, cy, qx - 50, cy, color=INK, sw=1.5))
    f.append(line(qx - 50, cy, qx - 50, cy + 25, color=INK, sw=1.5))
    # обкладки
    f.append(line(qx - 62, cy + 25, qx - 38, cy + 25, color=INK, sw=2.2))
    f.append(line(qx - 62, cy + 33, qx - 38, cy + 33, color=INK, sw=2.2))
    f.append(line(qx - 50, cy + 33, qx - 50, cy + 55, color=INK, sw=1.5))
    # земля
    f.append(line(qx - 58, cy + 55, qx - 42, cy + 55, color=INK, sw=1.8))
    f.append(text(qx - 70, cy + 30, "C_vcc\n47 мкФ", size=9.5, color=MUTED, anchor="end"))

    # ШІМ-контролер
    f.append(line(qx, cy, qx + 70, cy, color=INK, sw=1.8))
    f.append(rect(qx + 70, cy - 25, 95, 55, fill="#f4f6f8", stroke=LINE, sw=1.4))
    f.append(text(qx + 117, cy - 4, "ШІМ-контролер", size=10.5, bold=True))
    f.append(text(qx + 117, cy + 12, "Vcc_on = 15 В", size=9.5, color=FIELD))

    # Права частина: Порівняння фаз (Старт vs Робота)
    tb1, _, _ = textbox(610, 115, "Фаза 1: Холодний пуск (Vcc < 3 В)\n• V_витоку = Vcc ≈ 0 В, V_затвору = 0 В\n• Vgs = 0 В > Vth (−3 В) → Q_start ВІДКРИТИЙ\n• Швидкий заряд C_vcc постійним струмом Idss", size=10.5, pad=8, fill="#eff6ff", stroke=NEG)
    f.append(tb1)

    tb2, _, _ = textbox(610, 235, "Фаза 2: Робочий режим (Vcc = 15 В)\n• Додаткова обмотка живить ШІМ, Vcc = 15 В\n• V_витоку = 15 В → Vgs = 0 − 15 = −15 В ≪ Vth\n• Q_start ПОВНІСТЮ ЗАКРИТИЙ! Втрати холостого ходу = 0 Вт.", size=10.5, pad=8, fill="#fdf2f2", stroke=POS)
    f.append(tb2)

    # Порівняння зі старим резистором унизу
    f.append(text(410, 335, "Традиційний резистор 100 кОм давав 1.6 Вт постійного нагріву; збіднений MOSFET споживає < 1 мВт.", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "hv-startup-circuit.svg"), w, h, *f)

# ════════════════════════════════════════════════════════════════════════════
# 6. cascode-structure.svg: Силовий каскод GaN/SiC на збідненому приладі
# ════════════════════════════════════════════════════════════════════════════
def fig6_cascode():
    w, h = 820, 360
    f = []

    f.append(text(410, 24, "Силовий каскод: високовольтний GaN (Normally-ON) + кремнієвий MOSFET", size=15, bold=True))

    # Схема каскоду зліва
    cx = 170
    # Верхній вивід (Стік високовольтного ключа)
    f.append(line(cx, 55, cx, 85, color=POS, sw=2.0))
    f.append(text(cx, 46, "Стік (+650 В)", size=11.5, color=POS, bold=True))

    # Верхній транзистор: GaN HEMT (Normally-ON, Depletion, Vth = -5 В)
    gy = 115
    f.append(rect(cx - 25, gy - 25, 50, 50, fill="#fdf2f2", stroke=POS, sw=1.6))
    f.append(text(cx, gy - 7, "GaN HEMT", size=11, color=POS, bold=True))
    f.append(text(cx, gy + 7, "Normally-ON", size=9.5, color=MUTED))
    f.append(text(cx, gy + 18, "650 В, Vth=−5 В", size=9.5, color=MUTED))

    # Затвор GaN замкнений на землю (0 В)
    f.append(line(cx - 25, gy, cx - 75, gy, color=INK, sw=1.5))
    f.append(line(cx - 75, gy, cx - 75, gy + 145, color=INK, sw=1.5))
    f.append(circle(cx - 75, gy + 145, 3, fill=INK, stroke=INK))
    f.append(text(cx - 85, gy + 60, "Затвор GaN = 0 В\n(жорстко на землі)", size=9.5, color=INK, anchor="end"))

    # Проміжний вузол V_mid
    my = gy + 55
    f.append(line(cx, gy + 25, cx, my + 30, color=INK, sw=2.0))
    f.append(circle(cx, my, 3.5, fill=FIELD, stroke=FIELD))
    f.append(text(cx + 12, my + 4, "V_mid", size=11, color=FIELD, bold=True, anchor="start"))

    # Нижній транзистор: Si MOSFET (Normally-OFF, Enhancement, 30 В)
    sy = my + 55
    f.append(rect(cx - 25, sy - 25, 50, 50, fill="#eff6ff", stroke=NEG, sw=1.6))
    f.append(text(cx, sy - 7, "Si MOSFET", size=11, color=NEG, bold=True))
    f.append(text(cx, sy + 7, "Normally-OFF", size=9.5, color=MUTED))
    f.append(text(cx, sy + 18, "30 В, Vth=+3 В", size=9.5, color=MUTED))

    # Вхід керування (Затвор Si MOSFET)
    f.append(line(cx - 25, sy, cx - 60, sy, color=NEG, sw=1.8))
    f.append(circle(cx - 60, sy, 3.5, fill=NEG, stroke=NEG))
    f.append(text(cx - 68, sy + 4, "Драйвер\n0...10 В", size=10.5, color=NEG, bold=True, anchor="end"))

    # Витік Si MOSFET на землю
    f.append(line(cx, sy + 25, cx, sy + 50, color=INK, sw=1.8))
    f.append(line(cx - 16, sy + 50, cx + 16, sy + 50, color=INK, sw=2.2))
    f.append(line(cx - 10, sy + 54, cx + 10, sy + 54, color=INK, sw=1.8))
    f.append(line(cx - 4, sy + 58, cx + 4, sy + 58, color=INK, sw=1.4))
    f.append(text(cx, sy + 70, "Витік (Земля 0 В)", size=10, color=MUTED))

    # Права частина: Принцип роботи каскоду
    tb1, _, _ = textbox(590, 115, "Стан 1: Каскод ВИМКНЕНО (Драйвер = 0 В)\n• Нижній Si MOSFET закритий.\n• Струм витоку піднімає V_mid до +8 В.\n• Для GaN: Vgs = 0 − 8 = −8 В ≪ Vth (−5 В) → GaN ЗАКРИВАЄТЬСЯ!\n• GaN блокує високу напругу 650 В; на Si падає лише 8 В.", size=10, pad=8, fill="#fdf2f2", stroke=POS)
    f.append(tb1)

    tb2, _, _ = textbox(590, 235, "Стан 2: Каскод УВІМКНЕНО (Драйвер = +5 В)\n• Нижній Si MOSFET повністю відкритий → V_mid ≈ 0 В.\n• Для GaN: Vgs = 0 − 0 = 0 В > Vth (−5 В) → GaN ВІДКРИВАЄТЬСЯ!\n• Обидва ключі проводять струм з мінімальним опором Rds(on).", size=10, pad=8, fill="#eff6ff", stroke=NEG)
    f.append(tb2)

    f.append(text(410, 335, "Каскод перетворює небезпечний normally-on GaN на безпечний normally-off ключ зі стандартним драйвером 0...10 В.", size=11, color=FIELD, italic=True))

    render(os.path.join(IMG, "cascode-structure.svg"), w, h, *f)

if __name__ == "__main__":
    fig1_cross_section()
    fig2_modes()
    fig3_iv_curves()
    fig4_inverter()
    fig5_hv_startup()
    fig6_cascode()
    print("All 6 figures generated successfully.")
