# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *


def poly(pts, color, sw=2.5, dash=None):
    """Ламана/крива через <path> (у svgkit готового помічника нема)."""
    d = 'M %.2f %.2f ' % pts[0] + ' '.join('L %.2f %.2f' % p for p in pts[1:])
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, color, sw, da))

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

ORANGE = "#b8860b"


# ── Фігура 1: два світи напруги на одному кристалі ──────────────────────────
# Ліворуч — логіка нижнього боку (опора = земля). Праворуч — плаваючий домен
# (опора = вузол SW, що злітає до шини). Місток між ними — прилад зсуву рівня.
def fig_domain():
    W, H = 820, 440
    f = []

    # обрис кристала
    f.append(rect(36, 60, 748, 330, fill="#fbfbfd", stroke=MUTED, sw=1.5, rx=14))
    f.append(text(410, 82, "одна кремнієва підкладка", size=12, color=MUTED))

    # --- лівий блок: логіка нижнього боку ---
    f.append(fitbox(74, 130, 214, 96,
                    "Логіка нижнього боку\nопора — земля (COM)\n0 … +12 В",
                    size=13, fill="#eef4ff", stroke=NEG))
    # земляна шина під ним
    gy = 300
    f.append(line(74, gy, 288, gy, color=NEG, sw=3))
    f.append(line(181, 226, 181, gy, color=LINE, sw=1.4))
    f.append(text(181, gy + 22, "нерухома земля ≈ 0 В", size=11, color=NEG))

    # --- прилад зсуву рівня посередині ---
    f.append(fitbox(340, 138, 140, 80, "Прилад\nзсуву рівня",
                    size=14, bold=True, fill="#fff", stroke=INK))
    f.append(text(410, 236, "блокує всю шину Vбус", size=11, color=MUTED))

    # команда «лізе» знизу вгору
    f.append(arrow(288, 172, 338, 172, color=FIELD, sw=2.4))
    f.append(arrow(482, 172, 532, 172, color=FIELD, sw=2.4))
    f.append(text(410, 118, "команда «відкрий / закрий»", size=11, color=FIELD, bold=True))

    # --- правий блок: плаваючий домен ---
    f.append(fitbox(534, 130, 214, 96,
                    "Плаваючий домен\nопора — вузол SW\nживлення VB − VS",
                    size=13, fill="#fdeeec", stroke=POS))
    # дві шини праворуч: VB (верх) і VS=SW (низ), між ними бутстреп
    vbx = 700
    f.append(line(620, 250, 748, 250, color=POS, sw=3))
    f.append(text(684, 244, "VB = Vбус + 12", size=11, color=POS))
    f.append(line(620, 300, 748, 300, color=POS, sw=2.5))
    f.append(text(684, 320, "VS = SW: 0 → Vбус", size=11, color=POS))
    # бутстреп-конденсатор між шинами
    f.append(line(vbx, 250, vbx, 268, color=LINE, sw=1.4))
    f.append(line(vbx - 12, 268, vbx + 12, 268, color=LINE, sw=2))
    f.append(line(vbx - 12, 276, vbx + 12, 276, color=LINE, sw=2))
    f.append(line(vbx, 276, vbx, 300, color=LINE, sw=1.4))
    f.append(text(vbx + 40, 276, "Cbs", size=11, color=MUTED))
    # SW «злітає»
    f.append(arrow(600, 300, 600, 252, color=POS, sw=2))
    f.append(text(600, 340, "весь домен\nзлітає з SW", size=11, color=POS))

    f.append(fitbox(300, 356, 220, 30, "місток — лише прилад зсуву рівня",
                    size=12, bold=True, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, 'floating-domain.svg'), W, H, *f,
           title="Дві опори напруги на одному кристалі")


# ── Фігура 2: команда — двома імпульсами, стан тримає засувка ────────────────
def fig_pulse_latch():
    W, H = 820, 460
    f = []

    # шина VB угорі плаваючого домену
    vby = 96
    f.append(line(300, vby, 760, vby, color=POS, sw=2.5))
    f.append(text(530, vby - 10, "VB (живлення плаваючого домену)", size=12, color=POS, bold=True))

    # дві підтяжки-резистори від VB вниз
    def resistor(x, y0, y1, label):
        seg = line(x, y0, x, y0 + 10, color=LINE, sw=1.4)
        seg += rect(x - 8, y0 + 10, 16, 40, fill=FILL, stroke=LINE, sw=1.4, rx=3)
        seg += line(x, y0 + 50, x, y1, color=LINE, sw=1.4)
        seg += text(x + 26, y0 + 34, label, size=11, color=MUTED)
        return seg

    xset, xrst = 360, 500
    f.append(resistor(xset, vby, 210, "Rset"))
    f.append(resistor(xrst, vby, 210, "Rreset"))

    # два високовольтні ключі зсуву (SET / RESET) — прямокутники
    f.append(fitbox(xset - 55, 210, 110, 66, "HV-ключ\nSET", size=12, bold=True,
                    fill="#eafaf0", stroke=FIELD))
    f.append(fitbox(xrst - 55, 210, 110, 66, "HV-ключ\nRESET", size=12, bold=True,
                    fill="#fdeeec", stroke=POS))

    # вузли S та R (точки знімання), стрілки в засувку
    f.append(circle(xset, 205, 3.5, fill=INK, stroke=INK))
    f.append(circle(xrst, 205, 3.5, fill=INK, stroke=INK))
    f.append(text(xset - 20, 198, "S", size=13, bold=True, color=FIELD))
    f.append(text(xrst + 20, 198, "R", size=13, bold=True, color=POS))

    # засувка (SR-тригер) справа
    f.append(fitbox(620, 176, 150, 96, "SR-засувка\nтримає стан\nміж імпульсами",
                    size=12, fill="#fff", stroke=INK))
    f.append(arrow(xset, 176, 618, 200, color=FIELD, sw=2))
    f.append(arrow(xrst, 176, 618, 248, color=POS, sw=2))
    # вихід на верхній ключ
    f.append(arrow(770, 224, 806, 224, color=INK, sw=2))
    f.append(text(792, 210, "HO", size=12, bold=True))

    # --- низ: логіка нижнього боку гонить короткі імпульси в затвори ключів ---
    lgy = 330
    f.append(line(xset, 276, xset, lgy, color=LINE, sw=1.4))
    f.append(line(xrst, 276, xrst, lgy, color=LINE, sw=1.4))
    f.append(fitbox(300, lgy, 260, 54, "Логіка нижнього боку\n(коротка іскра в затвор ключа)",
                    size=12, fill="#eef4ff", stroke=NEG))

    # маленькі імпульси-символи
    def spark(x, y):
        return (line(x, y, x + 8, y, color=INK, sw=2) +
                line(x + 8, y, x + 8, y - 16, color=INK, sw=2) +
                line(x + 8, y - 16, x + 16, y - 16, color=INK, sw=2) +
                line(x + 16, y - 16, x + 16, y, color=INK, sw=2) +
                line(x + 16, y, x + 24, y, color=INK, sw=2))
    f.append(spark(xset - 12, 306))
    f.append(spark(xrst - 12, 306))

    # пояснення праворуч знизу
    f.append(fitbox(600, 320, 200, 96,
                    "SET-іскра → засувка в «1»\nRESET-іскра → в «0»\nміж іскрами ключі закриті —\nструму й втрат майже нема",
                    size=11, fill="#eafaf0", stroke=FIELD))

    render(os.path.join(IMG, 'pulse-latch.svg'), W, H, *f,
           title="Не рівень, а дві іскри: SET, RESET і засувка")


# ── Фігура 3: dV/dt підробляє команду ───────────────────────────────────────
def fig_dvdt():
    W, H = 820, 420
    f = []

    # фронт SW ліворуч
    x0, yb, yt = 70, 300, 150
    f.append(line(x0, yb, x0 + 60, yb, color=INK, sw=2.5))
    f.append(line(x0 + 60, yb, x0 + 110, yt, color=POS, sw=2.5))
    f.append(line(x0 + 110, yt, x0 + 170, yt, color=INK, sw=2.5))
    f.append(text(x0 + 24, 205, "dV/dt", size=13, color=POS, bold=True))
    f.append(text(x0 + 90, 345, "SW злітає  0 → Vбус", size=11, color=POS))

    # паразитні ємності від рухомого домену на обидві лінії зсуву
    def cap(x, y):
        s = line(x, y, x, y + 10, color=NEG, sw=1.4)
        s += line(x - 12, y + 10, x + 12, y + 10, color=NEG, sw=2)
        s += line(x - 12, y + 17, x + 12, y + 17, color=NEG, sw=2)
        s += line(x, y + 17, x, y + 27, color=NEG, sw=1.4)
        return s

    xs, xr = 400, 520
    f.append(cap(xs, 150))
    f.append(cap(xr, 150))
    f.append(text(460, 130, "паразитні ємності вузлів S і R", size=11, color=NEG))

    # струм-«злодій» в обидві лінії
    f.append(arrow(xs, 177, xs, 215, color=POS, sw=2.2))
    f.append(arrow(xr, 177, xr, 215, color=POS, sw=2.2))
    f.append(text(460, 205, "i = C · dV/dt", size=13, color=POS, bold=True))

    # вузли S, R → засувка
    f.append(circle(xs, 230, 3.5, fill=INK, stroke=INK))
    f.append(circle(xr, 230, 3.5, fill=INK, stroke=INK))
    f.append(text(xs - 18, 234, "S", size=12, bold=True, color=FIELD))
    f.append(text(xr + 18, 234, "R", size=12, bold=True, color=POS))
    f.append(fitbox(620, 200, 150, 70, "SR-засувка", size=13, fill="#fff", stroke=INK))
    f.append(arrow(xs, 236, 618, 224, color=MUTED, sw=1.8))
    f.append(arrow(xr, 236, 618, 246, color=MUTED, sw=1.8))

    # два висновки
    f.append(fitbox(60, 350, 340, 56,
                    "рух спільний на обох лініях →\nдиференційний приймач його відкидає",
                    size=11, fill="#eafaf0", stroke=FIELD))
    f.append(fitbox(430, 350, 350, 56,
                    "надто крутий чи несиметричний →\nфантомний імпульс → наскрізний струм",
                    size=11, fill="#fdeeec", stroke=POS))

    render(os.path.join(IMG, 'dvdt-false.svg'), W, H, *f,
           title="dV/dt підробляє команду в засувку")


# ── Вставка comp-halfbridge-hvic ────────────────────────────────────────────
# Фігура A: що всередині корпусу напівмостового драйвера (блок-схема класу)
def fig_hvic_block():
    W, H = 1080, 560
    f = []

    # обрис корпусу
    f.append(rect(40, 56, 900, 440, fill="#fbfbfd", stroke=MUTED, sw=1.5, rx=14))
    f.append(text(300, 80, "корпус: один кристал, два домени", size=12, color=MUTED))
    f.append(mtext(672, 74, "межа доменів:\nвисоковольтний перехід", size=11, color=MUTED))

    # --- вхідні виводи ---
    for y, nm in ((225, "HIN"), (300, "LIN"), (375, "SD")):
        f.append(text(30, y + 4, nm, size=13, bold=True, anchor="end"))
        f.append(arrow(36, y, 108, y, color=NEG, sw=2))

    # --- вхідна логіка (спільна на обидва боки) ---
    f.append(fitbox(110, 180, 175, 240,
                    "Вхідна логіка\nтригери Шмітта\nблокування\nUVLO по VCC",
                    size=13, fill="#eef4ff", stroke=NEG))

    # живлення нижнього боку знизу
    f.append(line(160, 420, 160, 496, color=LINE, sw=1.4))
    f.append(text(160, 516, "VCC", size=13, bold=True))
    f.append(line(235, 420, 235, 496, color=LINE, sw=1.4))
    f.append(text(235, 516, "COM", size=13, bold=True))

    # --- верхній шлях: формувач іскор → HV-ключі → межа ---
    f.append(arrow(285, 192, 318, 192, color=FIELD, sw=2))
    f.append(fitbox(320, 152, 160, 80, "Формувач іскор\nSET / RESET",
                    size=13, fill="#fff", stroke=INK))
    f.append(arrow(480, 192, 518, 192, color=FIELD, sw=2))
    f.append(fitbox(520, 152, 130, 80, "два HV-ключі\nзсуву рівня",
                    size=12, bold=True, fill="#eafaf0", stroke=FIELD))

    # межа доменів
    f.append(line(672, 100, 672, 360, color=MUTED, sw=2, dash="6 5"))
    f.append(arrow(650, 192, 698, 192, color=FIELD, sw=2.2))

    # --- плаваючий домен ---
    f.append(rect(686, 96, 240, 250, fill="none", stroke=POS, sw=1.6, rx=10))
    f.append(text(806, 118, "плаваючий домен (опора — VS)", size=11, color=POS))
    f.append(fitbox(700, 142, 212, 100,
                    "підтяжки Rset / Rreset\nдиференційний приймач\nSR-засувка\nUVLO по VBS",
                    size=12, fill="#fdeeec", stroke=POS))
    f.append(arrow(806, 242, 806, 266, color=INK, sw=2))
    f.append(fitbox(700, 270, 212, 56, "Драйвер HO", size=13, bold=True,
                    fill="#fff", stroke=INK))

    # виводи плаваючого боку
    f.append(line(926, 112, 968, 112, color=POS, sw=2))
    f.append(text(985, 116, "VB", size=13, bold=True, color=POS, anchor="start"))
    f.append(arrow(912, 298, 968, 298, color=INK, sw=2))
    f.append(text(985, 302, "HO", size=13, bold=True, anchor="start"))
    f.append(line(926, 330, 968, 330, color=POS, sw=2))
    f.append(text(985, 334, "VS", size=13, bold=True, color=POS, anchor="start"))

    # --- нижній шлях: просто драйвер ---
    f.append(arrow(285, 410, 318, 410, color=NEG, sw=2))
    f.append(fitbox(320, 380, 160, 60, "Драйвер LO", size=13, bold=True,
                    fill="#fff", stroke=INK))
    f.append(arrow(480, 410, 968, 410, color=INK, sw=2))
    f.append(text(985, 414, "LO", size=13, bold=True, anchor="start"))

    render(os.path.join(IMG, 'hvic-block.svg'), W, H, *f,
           title="Що напхано в корпус напівмостового драйвера")


# ── Фігура B: обв'язка — що навісити навколо ────────────────────────────────
def fig_hvic_hookup():
    W, H = 1100, 620
    f = []

    # шини
    f.append(line(60, 150, 640, 150, color=POS, sw=2.5))
    f.append(text(95, 138, "+12 В", size=12, color=POS, bold=True))
    f.append(line(60, 520, 1000, 520, color=NEG, sw=2.5))
    f.append(text(210, 542, "земля логіки й витоку нижнього ключа", size=11, color=NEG))
    f.append(line(700, 90, 1000, 90, color=POS, sw=2.5))
    f.append(text(940, 78, "+Vбус", size=12, color=POS, bold=True))

    # розв'язувальний конденсатор на VCC
    f.append(line(90, 150, 90, 320, color=LINE, sw=1.4))
    f.append(line(78, 320, 102, 320, color=LINE, sw=2))
    f.append(line(78, 330, 102, 330, color=LINE, sw=2))
    f.append(line(90, 330, 90, 520, color=LINE, sw=1.4))
    f.append(text(66, 328, "Cvcc", size=11, color=MUTED, anchor="end"))

    # контролер
    f.append(fitbox(150, 250, 140, 140, "Контролер\n(PWM)", size=13,
                    fill="#eef4ff", stroke=NEG))

    # мікросхема
    f.append(rect(360, 200, 230, 280, fill="#fbfbfd", stroke=INK, sw=2, rx=8))
    f.append(text(475, 228, "Напівмостовий драйвер", size=13, bold=True))
    for y, nm in ((270, "HIN"), (310, "LIN"), (350, "SD")):
        f.append(arrow(292, y, 358, y, color=NEG, sw=1.8))
        f.append(text(372, y + 4, nm, size=12, bold=True, anchor="start"))
    f.append(line(410, 200, 410, 150, color=LINE, sw=1.6))
    f.append(text(424, 172, "VCC", size=12, bold=True, anchor="start"))
    f.append(line(440, 480, 440, 520, color=LINE, sw=1.6))
    f.append(text(454, 502, "COM", size=12, bold=True, anchor="start"))

    f.append(text(578, 274, "VB", size=12, bold=True, color=POS, anchor="end"))
    f.append(line(590, 270, 680, 270, color=LINE, sw=1.6))
    f.append(text(578, 334, "HO", size=12, bold=True, anchor="end"))
    f.append(line(590, 330, 760, 330, color=LINE, sw=1.6))
    f.append(text(578, 394, "VS", size=12, bold=True, color=POS, anchor="end"))
    f.append(line(590, 390, 900, 390, color=POS, sw=2))
    f.append(text(700, 378, "вузол SW", size=11, color=POS))
    f.append(text(578, 444, "LO", size=12, bold=True, anchor="end"))
    f.append(line(590, 440, 760, 440, color=LINE, sw=1.6))

    # bootstrap-діод із шини +12 у VB
    f.append(line(640, 150, 640, 210, color=LINE, sw=1.6))
    f.append(line(631, 210, 649, 210, color=LINE, sw=1.8))
    f.append(line(631, 210, 640, 228, color=LINE, sw=1.8))
    f.append(line(649, 210, 640, 228, color=LINE, sw=1.8))
    f.append(line(630, 228, 650, 228, color=LINE, sw=2.2))
    f.append(line(640, 228, 640, 270, color=LINE, sw=1.6))
    f.append(text(668, 196, "Dbs", size=11, color=MUTED, anchor="start"))

    # bootstrap-конденсатор між VB і VS
    f.append(line(680, 270, 680, 300, color=LINE, sw=1.6))
    f.append(line(668, 300, 692, 300, color=LINE, sw=2))
    f.append(line(668, 308, 692, 308, color=LINE, sw=2))
    f.append(line(680, 308, 680, 390, color=LINE, sw=1.6))
    f.append(text(704, 300, "Cbs", size=11, color=MUTED, anchor="start"))

    # верхній ключ
    f.append(fitbox(840, 190, 120, 90, "верхній\nключ", size=12,
                    fill="#fdeeec", stroke=POS))
    f.append(line(900, 90, 900, 190, color=LINE, sw=1.8))
    f.append(line(900, 280, 900, 390, color=LINE, sw=1.8))
    f.append(line(760, 330, 760, 235, color=LINE, sw=1.6))
    f.append(line(760, 235, 770, 235, color=LINE, sw=1.6))
    f.append(rect(770, 227, 30, 16, fill=FILL, stroke=LINE, sw=1.4, rx=3))
    f.append(line(800, 235, 840, 235, color=LINE, sw=1.6))
    f.append(text(785, 216, "Rg", size=11, color=MUTED))

    # нижній ключ
    f.append(fitbox(840, 420, 120, 90, "нижній\nключ", size=12,
                    fill="#eef4ff", stroke=NEG))
    f.append(line(900, 390, 900, 420, color=LINE, sw=1.8))
    f.append(line(900, 510, 900, 520, color=LINE, sw=1.8))
    f.append(line(760, 440, 760, 465, color=LINE, sw=1.6))
    f.append(line(760, 465, 770, 465, color=LINE, sw=1.6))
    f.append(rect(770, 457, 30, 16, fill=FILL, stroke=LINE, sw=1.4, rx=3))
    f.append(line(800, 465, 840, 465, color=LINE, sw=1.6))
    f.append(text(785, 492, "Rg", size=11, color=MUTED))

    # вузли з'єднань
    for cx, cy in ((410, 150), (440, 520), (90, 520), (640, 270),
                   (680, 390), (900, 390), (900, 520), (900, 90)):
        f.append(circle(cx, cy, 3.5, fill=INK, stroke=INK))

    f.append(fitbox(150, 556, 400, 48,
                    "COM — до витоку нижнього ключа,\nа не «кудись у землю»",
                    size=11, fill="#eef4ff", stroke=NEG))
    f.append(fitbox(600, 556, 400, 48,
                    "Dbs — на всю шину Vбус і швидкий\nCbs заряджається, лише коли LO відкритий",
                    size=11, fill="#fdeeec", stroke=POS))

    render(os.path.join(IMG, 'hvic-hookup.svg'), W, H, *f,
           title="Обв'язка напівмостового драйвера")


# ── Фігура C: провал VS нижче COM → засувка паразитного тиристора ───────────
def fig_vs_undershoot():
    W, H = 980, 480
    f = []

    f.append(text(270, 88, "що бачить вивід VS", size=12, bold=True, color=MUTED))
    f.append(line(70, 130, 470, 130, color=MUTED, sw=1, dash="5 4"))
    f.append(text(60, 134, "Vбус", size=11, color=POS, anchor="end"))
    f.append(line(70, 250, 470, 250, color=MUTED, sw=1, dash="5 4"))
    f.append(text(60, 254, "COM = 0", size=11, color=MUTED, anchor="end"))

    # осцилограма VS: спад і дзвін нижче нуля
    pts = [(80, 130), (180, 130), (240, 250), (275, 330), (315, 215),
           (350, 275), (385, 238), (420, 256), (465, 250)]
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color=POS, sw=2.5))
    f.append(mtext(275, 360, "провал VS нижче COM\n−5 … −10 В за наносекунди",
                   size=11, color=NEG))
    f.append(fitbox(70, 400, 400, 46,
                    "паразитна індуктивність шин і корпусів\nдзвонить на вимкненні",
                    size=11, fill="#eef4ff", stroke=NEG))

    f.append(line(505, 100, 505, 450, color=MUTED, sw=1, dash="4 4"))

    # правий бік: паразитний перехід підкладки
    f.append(text(745, 88, "що з цього робить кремній", size=12, bold=True, color=MUTED))
    f.append(fitbox(600, 120, 290, 56, "плаваючий домен (опора VS)",
                    size=12, fill="#fdeeec", stroke=POS))
    f.append(fitbox(600, 280, 290, 56, "підкладка кристала (COM)",
                    size=12, fill="#eef4ff", stroke=NEG))

    # діод підкладки: анод унизу (COM), катод угорі (VS)
    f.append(line(745, 280, 745, 246, color=LINE, sw=1.8))
    f.append(line(736, 246, 754, 246, color=LINE, sw=1.8))
    f.append(line(736, 246, 745, 228, color=LINE, sw=1.8))
    f.append(line(754, 246, 745, 228, color=LINE, sw=1.8))
    f.append(line(734, 228, 756, 228, color=LINE, sw=2.2))
    f.append(line(745, 228, 745, 176, color=LINE, sw=1.8))
    f.append(mtext(790, 236, "перехід підкладки\nвідкривається",
                   size=11, color=NEG, anchor="start"))

    f.append(arrow(660, 276, 660, 182, color=POS, sw=2.2))
    f.append(mtext(600, 216, "струм\nу підкладку", size=11, color=POS, anchor="end"))

    f.append(fitbox(560, 380, 380, 66,
                    "паразитний тиристор замикається:\nживлення накоротко, HO завмирає\n"
                    "у поточному стані — або кристал гине",
                    size=11, fill="#fdeeec", stroke=POS))

    render(os.path.join(IMG, 'vs-undershoot.svg'), W, H, *f,
           title="Провал VS нижче COM — головний убивця класу")


# ── Вставка math-levelshift-power ───────────────────────────────────────────
# Фігура D: чи встигне приймач побачити спад.
# Δv(t) = I·R·(1 − e^(−t/τ)) проти порога Vth; три запаси k = I·R/Vth.
def fig_spark_detect():
    W, H = 880, 430
    f = []
    PX0, PX1 = 110.0, 660.0
    PY0, PY1 = 90.0, 330.0
    TMAX, VMAX = 12.0, 8.0
    TAU, VTH = 3.0, 2.0          # τ = R·Cp = 3 кОм · 1 пФ = 3 нс; поріг 2 В

    def xt(t):
        return PX0 + t / TMAX * (PX1 - PX0)

    def yv(v):
        return PY0 + v / VMAX * (PY1 - PY0)

    def curve(ir, color):
        pts = []
        t = 0.0
        while t <= TMAX + 1e-9:
            pts.append((xt(t), yv(min(VMAX, ir * (1.0 - math.exp(-t / TAU))))))
            t += 0.08
        return poly(pts, color, sw=2.6)

    # осі
    f.append(line(PX0, PY0, PX0, PY1, color=LINE, sw=1.5))
    f.append(line(PX0, PY1, PX1, PY1, color=LINE, sw=1.5))
    for v in (0, 2, 4, 6, 8):
        f.append(line(PX0 - 5, yv(v), PX0, yv(v), color=LINE, sw=1.2))
        if v != 2:
            f.append(text(PX0 - 12, yv(v) + 4, str(v), size=11, color=MUTED, anchor="end"))
    for t in (0, 3, 6, 9, 12):
        f.append(line(xt(t), PY1, xt(t), PY1 + 5, color=LINE, sw=1.2))
        f.append(text(xt(t), PY1 + 20, str(t), size=11, color=MUTED))
    f.append(text(PX0 + 6, PY0 - 14, "спад напруги під VB, В", size=11,
                  color=MUTED, anchor="start"))
    f.append(text((PX0 + PX1) / 2, PY1 + 92, "час від початку іскри, нс",
                  size=11, color=MUTED))

    # поріг приймача
    f.append(line(PX0, yv(VTH), PX1, yv(VTH), color=NEG, sw=1.8, dash="7,5"))
    f.append(text(PX0 - 12, yv(VTH) + 4, "Vth = 2 В", size=11, color=NEG,
                  anchor="end", bold=True))

    # три криві: здоровий запас, межовий, мертвий
    f.append(curve(6.0, FIELD))
    f.append(curve(2.4, ORANGE))
    f.append(curve(1.4, POS))

    # точки перетину порога
    for tc, col, lab in ((TAU * math.log(3.0 / 2.0), FIELD, "1.2 нс"),
                         (TAU * math.log(6.0), ORANGE, "5.4 нс")):
        f.append(line(xt(tc), yv(VTH), xt(tc), PY1, color=col, sw=1.4, dash="4,4"))
        f.append(circle(xt(tc), yv(VTH), 4, fill=col, stroke=col))
        f.append(text(xt(tc), PY1 + 44, lab, size=12, color=col, bold=True))

    # легенда
    lx = 672
    for i, (col, lines) in enumerate((
            (FIELD,  ["k = 3  (I·R = 6 В)", "поріг за 1.2 нс"]),
            (ORANGE, ["k = 1.2  (I·R = 2.4 В)", "поріг аж за 5.4 нс"]),
            (POS,    ["k = 0.7  (I·R = 1.4 В)", "порога не сягне ніколи"]))):
        y = 116 + i * 74
        f.append(line(lx, y, lx + 26, y, color=col, sw=3))
        f.append(mtext(lx + 33, y + 4, lines, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, 'spark-detect.svg'), W, H, *f,
           title="Чи встигне приймач побачити іскру")


# ── Фігура E: резистор скорочується, лишається стеля ────────────────────────
# Енергія однієї ПОМІЧЕНОЇ іскри: E = Vбус·Cp·Vth·f(k), f(k) = k·ln(k/(k−1)).
def fig_energy_overdrive():
    W, H = 900, 470
    f = []
    PX0, PX1 = 120.0, 760.0
    PY0, PY1 = 90.0, 330.0

    def xk(k):
        return PX0 + (k - 1.0) / 9.0 * (PX1 - PX0)

    def yf(v):
        return PY1 - (v - 0.5) / 3.0 * (PY1 - PY0)

    # осі
    f.append(line(PX0, PY0, PX0, PY1, color=LINE, sw=1.5))
    f.append(line(PX0, PY1, PX1, PY1, color=LINE, sw=1.5))
    for v in (1, 2, 3):
        f.append(line(PX0 - 5, yf(v), PX0, yf(v), color=LINE, sw=1.2))
        f.append(text(PX0 - 12, yf(v) + 4, str(v), size=11, color=MUTED, anchor="end"))
    for k in range(1, 11):
        f.append(line(xk(k), PY1, xk(k), PY1 + 5, color=LINE, sw=1.2))
        f.append(text(xk(k), PY1 + 20, str(k), size=11, color=MUTED))
    f.append(text(PX0 + 6, PY0 - 14, "f(k) — у скільки разів дорожче за стелю",
                  size=11, color=MUTED, anchor="start"))
    f.append(text((PX0 + PX1) / 2, PY1 + 112, "запас над порогом  k = I·R / Vth",
                  size=11, color=MUTED))

    # асимптота f = 1 — фізична стеля
    f.append(line(PX0, yf(1.0), PX1, yf(1.0), color=NEG, sw=1.8, dash="7,5"))
    f.append(text(660, yf(1.0) + 18, "фізична стеля  f → 1", size=11, color=NEG, bold=True))

    # крива f(k)
    pts = []
    k = 1.04
    while k <= 10.0 + 1e-9:
        v = k * math.log(k / (k - 1.0))
        if v <= 3.5:
            pts.append((xk(k), yf(v)))
        k += 0.01
    f.append(poly(pts, POS, sw=2.8))

    # стеля запасу: вузол не впаде нижче VS → k ≤ Vcc/Vth = 6
    f.append(line(xk(6), PY0, xk(6), 366, color=POS, sw=1.6, dash="6,5"))
    f.append(fitbox(352, 368, 250, 46, "стеля  k = Vcc/Vth = 6\nнижче VS вузол не впаде",
                    size=11, fill="#fdeeec", stroke=POS))

    # виноска про k → 1
    f.append(fitbox(150, 96, 250, 54, "k → 1: спад ледь дотягує\nдо порога — tвияв → ∞",
                    size=11, fill="#fdeeec", stroke=POS))
    f.append(arrow(250, 152, 140, 186, color=POS, sw=1.8))

    # табличка значень
    f.append(fitbox(560, 172, 310, 78,
                    "f(2) = 1.39     f(3) = 1.22\nf(4) = 1.15     f(6) = 1.09\n"
                    "f(k) = k·ln(k/(k−1))  →  1",
                    size=12, fill="#eef4ff", stroke=NEG))

    # робоча стрічка k = 2…4
    f.append(rect(xk(2), 368, xk(4) - xk(2), 14, fill="#eafaf0", stroke=FIELD, sw=1.4, rx=4))
    f.append(text((xk(2) + xk(4)) / 2, 400, "робоча зона k = 2…4", size=11,
                  color=FIELD, bold=True))

    render(os.path.join(IMG, 'energy-overdrive.svg'), W, H, *f,
           title="Ціна одного біта: резистор скорочується")


# ── Фігура F: вікно ширини іскри — перетин чотирьох умов ────────────────────
def fig_tp_window():
    W, H = 900, 400
    f = []
    X0, T0, DEC = 300.0, 0.3, 135.0     # x(0.3 нс) = 300, декада = 135 px

    def xt(t):
        return X0 + math.log10(t / T0) * DEC

    def bar(y, h, segs):
        s = ''
        for a, b, ok in segs:
            s += rect(xt(a), y, xt(b) - xt(a), h,
                      fill=("#eafaf0" if ok else "#fdeeec"),
                      stroke=(FIELD if ok else POS), sw=1.2, rx=4)
        return s

    def rlabel(y, h, lines, size=12, bold=False):
        ty = y + h / 2 - (len(lines) - 1) * size * 1.3 / 2 + size * 0.35
        return mtext(286, ty, lines, size=size, color=INK, anchor="end", bold=bold)

    rows = [
        (80, 32, [(0.3, 1.22, False), (1.22, 3000, True)],
         ["виявлення RC-спадом", "tp ≥ τ·ln(k/(k−1)) = 1.2 нс"], False),
        (128, 32, [(0.3, 43.2, False), (43.2, 3000, True)],
         ["фільтр проти dV/dt", "tp ≥ 4·tфронту ≈ 43 нс"], False),
        (176, 32, [(0.3, 231.5, True), (231.5, 3000, False)],
         ["тепловий бюджет 50 мВт", "tp ≤ P/(2·fsw·Vбус·I) = 231 нс"], False),
        (224, 32, [(0.3, 1000, True), (1000, 3000, False)],
         ["найкоротший імпульс ШІМ", "tp ≤ Dmin·Ts = 1 мкс"], False),
        (278, 40, [(0.3, 43.2, False), (43.2, 231.5, True), (231.5, 3000, False)],
         ["ВІКНО — перетин усіх чотирьох", "43 … 231 нс"], True),
    ]
    for y, h, segs, lab, bold in rows:
        f.append(bar(y, h, segs))
        f.append(rlabel(y, h, lab, bold=bold))

    # вісь часу
    f.append(line(X0, 340, xt(3000.0), 340, color=LINE, sw=1.5))
    for t, lab in ((1, "1 нс"), (10, "10 нс"), (100, "100 нс"), (1000, "1 мкс")):
        f.append(line(xt(t), 340, xt(t), 346, color=LINE, sw=1.2))
        f.append(text(xt(t), 362, lab, size=11, color=MUTED))

    # обраний робочий розмір
    f.append(line(xt(120), 70, xt(120), 344, color=MUTED, sw=1.5, dash="5,4"))
    f.append(text(xt(120), 60, "обрано tp = 120 нс", size=12, color=INK, bold=True))

    render(os.path.join(IMG, 'tp-window.svg'), W, H, *f,
           title="Вікно ширини іскри: між фільтром і нагрівом")


# ── Фігури вставки hist-hvic ────────────────────────────────────────────────
def area(pts, color, op=0.13):
    """Заливка площі під кривою (<path>, без обведення)."""
    d = 'M %.2f %.2f ' % pts[0] + ' '.join('L %.2f %.2f' % p for p in pts[1:]) + ' Z'
    return '<path d="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (d, color, op)


# ── hist-1: чому тонкий шар тримає більше (принцип RESURF) ───────────────────
# Головна думка: площа під кривою E(x) — це напруга. Пік упирається в Eкр
# однаково в обох випадках, але розмазане плато набирає в рази більшу площу.
def fig_resurf_field():
    W, H = 880, 560
    f = []

    # ═══ Ряд A: звичайний шар ═══
    f.append(text(56, 58, "Звичайний шар: усе поле збирається в один пік",
                  size=13, bold=True, anchor="start", color=INK))

    f.append(rect(56, 74, 340, 50, fill="#eef4ff", stroke=NEG, sw=1.4))
    f.append(rect(56, 124, 340, 44, fill="#eceff3", stroke=MUTED, sw=1.4))
    f.append(rect(58, 74, 30, 22, fill="#fdeeec", stroke=POS, sw=1.2, rx=2))
    f.append(text(73, 90, "p+", size=10, color=POS, bold=True))
    f.append(rect(364, 74, 30, 22, fill="#dce8ff", stroke=NEG, sw=1.2, rx=2))
    f.append(text(379, 90, "n+", size=10, color=NEG, bold=True))
    f.append(text(226, 110, "n-шар: товстий, легований сильніше", size=11, color=NEG))
    f.append(text(226, 152, "p-підкладка", size=11, color=MUTED))
    f.append(poly([(108, 74), (108, 124)], INK, 1.2, dash="4,3"))
    f.append(text(56, 190, "збіднення вузьке — поле не розтікається",
                  size=10, color=MUTED, anchor="start"))

    # графік поля
    f.append(line(470, 170, 856, 170, color=INK, sw=1.6))
    f.append(line(470, 60, 470, 170, color=INK, sw=1.6))
    f.append(text(462, 66, "E", size=12, anchor="end", bold=True))
    f.append(poly([(470, 72), (856, 72)], POS, 1.2, dash="6,4"))
    f.append(text(852, 66, "Eкр — лавинний пробій", size=11, color=POS, anchor="end"))

    curveA = [(472, 166), (478, 72), (492, 98), (510, 128), (530, 152),
              (546, 164), (856, 166)]
    f.append(area([(472, 170)] + curveA + [(856, 170)], POS, 0.13))
    f.append(poly(curveA, POS, 2.4))
    f.append(text(700, 120, "площа під кривою = напруга", size=12, color=MUTED))
    f.append(text(700, 144, "мала площа → пробій рано", size=12, color=POS, bold=True))
    f.append(text(660, 192, "відстань уздовж поверхні →", size=11, color=MUTED))

    # ═══ Ряд B: тонкий шар RESURF ═══
    f.append(text(56, 308, "Тонкий шар (RESURF): поле — плато",
                  size=13, bold=True, anchor="start", color=INK))
    f.append(text(668, 300, "…але площа в рази більша → 400 В",
                  size=12, bold=True, color=FIELD))

    f.append(rect(56, 324, 340, 22, fill="#eafaf0", stroke=FIELD, sw=1.4))
    f.append(rect(56, 346, 340, 72, fill="#eceff3", stroke=MUTED, sw=1.4))
    f.append(rect(58, 324, 28, 22, fill="#fdeeec", stroke=POS, sw=1.2, rx=2))
    f.append(rect(366, 324, 28, 22, fill="#dce8ff", stroke=NEG, sw=1.2, rx=2))
    f.append(text(226, 339, "n-шар тонкий:  Nd · t ≈ 10¹² см⁻²", size=11, color=FIELD))
    for x in (140, 226, 312):
        f.append(arrow(x, 388, x, 352, color=MUTED, sw=1.6))
    f.append(text(226, 408, "p-підкладка збіднює шар знизу — наскрізь",
                  size=11, color=MUTED))

    f.append(line(470, 420, 856, 420, color=INK, sw=1.6))
    f.append(line(470, 310, 470, 420, color=INK, sw=1.6))
    f.append(text(462, 316, "E", size=12, anchor="end", bold=True))
    f.append(poly([(470, 322), (856, 322)], POS, 1.2, dash="6,4"))
    f.append(text(852, 316, "Eкр — лавинний пробій", size=11, color=POS, anchor="end"))

    curveB = [(474, 418), (486, 322), (520, 358), (800, 358), (838, 322), (850, 418)]
    f.append(area(curveB, FIELD, 0.15))
    f.append(poly(curveB, FIELD, 2.4))
    f.append(text(640, 392, "плато нижче Eкр — і тягнеться всю довжину",
                  size=12, color=FIELD))
    f.append(text(660, 442, "відстань уздовж поверхні →", size=11, color=MUTED))

    f.append(fitbox(56, 470, 800, 60,
                    "Той самий кремній і та сама гранична напруженість — але поле, розмазане по довжині, набирає в рази більшу напругу.\n"
                    "Платня — точна доза заряду в шарі: забагато — не збідниться наскрізь; замало — зросте опір відкритого приладу.",
                    size=12, fill="#f7fbf8", stroke=FIELD))

    render(os.path.join(IMG, 'resurf-field.svg'), W, H, *f,
           title="Чому тонкий шар тримає більше: поле, розмазане по довжині")


# ── hist-2: дві нитки, що зійшлися наприкінці 1980-х ─────────────────────────
def fig_hvic_threads():
    W, H = 880, 520
    f = []

    # ── нитка I: прилад ──
    f.append(text(56, 62, "НИТКА I · прилад", size=13, bold=True,
                  anchor="start", color=NEG))
    f.append(fitbox(56, 78, 176, 76, "1977–78\nHEXFET\nЛідов і Герман\nIR",
                    size=12, fill="#eef4ff", stroke=NEG))
    f.append(fitbox(252, 78, 208, 76, "1980–83\nIGT / IGBT\nБаліґа · GE\nБекке й Вітлі · RCA",
                    size=12, fill="#eef4ff", stroke=NEG))
    f.append(fitbox(480, 78, 168, 76, "затвор — ємність:\nкерувати =\nдати заряд,\nа не струм",
                    size=12, fill="#fff", stroke=INK))
    f.append(arrow(234, 116, 250, 116, color=NEG, sw=2))
    f.append(arrow(462, 116, 478, 116, color=NEG, sw=2))

    # ── нитка II: кремній ──
    f.append(text(56, 290, "НИТКА II · кремній", size=13, bold=True,
                  anchor="start", color=FIELD))
    f.append(fitbox(56, 306, 176, 76, "1979\nRESURF\nАппелс і Ваес\nPhilips",
                    size=12, fill="#eafaf0", stroke=FIELD))
    f.append(fitbox(252, 306, 208, 76, "1980\nбічний 400-В DMOS\nЧолак, Сінґер, Ступп\nRCA",
                    size=12, fill="#eafaf0", stroke=FIELD))
    f.append(fitbox(480, 306, 168, 76, "600 В поруч\nіз логікою\nна спільній\nпідкладці",
                    size=12, fill="#fff", stroke=INK))
    f.append(arrow(234, 344, 250, 344, color=FIELD, sw=2))
    f.append(arrow(462, 344, 478, 344, color=FIELD, sw=2))

    # ── злиття ──
    f.append(fitbox(690, 168, 168, 120,
                    "1988\nперші доповіді\n1989\nперший монолітний\nHVIC-драйвер · IR\n(і патент Philips)\n~1990 · IR2110",
                    size=11, bold=True, fill="#fdeeec", stroke=POS))
    f.append(arrow(652, 120, 686, 190, color=INK, sw=2))
    f.append(arrow(652, 340, 686, 266, color=INK, sw=2))

    # ── бічна гілка: інша школа ──
    f.append(poly([(356, 384), (356, 424)], MUTED, 1.4, dash="5,4"))
    f.append(fitbox(56, 426, 420, 64,
                    "1985 · BCD, 60 В — Мурарі й команда · SGS\nінша школа: на кристал — усе, разом із ключами, але напруга низька",
                    size=11, fill="#f7f7fa", stroke=MUTED))
    f.append(fitbox(506, 426, 350, 64,
                    "стеля 600 В — не маркетинг: стільки дає\nізоляція p-n-переходом на спільній підкладці",
                    size=11, fill="#fdeeec", stroke=POS))

    render(os.path.join(IMG, 'hvic-threads.svg'), W, H, *f,
           title="Дві нитки, що зійшлися наприкінці 1980-х")


if __name__ == '__main__':
    fig_domain()
    fig_pulse_latch()
    fig_dvdt()
    fig_hvic_block()
    fig_hvic_hookup()
    fig_vs_undershoot()
    fig_spark_detect()
    fig_energy_overdrive()
    fig_tp_window()
    fig_resurf_field()
    fig_hvic_threads()
    print("figures written to", IMG)
