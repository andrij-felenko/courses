# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GREEN = FIELD
GREY  = "#e5e7eb"
BAND  = "#dbeafe"   # синя смуга «валідно»
FORB  = "#fde2e1"   # червонувата «заборонена зона»


# ── Фігура 1: сходи рівнів — VOH/VOL відправника vs VIH/VIL приймача, запас ──
def fig_margins():
    W, H = 720, 430
    frags = []
    frags.append(text(W/2, 26, "Рівні напруги і запас завадостійкості (3.3 В)", size=17, bold=True))

    # вертикальна вісь напруги ліворуч
    ax_x = 70
    top, bot = 70, 360
    v_top, v_bot = 3.3, 0.0
    def yv(v):  # напруга -> y
        return bot - (v - v_bot) / (v_top - v_bot) * (bot - top)

    frags.append(line(ax_x, top, ax_x, bot, color=INK, sw=2))
    for v in (0.0, 0.4, 0.8, 2.0, 2.4, 3.3):
        y = yv(v)
        frags.append(line(ax_x - 5, y, ax_x, y, color=INK, sw=1.5))
        frags.append(text(ax_x - 10, y + 4, ("%.1f" % v), size=12, color=MUTED, anchor="end"))
    frags.append(text(ax_x - 44, top - 14, "В", size=12, color=MUTED, anchor="start"))

    # колонка ВІДПРАВНИК
    cx1 = 240
    cw = 150
    frags.append(text(cx1, top - 24, "виходить із відправника", size=13, bold=True))
    # HIGH-вихід: 2.4 .. 3.3 гарантовано
    frags.append(rect(cx1 - cw/2, yv(3.3), cw, yv(2.4) - yv(3.3), fill=BAND, stroke=NEG, sw=1.5))
    frags.append(text(cx1, (yv(3.3)+yv(2.4))/2 + 4, "«1»  VOH ≥ 2.4", size=12, color=NEG, bold=True))
    # LOW-вихід: 0 .. 0.4
    frags.append(rect(cx1 - cw/2, yv(0.4), cw, yv(0.0) - yv(0.4), fill=BAND, stroke=NEG, sw=1.5))
    frags.append(text(cx1, (yv(0.4)+yv(0.0))/2 + 4, "«0»  VOL ≤ 0.4", size=12, color=NEG, bold=True))

    # колонка ПРИЙМАЧ
    cx2 = 470
    frags.append(text(cx2, top - 24, "приймач мусить розпізнати", size=13, bold=True))
    # HIGH-вхід: 2.0 .. 3.3
    frags.append(rect(cx2 - cw/2, yv(3.3), cw, yv(2.0) - yv(3.3), fill="#eafaf1", stroke=GREEN, sw=1.5))
    frags.append(text(cx2, (yv(3.3)+yv(2.0))/2 + 4, "«1»  VIH ≥ 2.0", size=12, color=GREEN, bold=True))
    # LOW-вхід: 0 .. 0.8
    frags.append(rect(cx2 - cw/2, yv(0.8), cw, yv(0.0) - yv(0.8), fill="#eafaf1", stroke=GREEN, sw=1.5))
    frags.append(text(cx2, (yv(0.8)+yv(0.0))/2 + 4, "«0»  VIL ≤ 0.8", size=12, color=GREEN, bold=True))
    # заборонена зона приймача 0.8 .. 2.0
    frags.append(rect(cx2 - cw/2, yv(2.0), cw, yv(0.8) - yv(2.0), fill=FORB, stroke=POS, sw=1.2))
    frags.append(text(cx2, (yv(2.0)+yv(0.8))/2 + 4, "невизначено", size=11, color=POS))

    # стрілки-запаси між колонками
    # верхній запас: від 2.4 (VOH) до 2.0 (VIH) = 0.4 В
    frags.append(arrow(cx1 + cw/2 + 8, yv(2.4), cx2 - cw/2 - 8, yv(2.0), color=INK, sw=1.6))
    frags.append(text((cx1+cx2)/2, yv(2.2) - 6, "запас «1»  ≈ 0.4 В", size=11, color=INK, bold=True))
    # нижній запас: від 0.4 (VOL) до 0.8 (VIL) = 0.4 В
    frags.append(arrow(cx1 + cw/2 + 8, yv(0.4), cx2 - cw/2 - 8, yv(0.8), color=INK, sw=1.6))
    frags.append(text((cx1+cx2)/2, yv(0.6) + 16, "запас «0»  ≈ 0.4 В", size=11, color=INK, bold=True))

    frags.append(text(W/2, H - 12,
                      "Вихід тримає рівень із запасом; приймач приймає рішення з нижчим порогом — різниця і є захист від завад.",
                      size=11, color=MUTED))
    render(os.path.join(OUT, "margins.svg"), W, H, *frags)


# ── Фігура 2: рейка-в-рейку CMOS vs «плаваючий» TTL-вихід ────────────────────
def fig_cmos_vs_ttl():
    W, H = 700, 340
    frags = []
    frags.append(text(W/2, 26, "Чому LVCMOS має ширший запас за LVTTL (3.3 В)", size=17, bold=True))

    top, bot = 70, 280
    v_top, v_bot = 3.3, 0.0
    def yv(v):
        return bot - v / v_top * (bot - top)

    for cx, name, voh, vol, col in [
        (200, "LVTTL-вихід", 2.4, 0.4, MUTED),
        (500, "LVCMOS-вихід", 3.2, 0.1, GREEN)]:
        cw = 130
        frags.append(text(cx, top - 20, name, size=13, bold=True))
        # весь діапазон 0..3.3 сірим
        frags.append(rect(cx - cw/2, yv(3.3), cw, yv(0.0) - yv(3.3), fill=GREY, stroke=LINE, sw=1.2))
        # HIGH-зона
        frags.append(rect(cx - cw/2, yv(3.3), cw, yv(voh) - yv(3.3), fill=BAND, stroke=col, sw=1.5))
        frags.append(text(cx, (yv(3.3)+yv(voh))/2 + 4, "«1» ≥ %.1f" % voh, size=12, color=col, bold=True))
        # LOW-зона
        frags.append(rect(cx - cw/2, yv(vol), cw, yv(0.0) - yv(vol), fill=BAND, stroke=col, sw=1.5))
        frags.append(text(cx, (yv(vol)+yv(0.0))/2 + 4, "«0» ≤ %.1f" % vol, size=12, color=col, bold=True))
        # позначки країв
        frags.append(text(cx + cw/2 + 8, yv(3.3) + 4, "3.3", size=11, color=MUTED, anchor="start"))
        frags.append(text(cx + cw/2 + 8, yv(0.0) + 4, "0", size=11, color=MUTED, anchor="start"))

    frags.append(text(W/2, H - 20,
                      "TTL-вихід зупиняється, не дійшовши до рейок; CMOS-ключ тягне майже до 3.3 і до 0 — звідси більший запас.",
                      size=11, color=MUTED))
    render(os.path.join(OUT, "cmos-vs-ttl.svg"), W, H, *frags)


# ── Фігура 3: VREF-стандарт — приймач-компаратор із опорою й термінація VTT ──
def fig_vref():
    W, H = 720, 340
    frags = []
    frags.append(text(W/2, 26, "VREF-стандарт (SSTL/HSTL): малий розмах довкола опори", size=16, bold=True))

    # драйвер ліворуч
    dx = 90
    dy = 150
    frags.append(fitbox(dx - 45, dy - 28, 90, 56, "драйвер", fill=FILL, stroke=INK))
    # послідовний резистор (стаб)
    rx = 250
    frags.append(line(dx + 45, dy, rx - 24, dy, color=INK, sw=2))
    frags.append(rect(rx - 24, dy - 12, 48, 24, fill="#eef2ff", stroke=INK, sw=1.5))
    frags.append(text(rx, dy - 18, "Rs ~25 Ω", size=11, color=INK))
    # лінія до приймача
    px = 560
    frags.append(line(rx + 24, dy, px - 46, dy, color=INK, sw=2))

    # приймач як компаратор
    tri = [(px - 46, dy - 34), (px - 46, dy + 34), (px + 34, dy)]
    frags.append('<polygon points="%s" fill="#eafaf1" stroke="%s" stroke-width="1.8"/>'
                 % (" ".join("%.0f,%.0f" % p for p in tri), GREEN))
    frags.append(text(px - 20, dy + 4, "приймач", size=11, color=GREEN))
    frags.append(text(px + 44, dy + 4, "→ «0»/«1»", size=11, color=INK, anchor="start"))

    # опора VREF на − вхід
    frags.append(line(px - 60, dy + 60, px - 46, dy + 18, color=NEG, sw=1.6))
    frags.append(text(px - 92, dy + 74, "VREF = VDDQ/2", size=12, color=NEG, bold=True, anchor="start"))

    # термінація VTT на середині лінії
    tx = 420
    frags.append(line(tx, dy, tx, dy + 46, color=POS, sw=1.6))
    frags.append(rect(tx - 12, dy + 46, 24, 40, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(tx + 40, dy + 70, "Rt", size=11, color=POS))
    frags.append(text(tx, dy + 104, "VTT = VREF", size=12, color=POS, bold=True))

    # мала «хвиля» розмаху над лінією
    sw_x = 300
    frags.append(line(sw_x, dy - 60, sw_x + 90, dy - 60, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(sw_x, dy - 40, sw_x + 90, dy - 40, color=MUTED, sw=1, dash="3,3"))
    frags.append(arrow(sw_x + 45, dy - 40, sw_x + 45, dy - 60, color=INK, sw=1.3))
    frags.append(arrow(sw_x + 45, dy - 60, sw_x + 45, dy - 40, color=INK, sw=1.3))
    frags.append(text(sw_x + 45, dy - 68, "розмах лише ~0.7 В", size=11, color=INK))

    frags.append(text(W/2, H - 16,
                      "Приймач порівнює вхід не з фіксованим порогом, а з опорою VREF: сигнал може бути малим і швидким.",
                      size=11, color=MUTED))
    render(os.path.join(OUT, "vref.svg"), W, H, *frags)


# ── Фігура 4 (hist): смуга часу JEDEC — від ламп до родини JESD8 ──────────────
def fig_jedec_timeline():
    W, H = 820, 380
    frags = []
    frags.append(text(W / 2, 26, "Від ради з нумерації ламп до родини рівнів JESD8", size=17, bold=True))

    # горизонтальна вісь часу — кусково: рідкі ранні роки ліворуч (40%),
    # густа доба 1990-х праворуч (60%), з видимим «зламом» між ними.
    ax_y = 158
    x0, x1 = 70, 748
    xb = x0 + 0.40 * (x1 - x0)   # точка зламу масштабу
    frags.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    frags.append(text(x1 + 8, ax_y + 4, "рік", size=12, color=MUTED, anchor="start"))

    def xt(year):
        if year <= 1990:                       # 1944..1990 -> ліва частина
            return x0 + (year - 1944) / (1990 - 1944) * (xb - x0)
        return xb + (year - 1990) / (1999 - 1990) * (x1 - xb)  # 1990..1999 -> права

    # позначка зламу масштабу (дві скісні риски)
    for dx in (-4, 2):
        frags.append(line(xb + dx - 3, ax_y - 6, xb + dx + 3, ax_y + 6, color=MUTED, sw=1.4))

    for yr in (1944, 1958, 1990, 1994, 1999):
        x = xt(yr)
        frags.append(line(x, ax_y - 5, x, ax_y + 5, color=INK, sw=1.5))
        frags.append(text(x, ax_y + 22, str(yr), size=12, color=MUTED))

    def clamp(cx, w):
        half = w / 2
        return min(max(cx, 8 + half), W - 8 - half)

    # події НАД віссю (як мінялась рада)
    def event_up(year, title, sub, color, depth=56):
        x = xt(year)
        w = max(text_width(title, 11, True), text_width(sub, 11)) + 16
        cx = clamp(x, w)
        frags.append(line(x, ax_y - 4, cx, ax_y - depth + 14, color=color, sw=1.3, dash="3,3"))
        b, bw, bh = textbox(cx, ax_y - depth - 4, "%s\n%s" % (title, sub), size=11,
                            fill="#eef2ff", stroke=color, color=INK, pad=8)
        frags.append(b)

    # події ПІД віссю (коли рівні стали стандартом) — легкий стагер за глибиною
    def event_dn(year, title, sub, color, depth):
        x = xt(year)
        w = max(text_width(title, 11, True), text_width(sub, 11)) + 16
        cx = clamp(x, w)
        frags.append(line(x, ax_y + 4, cx, ax_y + depth - 14, color=color, sw=1.3, dash="3,3"))
        b, bw, bh = textbox(cx, ax_y + depth, "%s\n%s" % (title, sub), size=11,
                            fill="#eafaf1", stroke=color, color=INK, pad=8)
        frags.append(b)

    event_up(1944, "JETEC", "нумерація ламп", MUTED)
    event_up(1958, "JEDEC", "тепер — прилади", NEG)
    event_up(1999, "незалежна", "асоціація", MUTED)

    event_dn(1994, "3.3 В: JESD8-A", "LVTTL + LVCMOS", FIELD, 52)
    event_dn(1995, "HSTL: JESD8-6", "1.5 В · 08.1995", POS, 108)
    event_dn(1997, "SSTL: JESD8-8/9", "для пам'яті", POS, 52)

    frags.append(text(W / 2, H - 12,
                      "Над віссю — як мінялась сама рада; під віссю — коли вона звела кожну родину рівнів у стандарт.",
                      size=11, color=MUTED))
    render(os.path.join(OUT, "jedec-timeline.svg"), W, H, *frags)


# ── Фігура (hist-ttl): чому 5 В — вузьке вікно між стелею й підлогою ──────────
def fig_ttl_window():
    W, H = 720, 440
    frags = []
    frags.append(text(W/2, 26, "Чому TTL затиснуло живлення коло 5 В", size=17, bold=True))

    ax_x = 92
    top, bot = 66, 340
    v_top, v_bot = 7.0, 0.0
    def yv(v):
        return bot - (v - v_bot) / (v_top - v_bot) * (bot - top)

    frags.append(line(ax_x, top, ax_x, bot, color=INK, sw=2))
    for v in (0, 1, 2, 3, 4, 5, 6, 7):
        y = yv(v)
        frags.append(line(ax_x - 5, y, ax_x, y, color=INK, sw=1.4))
        frags.append(text(ax_x - 10, y + 4, str(v), size=12, color=MUTED, anchor="end"))
    frags.append(text(ax_x - 34, top - 12, "В", size=12, color=MUTED, anchor="start"))

    ceil = 5.5
    frags.append(rect(ax_x + 4, yv(7.0), 500, yv(ceil) - yv(7.0), fill=FORB, stroke=POS, sw=1.2))
    frags.append(text(ax_x + 254, yv(6.25) + 4, "пробій емітера ~5–6 В — вище не можна",
                      size=12, color=POS, bold=True))

    floor = 3.5
    frags.append(rect(ax_x + 4, yv(floor), 500, yv(0.0) - yv(floor), fill="#eef2ff", stroke=NEG, sw=1.0))
    frags.append(text(ax_x + 254, yv(1.7) + 4, "замало на стос переходів — нижче не тягне",
                      size=12, color=NEG, bold=True))

    frags.append(rect(ax_x + 4, yv(ceil), 500, yv(floor) - yv(ceil), fill="#eafaf1", stroke=FIELD, sw=1.6))
    frags.append(line(ax_x + 4, yv(5.0), ax_x + 504, yv(5.0), color=FIELD, sw=2.2, dash="6,3"))
    frags.append(text(ax_x + 254, yv(4.55) + 4, "робоче вікно → зупинилися на 5 В",
                      size=13, color=FIELD, bold=True))

    frags.append(text(W/2, H - 26,
                      "Вхід TTL — це емітер транзистора «навпаки»: його пробій тисне стелю вниз,",
                      size=11, color=MUTED))
    frags.append(text(W/2, H - 11,
                      "а стос переходів тисне підлогу вгору; лишається вузька смуга — 5 В опинилися рівно в ній.",
                      size=11, color=MUTED))
    render(os.path.join(OUT, "ttl-window.svg"), W, H, *frags)


# ── Фігура (hist-ttl): точка перемикання 1.4 В і симетричні пороги 0.8/2.0 ────
def fig_switch_point():
    W, H = 660, 360
    frags = []
    frags.append(text(W/2, 26, "Пороги 0.8 і 2.0 висять симетрично від точки 1.4 В", size=16, bold=True))

    ax_x = 300
    top, bot = 60, 300
    v_top, v_bot = 2.6, 0.0
    def yv(v):
        return bot - (v - v_bot) / (v_top - v_bot) * (bot - top)

    bw = 66
    frags.append(rect(ax_x - bw/2, yv(2.6), bw, yv(0.0) - yv(2.6), fill=GREY, stroke=LINE, sw=1.2))
    frags.append(rect(ax_x - bw/2, yv(0.8), bw, yv(0.0) - yv(0.8), fill="#eafaf1", stroke=FIELD, sw=1.4))
    frags.append(rect(ax_x - bw/2, yv(2.6), bw, yv(2.0) - yv(2.6), fill=BAND, stroke=NEG, sw=1.4))
    frags.append(rect(ax_x - bw/2, yv(2.0), bw, yv(0.8) - yv(2.0), fill=FORB, stroke=POS, sw=1.2))

    frags.append(line(ax_x - bw/2 - 40, yv(1.4), ax_x + bw/2 + 30, yv(1.4), color=INK, sw=2, dash="5,3"))
    frags.append(text(ax_x + bw/2 + 36, yv(1.4) + 4, "1.4 В = 2 × 0.7 (точка перемикання)",
                      size=12, color=INK, bold=True, anchor="start"))
    frags.append(text(ax_x + bw/2 + 36, yv(2.0) + 4, "VIH = 2.0  (поріг «1»)", size=12, color=NEG, bold=True, anchor="start"))
    frags.append(text(ax_x + bw/2 + 36, yv(0.8) + 4, "VIL = 0.8  (поріг «0»)", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(arrow(ax_x - bw/2 - 16, yv(1.4), ax_x - bw/2 - 16, yv(2.0), color=INK, sw=1.4))
    frags.append(text(ax_x - bw/2 - 22, (yv(1.4)+yv(2.0))/2 + 4, "+0.6", size=11, color=INK, anchor="end"))
    frags.append(arrow(ax_x - bw/2 - 16, yv(1.4), ax_x - bw/2 - 16, yv(0.8), color=INK, sw=1.4))
    frags.append(text(ax_x - bw/2 - 22, (yv(1.4)+yv(0.8))/2 + 4, "−0.6", size=11, color=INK, anchor="end"))
    frags.append(text(ax_x, (yv(2.6)+yv(2.0))/2 + 4, "«1»", size=13, color=NEG, bold=True))
    frags.append(text(ax_x, (yv(0.8)+yv(0.0))/2 + 4, "«0»", size=13, color=FIELD, bold=True))

    frags.append(text(W/2, H - 12,
                      "Від точки перемикання ~1.4 В відклали однаковий запас угору і вниз — так і вийшла пара 2.0 / 0.8.",
                      size=11, color=MUTED))
    render(os.path.join(OUT, "switch-point.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_margins()
    fig_cmos_vs_ttl()
    fig_vref()
    fig_jedec_timeline()
    fig_ttl_window()
    fig_switch_point()
    print("ok")
