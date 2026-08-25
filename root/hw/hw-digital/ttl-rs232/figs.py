# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

YELLOW = "#b08900"   # «0» RS-232 / попередження рівня
VIOLET = "#7a2bd6"   # «1» RS-232 (від'ємна напруга)


def waveform(ox, hi, lo, unit, bits, x0=None):
    """Прямокутна хвиля за списком бітів (0/1). hi,lo — y-координати рівнів.
    Повертає (фрагменти, x_кінця). unit — ширина одного біта."""
    frags = []
    x = ox if x0 is None else x0
    prev = None
    for b in bits:
        y = hi if b else lo
        if prev is not None and prev != y:          # вертикальний фронт
            frags.append(line(x, prev, x, y, color=INK, sw=2.6))
        frags.append(line(x, y, x + unit, y, color=INK, sw=2.6))
        prev = y
        x += unit
    return frags, x


# ── ttl-levels: спокій=VCC, старт тягне до нуля ───────────────────────────────
# Ідея: UART прямо на ніжці МК — однополярний, неінвертований; «1»=VCC, «0»=0.

def fig_ttl_levels():
    W, H = 720, 300
    ox = 120
    hi, lo = 110, 200
    unit = 52
    bits = [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1]    # спокій-старт-…-стоп
    p = []

    # шкала рівнів
    p.append(line(ox - 10, hi, ox - 10, lo, color=MUTED, sw=1.4))
    p.append(line(ox - 16, hi, ox - 4, hi, color=MUTED, sw=1.4))
    p.append(line(ox - 16, lo, ox - 4, lo, color=MUTED, sw=1.4))
    p.append(text(ox - 22, hi + 4, "VCC", size=12, color=POS, anchor="end", bold=True))
    p.append(text(ox - 22, lo + 4, "0 В", size=12, color=NEG, anchor="end", bold=True))
    p.append(text(ox - 22, hi - 14, "3.3 або 5 В", size=11, color=MUTED, anchor="end"))

    wf, xend = waveform(ox, hi, lo, unit, bits)
    p += wf

    # підписи спокій / старт / стоп
    p.append(text(ox + unit * 0.5, hi - 12, "спокій=1", size=11, color=MUTED, italic=True))
    p.append(text(ox + unit * 1.5, lo + 22, "СТАРТ", size=11, color=POS, bold=True))
    p.append(text(xend - unit * 0.5, hi - 12, "стоп=1", size=11, color=MUTED, italic=True))

    p.append(text(W / 2, H - 26,
                  "однополярний і неінвертований — як будь-який цифровий сигнал",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, H - 8,
                  "рівень «1» прив'язаний до напруги живлення чипа",
                  size=11, color=INK))

    render(os.path.join(OUT, "ttl-levels.svg"), W, H, *p,
           title="TTL-рівні UART: «1» = VCC, «0» = 0 В")


# ── 3v3-vs-5v: перенапруга проти недостатнього рівня ──────────────────────────
# Ідея: 5→3.3 — перенапруга (вбиває вхід); 3.3→5 — часто ок, та для CMOS буває замало.

def fig_3v3_vs_5v():
    W, H = 900, 320
    p = []
    bw, bh = 150, 84
    y = 110

    # ліворуч: 5 В → 3.3 В (небезпечно). Пара по центру 225.
    p.append(text(225, 86, "5 В → 3.3 В", size=14, color=POS, bold=True))
    p.append(fitbox(70, y, bw, bh, "TX 5 В\nвихід 5 В", size=12, bold=True,
                    fill=BG, stroke=POS, sw=2, color=INK))
    p.append(fitbox(280, y, bw, bh, "RX 3.3 В\nмакс ≈3.6 В", size=12, bold=True,
                    fill=BG, stroke=NEG, sw=2, color=INK))
    p.append(arrow(220, y + bh / 2, 280, y + bh / 2, color=POS, sw=2.4))
    p.append(text(250, y + bh / 2 - 8, "5 В", size=11, color=POS, bold=True))
    p.append(text(225, y + bh + 24, "перенапруга → ушкодження входу",
                  size=11, color=POS, bold=True))
    p.append(text(225, y + bh + 42, "(потрібен зсув рівнів: дільник / буфер)",
                  size=10, color=MUTED, italic=True))

    # праворуч: 3.3 В → 5 В (часто ок). Пара по центру 675.
    p.append(text(675, 86, "3.3 В → 5 В", size=14, color=YELLOW, bold=True))
    p.append(fitbox(520, y, bw, bh, "TX 3.3 В\nвихід 3.3 В", size=12, bold=True,
                    fill=BG, stroke=NEG, sw=2, color=INK))
    p.append(fitbox(730, y, bw, bh, "RX 5 В\nпоріг VIH", size=12, bold=True,
                    fill=BG, stroke=YELLOW, sw=2, color=INK))
    p.append(arrow(670, y + bh / 2, 730, y + bh / 2, color=NEG, sw=2.4))
    p.append(text(700, y + bh / 2 - 8, "3.3 В", size=11, color=NEG, bold=True))
    p.append(text(675, y + bh + 24, "5 В TTL (VIH≈2.0): ок",
                  size=11, color=FIELD, bold=True))
    p.append(text(675, y + bh + 42, "5 В CMOS (VIH≈3.5): замало!",
                  size=11, color=POS, bold=True))

    p.append(fitbox(60, 268, W - 120, 40,
                    "5→3.3 майже завжди потребує зсуву рівнів; 3.3→5 часто працює, та перевір VIH приймача",
                    size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "3v3-vs-5v.svg"), W, H, *p,
           title="3.3 В проти 5 В: пряме з'єднання буває небезпечним")


# ── rs232-vs-ttl: той самий байт біполярно ТА інвертовано ─────────────────────
# Ідея: угорі TTL (спокій високий), унизу RS-232 — «1» від'ємна, біполярно, ±12 В.

def fig_rs232_vs_ttl():
    W, H = 860, 380
    ox = 130
    unit = 54
    bits = [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1]
    p = []

    # TTL угорі
    hi1, lo1 = 90, 150
    p.append(text(120, 110, "TTL", size=13, color=INK, anchor="end", bold=True))
    wf, xend = waveform(ox, hi1, lo1, unit, bits)
    p += wf
    p.append(text(120, hi1 + 4, "3.3 В", size=10, color=POS, anchor="end"))
    p.append(text(120, lo1 + 4, "0 В", size=10, color=NEG, anchor="end"))
    p.append(text(xend + 8, hi1 + 4, "спокій=1=ВИСОКО", size=10, color=MUTED, anchor="start"))

    # RS-232 унизу (нуль посередині, «1» внизу)
    hiR, midR, loR = 240, 290, 340     # +12 / 0 / −12
    p.append(text(120, 300, "RS-232", size=13, color=INK, anchor="end", bold=True))
    p.append(line(ox - 6, midR, xend + 60, midR, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(xend + 66, midR + 4, "0 В", size=10, color=MUTED, anchor="start"))
    # та сама послідовність, але рівні інвертовано: 1→loR(−12), 0→hiR(+12)
    wfR, _ = waveform(ox, loR, hiR, unit, bits)   # hi-параметр=loR (для b=1), lo=hiR (для b=0)
    p += wfR
    p.append(text(120, hiR + 4, "+12 В", size=10, color=YELLOW, anchor="end"))
    p.append(text(120, loR + 4, "−12 В", size=10, color=VIOLET, anchor="end"))
    p.append(text(xend + 8, loR + 4, "спокій=1=НИЗЬКО", size=10, color=MUTED, anchor="start"))

    # стрілка «та сама 1 — догори дриґом»
    p.append(line(ox + unit * 0.5, lo1 + 6, ox + unit * 0.5, hiR - 6,
                  color=FIELD, sw=1.6, dash="4 4"))
    p.append(text(ox + unit * 0.5 + 8, (lo1 + hiR) / 2, "та сама «1» — догори дриґом",
                  size=10, color=FIELD, anchor="start", bold=True))

    p.append(fitbox(60, 352, W - 120, 22,
                    "несумісність тричі: інша полярність, інвертована логіка і ±12 В замість 0…3.3 В",
                    size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.6))

    render(os.path.join(OUT, "rs232-vs-ttl.svg"), W, H, *p,
           title="RS-232: той самий байт, але біполярно ТА інвертовано")


# ── noise-margin: запас завадостійкості RS-232 проти TTL 3.3 В ────────────────
# Ідея: дві вертикальні шкали; у RS-232 між рівнями й порогом — багато вольтів,
# у TTL 3.3 В — лічені сотні мілівольтів.

def fig_noise_margin():
    W, H = 760, 380
    p = []
    top, bot = 80, 330

    def scale(cx, label, ticks, bands, margin):
        out = [text(cx, top - 16, label, size=13, color=INK, bold=True)]
        out.append(line(cx, top, cx, bot, color=INK, sw=2))
        for ty, lab in ticks:
            out.append(line(cx - 6, ty, cx + 6, ty, color=INK, sw=1.4))
            out.append(text(cx - 12, ty + 4, lab, size=10, color=MUTED, anchor="end"))
        for y0, y1, col, fill, lab in bands:
            out.append(rect(cx - 30, y0, 60, y1 - y0, fill=fill, stroke=col, sw=1.2, rx=0))
            out.append(text(cx + 40, (y0 + y1) / 2 + 4, lab, size=10, color=col, anchor="start"))
        # стрілка-запас
        my0, my1 = margin
        out.append(line(cx - 50, my0, cx - 50, my1, color=FIELD, sw=2, dash=None))
        out.append(text(cx - 56, (my0 + my1) / 2, "запас", size=10, color=FIELD,
                        anchor="end", bold=True))
        return out

    # RS-232: +15..-15, пороги ±3
    p += scale(250, "RS-232 (±)",
               [(top, "+15"), (175, "+3"), (205, "0"), (235, "−3"), (bot, "−15")],
               [(top, 175, FIELD, "#eef6ef", "«0»: +5…+15"),
                (175, 235, POS, "#fdeeee", "невизначена зона ±3 В"),
                (235, bot, FIELD, "#eef6ef", "«1»: −5…−15")],
               (175, top + 30))

    # TTL 3.3: 3.3..0, VIH 2.0 / VIL 0.8
    p += scale(560, "TTL 3.3 В",
               [(top, "3.3"), (175, "VIH 2.0"), (268, "VIL 0.8"), (bot, "0")],
               [(top, 175, FIELD, "#eef6ef", "«1»"),
                (175, 268, POS, "#fdeeee", "зона ≈1.2 В"),
                (268, bot, FIELD, "#eef6ef", "«0»")],
               (175, top + 30))

    p.append(fitbox(60, 348, W - 120, 24,
                    "RS-232 терпить кілька вольтів завад на кабелі; у TTL 3.3 В запас — лічені сотні мілівольтів",
                    size=12, bold=True, fill=FILL, stroke=MUTED, sw=1.4))

    render(os.path.join(OUT, "noise-margin.svg"), W, H, *p,
           title="Навіщо такий розмах: запас завадостійкості RS-232")


# ── converter: MAX232 між TTL і RS-232 ────────────────────────────────────────
# Ідея: конвертер перекладає рівні в обидва боки й сам накачує ±10 В із 5 В.

def fig_converter():
    W, H = 740, 320
    p = []
    cy = 150
    # центральний чип
    chip, cw, ch = textbox(W / 2, cy, "конвертер рівнів\n(MAX232)", size=13, bold=True,
                           fill="#eef4ff", stroke=NEG, sw=2, pad=16, min_w=200)
    # TTL-бік ліворуч
    p.append(fitbox(50, cy - 42, 150, 84, "TTL-бік\nМК · 3.3/5 В\nнеінвертовано",
                    size=11, bold=True, fill=FILL, stroke=INK, sw=1.6))
    # RS-232-бік праворуч
    p.append(fitbox(W - 200, cy - 42, 150, 84, "RS-232-бік\n±12 В\nінвертовано",
                    size=11, bold=True, fill=FILL, stroke=POS, sw=1.6))
    p.append(chip)
    # двосторонні стрілки
    p.append(arrow(205, cy - 14, W / 2 - cw / 2 - 4, cy - 14, color=INK, sw=1.8))
    p.append(arrow(W / 2 - cw / 2 - 4, cy + 14, 205, cy + 14, color=INK, sw=1.8))
    p.append(arrow(W / 2 + cw / 2 + 4, cy - 14, W - 205, cy - 14, color=INK, sw=1.8))
    p.append(arrow(W - 205, cy + 14, W / 2 + cw / 2 + 4, cy + 14, color=INK, sw=1.8))
    # живлення 5 В і зарядні помпи знизу
    p.append(fitbox(W / 2 - cw / 2, cy + ch / 2 + 24, cw, 46,
                    "зарядні помпи: ±10 В з 5 В\n(кілька конденсаторів)",
                    size=11, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(arrow(W / 2, cy + ch / 2 + 70 + 6, W / 2, cy + ch / 2 + 6, color=FIELD, sw=1.8))
    p.append(text(W / 2, cy - ch / 2 - 14, "єдина шина 5 В — окреме живлення не потрібне",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "converter.svg"), W, H, *p,
           title="Конвертер рівнів MAX232 між TTL і RS-232")


# ── usb-serial: сучасний «послідовний порт» через USB ─────────────────────────
# Ідея: ПК бачить віртуальний COM, кабель несе USB, чип-міст віддає TTL-UART.

def fig_usb_serial():
    W, H = 760, 230
    p = []
    y = 110
    bw, bh = 130, 64
    step = 152
    x = 24
    boxes = [
        ("ПК\nвіртуальний\nCOM-порт", FILL, INK),
        ("кабель\nUSB", "#eef4ff", NEG),
        ("чип-міст\nCP2102 · CH340\n· FT232", "#fdf6e3", YELLOW),
        ("TTL-UART\n3.3 В", "#eafaf0", FIELD),
        ("МК\nRX / TX", FILL, INK),
    ]
    centers = []
    for i, (lab, fill, col) in enumerate(boxes):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=10, bold=True,
                        fill=fill, stroke=col if col != INK else INK, sw=1.6, color=INK))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1] + 2, y, x - 2, y, color=INK, sw=1.7))
        x += step

    p.append(text(W / 2, H - 22,
                  "«COM-порт» — віртуальний; до МК доходить звичайний логічний рівень",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "usb-serial.svg"), W, H, *p,
           title="USB-to-serial міст: сучасний «послідовний порт»")


# ── matrix: що з чим з'єднується + типові помилки ─────────────────────────────
# Ідея: правила прямого з'єднання за рівнями і три класичні помилки «лінія є, зв'язку нема».

def fig_matrix():
    W, H = 760, 360
    p = []
    # рядки-правила
    rules = [
        ("TTL ↔ TTL однакової напруги", "напряму (навхрест, спільна земля)", FIELD),
        ("TTL 5 ↔ 3.3", "через зсув рівнів", YELLOW),
        ("TTL ↔ RS-232", "лише через конвертер (інакше спалиш вхід)", POS),
        ("RS-232 ↔ RS-232", "напряму", FIELD),
    ]
    y = 70
    rh = 42
    for left, right, col in rules:
        p.append(fitbox(40, y, 250, rh - 8, left, size=11, bold=True,
                        fill=FILL, stroke=INK, sw=1.4))
        p.append(text(300, y + (rh - 8) / 2 + 4, "→", size=16, color=col, anchor="start", bold=True))
        p.append(fitbox(326, y, W - 366, rh - 8, right, size=11, bold=True,
                        fill="#fbfbfb", stroke=col, sw=1.4, color=col))
        y += rh

    # три типові помилки
    p.append(text(W / 2, y + 18, "три класичні помилки «лінія є, а зв'язку нема»",
                  size=12, color=INK, bold=True))
    errs = ["TX↔TX замість навхрест", "забута спільна земля", "неузгоджені рівні / інверсія"]
    ex = 40
    ew = (W - 80 - 2 * 16) / 3
    for e in errs:
        p.append(fitbox(ex, y + 34, ew, 50, e, size=11, bold=True,
                        fill="#fdecea", stroke=POS, sw=1.5, color=POS))
        ex += ew + 16

    render(os.path.join(OUT, "matrix.svg"), W, H, *p,
           title="Що з чим з'єднується напряму — і три типові помилки")


if __name__ == "__main__":
    fig_ttl_levels()
    fig_3v3_vs_5v()
    fig_rs232_vs_ttl()
    fig_noise_margin()
    fig_converter()
    fig_usb_serial()
    fig_matrix()
    print("OK: figures written to", OUT)
