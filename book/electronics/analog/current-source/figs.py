# -*- coding: utf-8 -*-
"""Фігури до теми «Джерело струму» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  duality.svg     — джерело напруги ↔ джерело струму як двійники: що тримають, що віддають вільно
  iv-curve.svg    — вольт-амперна характеристика: ідеальне (горизонталь) vs реальне (ледь похиле)
  compliance.svg  — вікно піддатливості: струм сталий лише в діапазоні напруг, поза ним падає
  transistor.svg  — найпростіше реальне джерело: транзистор в активному режимі, поличка струму
  norton-divider.svg — (вставка math) еквівалент Нортона: I₀ ∥ r_out живить R_L, струм ділиться
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def duality():
    """Два двополюсники-двійники: напругу тримає один, струм — інший."""
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 28, "Два двійники: що тримають жорстко, що віддають вільно", size=17, bold=True))

    # ── Ліва панель: джерело напруги ──
    cx = 185
    p.append(fitbox(40, 56, 290, 24, "ДЖЕРЕЛО НАПРУГИ", size=14, bold=True,
                    fill="#eaf0fd", stroke=NEG, color=NEG))
    # символ: дві риски (батарея)
    bx, by = cx, 150
    p.append(line(bx, by - 34, bx, by - 6, color=INK, sw=2))
    p.append(line(bx - 22, by - 6, bx + 22, by - 6, color=INK, sw=4))   # довга (+)
    p.append(line(bx - 12, by + 6, bx + 12, by + 6, color=INK, sw=2))   # коротка (−)
    p.append(line(bx, by + 6, bx, by + 34, color=INK, sw=2))
    p.append(plus(bx + 40, by - 18, r=9))
    p.append(minus(bx + 40, by + 18, r=9))
    p.append(text(cx, 210, "тримає U сталою", size=14, bold=True, color=NEG))
    p.append(text(cx, 232, "струм бере, скільки", size=13, color=MUTED))
    p.append(text(cx, 250, "візьме навантаження", size=13, color=MUTED))
    p.append(text(cx, 286, "коротко замкнути —", size=12, color=POS))
    p.append(text(cx, 303, "струм нескінченний", size=12, color=POS))

    # вертикальна межа
    p.append(line(360, 56, 360, 320, color="#d0d0d0", sw=1.5, dash="4,4"))

    # ── Права панель: джерело струму ──
    cx = 535
    p.append(fitbox(390, 56, 290, 24, "ДЖЕРЕЛО СТРУМУ", size=14, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))
    # символ: коло зі стрілкою вгору
    sx, sy = cx, 150
    p.append(circle(sx, sy, 30, fill=BG, stroke=INK, sw=2))
    p.append(arrow(sx, sy + 18, sx, sy - 18, color=INK, sw=2.4))
    p.append(text(cx, 210, "тримає I сталим", size=14, bold=True, color=POS))
    p.append(text(cx, 232, "напругу бере, скільки", size=13, color=MUTED))
    p.append(text(cx, 250, "треба, щоб продавити I", size=13, color=MUTED))
    p.append(text(cx, 286, "розірвати коло —", size=12, color=POS))
    p.append(text(cx, 303, "напруга нескінченна", size=12, color=POS))

    render(os.path.join(OUT, 'duality.svg'), W, H, *p)


def _axes(p, ox, oy, w, h, xlab, ylab):
    """Осі зі стрілками; ox,oy — лівий нижній кут (початок)."""
    p.append(arrow(ox, oy, ox + w, oy, color=INK, sw=1.8))      # X
    p.append(arrow(ox, oy, ox, oy - h, color=INK, sw=1.8))      # Y
    p.append(text(ox + w - 4, oy + 22, xlab, size=13, color=MUTED, anchor="end"))
    p.append(text(ox + 8, oy - h + 4, ylab, size=13, color=MUTED, anchor="start"))


def iv_curve():
    """Вольт-амперна: ідеал — горизонталь; реал — ледь росте і має коліно."""
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 28, "Джерело струму на вольт-амперній площині", size=17, bold=True))

    ox, oy, w, h = 90, 320, 560, 250
    _axes(p, ox, oy, w, h, "напруга на джерелі  U", "струм  I")

    Iy = oy - 150          # рівень заданого струму
    knee = ox + 90         # коліно піддатливості

    # ідеальне джерело — строго горизонталь на всю ширину
    p.append(line(ox, Iy, ox + w - 20, Iy, color=NEG, sw=2.6, dash="7,5"))
    p.append(text(ox + w - 24, Iy - 12, "ідеальне: I = const", size=13, color=NEG, anchor="end", bold=True))

    # реальне: до коліна круто росте з нуля (мала напруга — провал), далі майже стала з легким нахилом
    seg = []
    seg.append((ox, oy))
    seg.append((knee - 40, oy - 90))
    seg.append((knee, Iy + 6))           # коліно
    # пологий нахил угору
    x_end = ox + w - 24
    y_end = Iy - 36
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        seg[0][0], seg[0][1], seg[1][0], seg[1][1], seg[2][0], seg[2][1], x_end, y_end)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts, POS))
    p.append(text(x_end, y_end - 14, "реальне: ледь похиле", size=13, color=POS, anchor="end", bold=True))

    # коліно — лінія піддатливості
    p.append(line(knee, oy, knee, Iy + 6, color=MUTED, sw=1.2, dash="3,3"))
    p.append(text(knee, oy + 22, "U_min", size=12, color=MUTED))

    # позначка рівня струму
    p.append(line(ox, Iy, ox + 6, Iy, color=INK, sw=1.5))
    p.append(text(ox - 8, Iy + 4, "I₀", size=13, color=INK, anchor="end", bold=True))

    # підписи зон
    p.append(fitbox(ox + 8, oy - 64, 78, 40, "провал:\nзамало U", size=11,
                    fill="#fdecea", stroke=POS, color=POS))
    p.append(fitbox(knee + 130, Iy + 30, 150, 26, "робоча поличка струму", size=12,
                    fill="#eafaf1", stroke=FIELD, color="#1e7e44"))

    render(os.path.join(OUT, 'iv-curve.svg'), W, H, *p)


def compliance():
    """Вікно піддатливості: струм тримається лише доки джерелу вистачає напруги."""
    W, H = 720, 320
    p = []
    p.append(text(W / 2, 28, "Піддатливість: межа, доки джерело ще тримає струм", size=17, bold=True))

    # шкала напруги навантаження зліва направо
    ox, oy, w = 70, 200, 580
    p.append(arrow(ox, oy, ox + w, oy, color=INK, sw=1.8))
    p.append(text(ox + w - 4, oy + 26, "напруга, що дісталась навантаженню", size=12, color=MUTED, anchor="end"))

    lo = ox + 70           # нижня межа (мінімальний запас джерела)
    hi = ox + 470          # верхня межа (живлення)

    # зелене вікно
    p.append(rect(lo, oy - 90, hi - lo, 78, fill="#eafaf1", stroke=FIELD, sw=1.5))
    p.append(text((lo + hi) / 2, oy - 46, "тут струм стабільний: I = I₀", size=14, bold=True, color="#1e7e44"))

    # межі
    p.append(line(lo, oy - 100, lo, oy + 8, color=POS, sw=1.6, dash="4,3"))
    p.append(line(hi, oy - 100, hi, oy + 8, color=POS, sw=1.6, dash="4,3"))
    p.append(text(lo, oy - 110, "запас джерела", size=12, color=POS))
    p.append(text(hi, oy - 110, "уся напруга живлення", size=12, color=POS, anchor="middle"))

    # ліворуч від вікна — джерело «здавило», струм падає
    p.append(fitbox(ox + 2, oy - 78, 60, 54, "джерело\nздавлене:\nI падає", size=10,
                    fill="#fdecea", stroke=POS, color=POS))
    # праворуч — навантаженню віддали все, джерелу не лишилось
    p.append(fitbox(hi + 14, oy - 78, 86, 54, "джерелу не\nлишилось\nнапруги", size=10,
                    fill="#fdecea", stroke=POS, color=POS))

    p.append(text(W / 2, 290, "Ширину вікна звуть напругою піддатливості (compliance).",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'compliance.svg'), W, H, *p)


def transistor():
    """Найпростіше реальне джерело: транзистор в активі — вихідна характеристика."""
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 28, "Звідки береться стала полиця: транзистор в активному режимі", size=17, bold=True))

    ox, oy, w, h = 100, 300, 540, 230
    _axes(p, ox, oy, w, h, "напруга колектор-емітер  U_CE", "струм колектора  I_C")

    knee = ox + 80
    levels = [(oy - 70, "малий струм бази"),
              (oy - 130, "більший струм бази"),
              (oy - 190, "ще більший")]

    for (Iy, lab) in levels:
        # крута ділянка від 0 до коліна
        kx = knee
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (ox, oy, kx - 30, Iy + (oy - Iy) * 0.30, kx, Iy + 4)
        # пологий нахил угору після коліна (ефект Ерлі)
        x_end = ox + w - 24
        slope = (oy - Iy) * 0.10
        p.append('<polyline points="%s %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (pts, x_end, Iy - slope, POS))
        p.append(text(x_end, Iy - slope - 10, lab, size=11, color=MUTED, anchor="end"))

    # зона коліна
    p.append(line(knee, oy, knee, oy - 200, color=MUTED, sw=1.0, dash="3,3"))
    p.append(text(knee, oy + 22, "U_min", size=12, color=MUTED))
    p.append(fitbox(ox + 6, oy - 56, 64, 34, "насичення:\nне джерело", size=10,
                    fill="#fdecea", stroke=POS, color=POS))
    p.append(fitbox(knee + 150, oy - 224, 200, 26, "активний режим = майже сталий струм", size=12,
                    fill="#eafaf1", stroke=FIELD, color="#1e7e44"))

    p.append(text(W / 2, 344, "Кожна крива — своя «поличка»; джерело працює праворуч від коліна U_min.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'transistor.svg'), W, H, *p)


def norton_divider():
    """Еквівалент Нортона: ідеальне I₀ паралельно з r_out живить R_L; струм ділиться надвоє."""
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 28, "Реальне джерело струму як Нортон: куди йде струм", size=17, bold=True))

    # ── Рамка реального джерела (ліворуч): ідеальне I0 || r_out ──
    bx, by, bw, bh = 60, 70, 230, 250
    p.append(rect(bx, by, bw, bh, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=10))
    p.append(text(bx + bw / 2, by - 12, "реальне джерело струму", size=13, color=MUTED, bold=True))

    # символ ідеального джерела струму — коло зі стрілкою (ліва вітка)
    sx = bx + 70
    s_top, s_bot = by + 70, by + 200
    p.append(circle(sx, (s_top + s_bot) / 2, 28, fill=BG, stroke=INK, sw=2))
    p.append(arrow(sx, (s_top + s_bot) / 2 + 16, sx, (s_top + s_bot) / 2 - 16, color=INK, sw=2.4))
    p.append(text(sx - 42, (s_top + s_bot) / 2 + 4, "I₀", size=15, color=INK, bold=True, anchor="middle"))
    # дроти джерела до верхньої й нижньої шин
    top_y, bot_y = by + 30, by + bh - 30
    p.append(line(sx, top_y, sx, s_top, color=INK, sw=2))
    p.append(line(sx, s_bot, sx, bot_y, color=INK, sw=2))

    # r_out — паралельний резистор (права вітка всередині рамки)
    rx_ = bx + 165
    p.append(_resistor_v(rx_, s_top, s_bot, sw=2))
    p.append(text(rx_ + 40, (s_top + s_bot) / 2 - 6, "r_out", size=14, color=POS, bold=True, anchor="middle"))
    p.append(text(rx_ + 40, (s_top + s_bot) / 2 + 14, "(велике)", size=11, color=MUTED, anchor="middle"))
    p.append(line(rx_, top_y, rx_, s_top, color=INK, sw=2))
    p.append(line(rx_, s_bot, rx_, bot_y, color=INK, sw=2))

    # верхня й нижня шини всередині рамки
    p.append(line(sx, top_y, rx_, top_y, color=INK, sw=2))
    p.append(line(sx, bot_y, rx_, bot_y, color=INK, sw=2))

    # ── Зовнішні дроти до навантаження R_L (праворуч) ──
    node_x = bx + bw + 60          # вузол виходу
    p.append(line(rx_, top_y, node_x + 120, top_y, color=INK, sw=2))   # верхня шина назовні
    p.append(line(rx_, bot_y, node_x + 120, bot_y, color=INK, sw=2))   # нижня (зворотна)

    # навантаження R_L — резистор у зовнішній вітці
    lx = node_x + 120
    p.append(_resistor_v(lx, top_y, bot_y, sw=2))
    p.append(text(lx + 42, (top_y + bot_y) / 2 - 6, "R_L", size=14, color="#1e7e44", bold=True, anchor="middle"))
    p.append(text(lx + 42, (top_y + bot_y) / 2 + 14, "(мале)", size=11, color=MUTED, anchor="middle"))

    # спільна напруга U між шинами
    p.append(line(node_x, top_y + 8, node_x, bot_y - 8, color=NEG, sw=1.2, dash="4,3"))
    p.append(text(node_x + 14, (top_y + bot_y) / 2 + 4, "U", size=14, color=NEG, bold=True, anchor="start"))

    # стрілки розгалуження струму у верхній шині
    p.append(arrow(rx_ + 18, top_y, rx_ + 70, top_y, color=FIELD, sw=2.2))  # до навантаження
    p.append(text(rx_ + 44, top_y - 10, "I_L", size=12, color="#1e7e44", bold=True))
    # обхідний струм униз через r_out (стрілка трохи лівіше дроту, щоб не зливалася з ним)
    p.append(arrow(rx_ - 16, s_top + 4, rx_ - 16, s_top + 40, color=POS, sw=2.2))
    p.append(text(rx_ - 24, s_top + 26, "I_Rout", size=12, color=POS, bold=True, anchor="end"))

    # формула дільника знизу
    p.append(fitbox(150, 330, 420, 34,
                    "I_L = I₀ · r_out / (r_out + R_L)   →   r_out ≫ R_L  ⇒  I_L ≈ I₀",
                    size=13, fill="#eafaf1", stroke=FIELD, color="#1e7e44", bold=True))

    render(os.path.join(OUT, 'norton-divider.svg'), W, H, *p)


def _resistor_v(x, y_top, y_bot, sw=2):
    """Вертикальний резистор-прямокутник між y_top і y_bot; повертає SVG-рядок."""
    rw, rh = 26, 64
    cy = (y_top + y_bot) / 2
    out = []
    out.append(line(x, y_top, x, cy - rh / 2, color=INK, sw=sw))
    out.append(rect(x - rw / 2, cy - rh / 2, rw, rh, fill="#fff", stroke=INK, sw=sw, rx=3))
    out.append(line(x, cy + rh / 2, x, y_bot, color=INK, sw=sw))
    return "".join(out)


def _qcurve(p, ox, oy, idss_y, knee_x, x_end, slope_y, color, sw=2.6):
    """Крива квадратичного закону у виглядді джерела: круто від 0 до коліна, далі ледь росте."""
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        ox, oy, knee_x - 34, oy - (oy - idss_y) * 0.72, knee_x, idss_y + 4, x_end, slope_y)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (pts, color, sw))


def jfet_cld():
    """Двовивідне джерело на JFET: схема із закороченим затвором + вихідна характеристика."""
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 26, "Двовивідне джерело струму: закорочений затвор JFET", size=17, bold=True))

    # ── Ліва панель: схема двополюсника ──
    p.append(line(345, 56, 345, 332, color="#d0d0d0", sw=1.5, dash="4,4"))   # межа

    cx = 150
    top_y, bot_y = 80, 300
    # верхній вивід (стік = анод)
    p.append(line(cx, top_y, cx, 130, color=INK, sw=2))
    p.append(text(cx, top_y - 8, "стік (анод)", size=12, color=MUTED))
    # тіло JFET: вертикальний канал (товста риска) + затвор-стрілка збоку
    chan_top, chan_bot = 130, 250
    p.append(line(cx, chan_top, cx, chan_bot, color=INK, sw=4))             # канал
    gx = cx - 56                                                            # лінія затвора
    gy = (chan_top + chan_bot) / 2
    p.append(line(gx, gy, cx - 2, gy, color=INK, sw=2))                     # затвор → канал (стрілка n-кан.)
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        cx - 2, gy, cx - 14, gy - 6, cx - 14, gy + 6, INK))                 # вістря до каналу
    p.append(text(gx - 6, gy + 4, "затвор", size=12, color=MUTED, anchor="end"))
    # нижній вивід (витік = катод)
    p.append(line(cx, chan_bot, cx, bot_y, color=INK, sw=2))
    p.append(text(cx, bot_y + 18, "витік (катод)", size=12, color=MUTED))
    # ЗАКОРОЧЕННЯ затвор–витік: провід від затвора вниз і до витоку
    short_y = bot_y - 18
    p.append(line(gx, gy, gx, short_y, color=POS, sw=2.2))
    p.append(line(gx, short_y, cx, short_y, color=POS, sw=2.2))
    p.append(circle(cx, short_y, 3.2, fill=POS, stroke=POS, sw=1))
    p.append(fitbox(cx - 96, gy - 56, 92, 30, "затвор\nзакорочено\nна витік", size=10,
                    fill="#fdecea", stroke=POS, color=POS))
    # струм крізь двополюсник
    p.append(arrow(cx + 34, 150, cx + 34, 110, color=FIELD, sw=2.2))
    p.append(text(cx + 40, 134, "I = I_DSS", size=12, color="#1e7e44", bold=True, anchor="start"))

    # ── Права панель: вихідна характеристика з полицею I_DSS ──
    ox, oy, w, h = 410, 300, 270, 210
    _axes(p, ox, oy, w, h, "напруга на джерелі  U_DS", "струм  I_D")
    Iy = oy - 150
    knee = ox + 56
    _qcurve(p, ox, oy, Iy, knee, ox + w - 20, Iy - 26, POS)
    # рівень I_DSS
    p.append(line(ox, Iy, ox + w - 20, Iy, color=NEG, sw=1.4, dash="6,4"))
    p.append(line(ox, Iy, ox + 6, Iy, color=INK, sw=1.5))
    p.append(text(ox - 8, Iy + 4, "I_DSS", size=12, color=INK, anchor="end", bold=True))
    # коліно V_K
    p.append(line(knee, oy, knee, Iy + 4, color=MUTED, sw=1.1, dash="3,3"))
    p.append(text(knee, oy + 20, "V_K", size=12, color=MUTED))
    p.append(fitbox(knee + 56, Iy + 26, 150, 24, "полиця: I = I_DSS", size=12,
                    fill="#eafaf1", stroke=FIELD, color="#1e7e44"))

    render(os.path.join(OUT, 'jfet-cld.svg'), W, H, *p)


def self_bias():
    """Самозміщення: робоча точка — перетин квадратичної кривої JFET і прямої навантаження R_S."""
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 26, "Резистор витоку опускає струм: робоча точка self-bias", size=17, bold=True))

    # ── Ліва панель: схема із R_S ──
    p.append(line(330, 54, 330, 350, color="#d0d0d0", sw=1.5, dash="4,4"))
    cx = 150
    top_y = 78
    p.append(line(cx, top_y, cx, 120, color=INK, sw=2))
    p.append(text(cx, top_y - 8, "стік", size=12, color=MUTED))
    chan_top, chan_bot = 120, 220
    p.append(line(cx, chan_top, cx, chan_bot, color=INK, sw=4))
    gx = cx - 54
    gy = (chan_top + chan_bot) / 2
    p.append(line(gx, gy, cx - 2, gy, color=INK, sw=2))
    p.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
        cx - 2, gy, cx - 14, gy - 6, cx - 14, gy + 6, INK))
    p.append(text(gx - 6, gy + 4, "затвор", size=12, color=MUTED, anchor="end"))
    # витік → резистор R_S → нижня шина
    p.append(line(cx, chan_bot, cx, 250, color=INK, sw=2))
    p.append(_resistor_v(cx, 250, 320, sw=2))
    p.append(text(cx + 38, 285, "R_S", size=14, color=POS, bold=True, anchor="middle"))
    bot_y = 320
    p.append(line(cx, bot_y, cx, bot_y + 10, color=INK, sw=2))
    # затвор притягнутий до НИЗУ (землі), не до витоку
    p.append(line(gx, gy, gx, bot_y, color=INK, sw=2))
    p.append(line(gx, bot_y, cx, bot_y, color=INK, sw=2))
    p.append(circle(cx, bot_y, 3.2, fill=INK, stroke=INK, sw=1))
    # U_GS між затвором і витоком
    p.append(text(cx + 30, gy + 4, "U_GS < 0", size=12, color=NEG, bold=True, anchor="start"))
    p.append(fitbox(gx - 78, gy + 40, 132, 44, "затвор — на землю,\nвитік піднятий I·R_S\n→ U_GS = −I·R_S",
                    size=10, fill="#eaf0fd", stroke=NEG, color=NEG))

    # ── Права панель: перетин кривої й прямої навантаження ──
    # тут осі НЕЗВИЧНІ: по X — від'ємна U_GS (управо росте |U_GS|), по Y — струм
    ox, oy, w, h = 400, 320, 280, 250
    p.append(arrow(ox, oy, ox + w, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - h, color=INK, sw=1.8))
    p.append(text(ox + w - 4, oy + 22, "−U_GS  (глибше зміщення →)", size=12, color=MUTED, anchor="end"))
    p.append(text(ox + 8, oy - h + 4, "струм  I_D", size=12, color=MUTED, anchor="start"))

    Idss_y = oy - 200          # рівень I_DSS (при U_GS=0, тобто при x=ox)
    Up_x = ox + w - 30         # відсічка U_P (струм=0)

    # квадратична крива I = I_DSS·(1 − U_GS/U_P)²: від (ox, I_DSS) спадає до (Up_x, 0)
    import math as _m
    qpts = []
    N = 28
    for i in range(N + 1):
        t = i / N                       # 0..1 уздовж осі −U_GS до відсічки
        x = ox + t * (Up_x - ox)
        y = oy - (oy - Idss_y) * (1.0 - t) ** 2   # (1 − t)² від I_DSS до 0
        qpts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(qpts), POS))
    p.append(text(ox + 70, Idss_y - 8, "крива JFET (квадрат)", size=12, color=POS, bold=True, anchor="start"))
    p.append(line(ox, Idss_y, ox + 6, Idss_y, color=INK, sw=1.5))
    p.append(text(ox - 8, Idss_y + 4, "I_DSS", size=12, color=INK, anchor="end", bold=True))
    p.append(text(Up_x, oy + 20, "U_P", size=12, color=MUTED))

    # пряма навантаження резистора: I = −U_GS / R_S → у наших осях пряма з початку вгору-вправо
    # підберемо так, щоб перетнути криву десь на чверті висоти (демонстрація опускання струму)
    op_t = 0.5                                  # параметр перетину вздовж осі
    op_x = ox + op_t * (Up_x - ox)
    op_y = oy - (oy - Idss_y) * (1.0 - op_t) ** 2
    p.append(line(ox, oy, op_x + (op_x - ox) * 0.25, op_y - (oy - op_y) * 0.25,
                  color=NEG, sw=2.4))
    p.append(text(op_x + 40, oy - 26, "пряма R_S:", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(op_x + 40, oy - 10, "I = −U_GS/R_S", size=11, color=NEG, anchor="start"))

    # точка перетину — робочий струм
    p.append(circle(op_x, op_y, 5, fill=FIELD, stroke="#1e7e44", sw=2))
    p.append(line(ox, op_y, op_x, op_y, color=MUTED, sw=1.0, dash="3,3"))
    p.append(line(op_x, oy, op_x, op_y, color=MUTED, sw=1.0, dash="3,3"))
    p.append(text(ox - 8, op_y + 4, "I_роб", size=12, color="#1e7e44", anchor="end", bold=True))
    p.append(fitbox(op_x + 8, op_y - 44, 150, 30, "робоча точка:\nструм < I_DSS", size=11,
                    fill="#eafaf1", stroke=FIELD, color="#1e7e44"))

    render(os.path.join(OUT, 'self-bias.svg'), W, H, *p)


def _gnd(p, x, y):
    """Символ землі під точкою (x,y)."""
    p.append(line(x - 16, y, x + 16, y, color=INK, sw=2.2))
    p.append(line(x - 10, y + 6, x + 10, y + 6, color=INK, sw=2))
    p.append(line(x - 5, y + 12, x + 5, y + 12, color=INK, sw=2))


# ── (вставка hist) Чому заземлене навантаження — складна вимога ──────────────
def hist_grounded_load():
    """Ліворуч — легкий випадок: навантаження «плаває», транзистор сам у ролі
    джерела струму. Праворуч — важкий: один кінець навантаження вже на землі,
    джерело мусить бути «зверху» й боротися з напругою, що гуляє з опором."""
    W, H = 760, 350
    p = []
    p.append(text(W / 2, 28, "Заземлене навантаження: джерело струму нема куди «сховати»", size=16, bold=True))
    midx = W / 2
    p.append(line(midx, 56, midx, H - 22, color="#d0d0d0", sw=1.5, dash="4,4"))
    gnd_y = H - 78

    # ── ліва панель: навантаження «плаває» (легко) ──
    lx = 150
    p.append(text(lx + 24, 52, "Навантаження «плаває»", size=14, color="#1e7e44", bold=True))
    src_l, sw_, sh_ = textbox(lx, 112, "джерело\nструму", size=12, pad=10,
                              fill="#eafaf1", stroke=FIELD, sw=2)
    p.append(src_l)
    ld_l, lw_, lh_ = textbox(lx, 204, "наван-\nтаження", size=12, pad=10, stroke=INK, sw=1.8)
    p.append(ld_l)
    p.append(line(lx, 112 + sh_ / 2, lx, 204 - lh_ / 2, color=INK, sw=2))
    p.append(arrow(lx, 134, lx, 178, color=FIELD, sw=2.2))
    p.append(line(lx, 204 + lh_ / 2, lx, gnd_y, color=INK, sw=2))
    _gnd(p, lx, gnd_y)
    p.append(text(lx, gnd_y + 42, "обидва кінці вільні —\nструм просто тече крізь", size=11, color=MUTED))

    # ── права панель: один кінець на землі (важко) ──
    rx = midx + 150
    p.append(text(rx + 14, 52, "Один кінець уже на землі", size=14, color=POS, bold=True))
    src_r, sw2, sh2 = textbox(rx, 112, "джерело\nмусить бути\nтут, «зверху»", size=12, pad=10,
                              fill="#fdecea", stroke=POS, sw=2)
    p.append(src_r)
    ld_r, lw2, lh2 = textbox(rx, 214, "наван-\nтаження", size=12, pad=10, stroke=INK, sw=1.8)
    p.append(ld_r)
    p.append(line(rx, 112 + sh2 / 2, rx, 214 - lh2 / 2, color=INK, sw=2))
    p.append(arrow(rx, 150, rx, 192, color=POS, sw=2.2))
    p.append(line(rx, 214 + lh2 / 2, rx, gnd_y, color=INK, sw=2))
    _gnd(p, rx, gnd_y)
    p.append(text(rx, gnd_y + 42, "напруга вузла гуляє з опором —\nважко тримати струм", size=11, color=POS))

    render(os.path.join(OUT, 'grounded-load.svg'), W, H, *p)


# ── (вставка hist) Міст опорів: рівновага R1/R2 = R3/R4 → опір виходу ∞ ───────
def hist_bridge_balance():
    """Дві гілки тягнуть вузол навантаження в різні боки. Поки міст
    збалансований (R1/R2 = R3/R4), будь-яка зміна напруги на навантаженні
    тягнеться однаково обома гілками й гаситься — струм не залежить від опору."""
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 28, "Гра опорів: збалансований міст робить вихідний опір нескінченним", size=15, bold=True))
    cx = W / 2

    # центральний вузол навантаження
    nx, ny = cx, 196
    p.append(circle(nx, ny, 7, fill=INK, stroke=INK))
    p.append(text(nx, ny - 18, "вузол навантаження  (iₒ)", size=13, color=INK, bold=True))

    # ── ліва, від'ємна гілка (через вхід −) ──
    lx = 122
    nb, nbw, nbh = textbox(lx, 118, "від'ємний\nзв'язок\n(R1, R2)", size=12, pad=10,
                           fill="#eaf0fd", stroke=NEG, sw=2)
    p.append(nb)
    p.append(text(lx, 118 - nbh / 2 - 13, "тягне вниз", size=12, color=NEG, italic=True))
    p.append(arrow(lx + nbw / 2 + 6, 124, nx - 70, ny - 8, color=NEG, sw=2.2))

    # ── права, додатна гілка (через вхід +) ──
    rx = W - 122
    pb, pbw, pbh = textbox(rx, 118, "додатний\nзв'язок\n(R3, R4)", size=12, pad=10,
                           fill="#fdecea", stroke=POS, sw=2)
    p.append(pb)
    p.append(text(rx, 118 - pbh / 2 - 13, "тягне вгору", size=12, color=POS, italic=True))
    p.append(arrow(rx - pbw / 2 - 6, 124, nx + 70, ny - 8, color=POS, sw=2.2))

    # рівновага в центрі
    eqb, eqw, eqh = textbox(cx, ny + 86,
                            "R1/R2 = R3/R4\n→ дві тяги рівні й гасять одна одну\n→ опір виходу = ∞",
                            size=13, pad=12, fill="#eafaf1", stroke=FIELD, sw=2.2)
    p.append(eqb)
    p.append(line(nx, ny + 7, cx, ny + 86 - eqh / 2, color=FIELD, sw=2, dash="4,4"))

    p.append(text(cx, H - 20,
                  "струм у навантаження не залежить від його опору — рівно vᵢ/R1",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'bridge-balance.svg'), W, H, *p)


if __name__ == '__main__':
    duality()
    iv_curve()
    compliance()
    transistor()
    norton_divider()
    jfet_cld()
    self_bias()
    hist_grounded_load()
    hist_bridge_balance()
    print("OK: 9 фігур у", OUT)
