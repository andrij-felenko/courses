# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольори субсвітлодіодів (не з палітри — це справжні R/G/B світла)
RED, GRN, BLU = POS, FIELD, NEG


def _pulse(x0, y_lo, y_hi, widths, sw=2.4, color=NEG):
    """Цифрова доріжка: widths = [(w_high, w_low), ...]; повертає polyline."""
    pts = ["%.1f,%.1f" % (x0, y_lo)]
    x = x0
    for wh, wl in widths:
        pts.append("%.1f,%.1f" % (x, y_hi))
        pts.append("%.1f,%.1f" % (x + wh, y_hi))
        pts.append("%.1f,%.1f" % (x + wh, y_lo))
        x += wh + wl
        pts.append("%.1f,%.1f" % (x, y_lo))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), color, sw))


# ── 1. Проблема «у лоб»: 300 каналів проти одного дроту ───────────────────────
# Ідея: наївне рішення (3 канали ШІМ на піксель) вибухає кількістю дротів;
# адресне виносить ШІМ у піксель і лишає один дріт даних на всіх.
def fig_problem():
    W, H = 760, 300
    p = []
    # ліва рамка — «у лоб»
    p.append(rect(40, 70, 320, 180, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(200, 98, "«У лоб»", size=13, color=POS, bold=True))
    p.append(text(200, 126, "кожному RGB-світлодіоду —", size=11, color=INK))
    p.append(text(200, 146, "три канали ШІМ", size=12, color=INK, bold=True))
    p.append(text(200, 184, "100 пікселів → 300 каналів", size=12, color=POS, bold=True))
    p.append(text(200, 214, "неможливо", size=13, color=POS, bold=True))
    # права рамка — адресні
    p.append(rect(400, 70, 320, 180, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(560, 98, "Адресні (WS2812-клас)", size=13, color=FIELD, bold=True))
    p.append(text(560, 126, "кожен піксель — власний", size=11, color=INK))
    p.append(text(560, 146, "контролер, сам ШІМить R/G/B", size=11, color=INK))
    p.append(text(560, 184, "усі — на ОДНОМУ дроті даних", size=12, color=FIELD, bold=True))
    p.append(text(560, 214, "хоч тисяча пікселів", size=13, color=FIELD, bold=True))
    p.append(text(W / 2, 280, "МК більше не ШІМить кожен колір — він лише шле дані, а ШІМ робить сам піксель.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "problem-300-channels.svg"), W, H, *p,
           title="Адресні світлодіоди: кожен піксель — свого кольору")


# ── 2. ШІМ усередині пікселя: 24 біти → три широтно-імпульсні доріжки ─────────
def fig_pwm_inside_pixel():
    W, H = 760, 300
    p = []
    # вхід — 24 біти кольору
    b, bw, bh = textbox(150, 120, "24 біти кольору\nR=200  G=50  B=255",
                        size=11, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8)
    p.append(b)
    p.append(arrow(150 + bw / 2, 120, 300, 120, color=INK, sw=2))
    # піксель — рамка з трьома доріжками
    p.append(rect(300, 70, 420, 190, fill="#fbfbff", stroke=INK, sw=1.8))
    p.append(text(510, 92, "піксель: контролер + 3 субсвітлодіоди", size=11, color=INK, bold=True))
    rows = [("R", RED, [(46, 8)] * 5, "яскравість 198"),
            ("G", GRN, [(12, 42)] * 5, "яскравість 51"),
            ("B", BLU, [(58, 0)] * 4, "яскравість 255")]
    ry = 128
    for lab, col, widths, note in rows:
        p.append(text(326, ry + 4, lab, size=12, color=col, bold=True))
        p.append(_pulse(348, ry + 14, ry - 8, widths, sw=2.4, color=col))
        p.append(text(706, ry + 4, note, size=9, color=MUTED, anchor="end"))
        ry += 48
    p.append(text(W / 2, 286,
                  "Контролер пікселя широтно-імпульсно запалює кожен субсвітлодіод — той самий ШІМ, лише вбудований.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "pwm-inside-pixel.svg"), W, H, *p,
           title="ШІМ усередині кожного пікселя")


# ── 3. Ланцюжок DIN→DOUT: дані течуть від пікселя до пікселя ──────────────────
def fig_daisy_chain():
    W, H = 760, 280
    p = []
    y = 120
    # МК
    p.append(rect(40, y - 28, 90, 56, fill="#eaf0fd", stroke=NEG, sw=1.8))
    p.append(text(85, y + 5, "МК", size=13, color=NEG, bold=True))
    # три пікселі
    xs = [170, 350, 530]
    prev_r = 130
    for i, x in enumerate(xs, 1):
        p.append(rect(x, y - 28, 140, 56, fill="#eafaf0", stroke=FIELD, sw=1.8))
        p.append(text(x + 70, y - 4, "піксель %d" % i, size=11, color=FIELD, bold=True))
        p.append(text(x + 8, y + 18, "DIN", size=9, color=MUTED, anchor="start"))
        p.append(text(x + 132, y + 18, "DOUT", size=9, color=MUTED, anchor="end"))
        p.append(arrow(prev_r, y, x - 2, y, color=INK, sw=2))
        prev_r = x + 140
    p.append(arrow(prev_r, y, prev_r + 28, y, color=INK, sw=2))
    p.append(text(prev_r + 34, y + 4, "…далі", size=10, color=MUTED, anchor="start"))
    # пояснення
    p.append(text(W / 2, 198, "Перший піксель забирає СВОЇ перші 24 біти, а решту штовхає сусідові.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 222, "На N пікселів МК шле N×24 біти поспіль; наприкінці довгий LOW — скидання —",
                  size=10, color=MUTED))
    p.append(text(W / 2, 240, "вмикає всі кольори одночасно.", size=10, color=MUTED))
    render(os.path.join(OUT, "daisy-chain.svg"), W, H, *p,
           title="Ланцюжок: дані течуть від пікселя до пікселя")


# ── 4. Біти шириною імпульсу, без лінії такту ────────────────────────────────
def fig_bit_by_pulse_width():
    W, H = 760, 290
    p = []
    # доріжка: 1 0 1 1 0 — довгий/короткий HIGH
    seq = [1, 0, 1, 1, 0]
    x0, y_lo, y_hi = 110, 150, 110
    cell = 116
    widths = []
    for b in seq:
        wh = 78 if b else 34
        widths.append((wh, cell - wh))
        # підпис біта над вікном
        cx = x0 + sum(w[0] + w[1] for w in widths[:-1]) + cell / 2
        p.append(text(cx, 96, str(b), size=13, color=(GRN if b else POS), bold=True))
    p.append(_pulse(x0, y_lo, y_hi, widths, sw=2.6, color=NEG))
    p.append(text(x0 - 12, y_lo - 20, "DATA", size=10, color=NEG, anchor="end", bold=True))
    p.append(text(x0 + cell / 2, 172, "довгий HIGH = 1", size=9, color=GRN))
    p.append(text(x0 + cell + cell / 2, 172, "короткий HIGH = 0", size=9, color=POS))
    # рамка-висновок
    p.append(fitbox(110, 212, W - 220, 56,
                    "Такту нема — біт розрізняють за шириною імпульсу (вікно ~1.25 мкс, часи — сотні нс);\nтому таймінг критичний.",
                    size=10, fill="#fdf6e3", stroke="#caa24a", sw=1.4, bold=True))
    render(os.path.join(OUT, "bit-by-pulse-width.svg"), W, H, *p,
           title="Біти — шириною імпульсу (один дріт, без такту)")


# ── 5. Чому таймінг доручають залізу ─────────────────────────────────────────
def fig_timing_to_hardware():
    W, H = 760, 270
    p = []
    p.append(rect(40, 70, 320, 140, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(200, 96, "Біт-бенгінг у коді", size=12, color=POS, bold=True))
    p.append(text(200, 124, "смикаємо ніжку — а переривання", size=10, color=INK))
    p.append(text(200, 142, "збиває точний таймінг", size=10, color=INK))
    p.append(text(200, 174, "піксель прочитає не той біт →", size=10, color=POS))
    p.append(text(200, 194, "глюки кольору", size=12, color=POS, bold=True))
    p.append(rect(400, 70, 320, 140, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(560, 96, "Спеціальний блок", size=12, color=FIELD, bold=True))
    p.append(text(560, 124, "RMT (ESP32) чи DMA жене біти", size=10, color=INK))
    p.append(text(560, 142, "із точним таймінгом сам,", size=10, color=INK))
    p.append(text(560, 174, "не залежачи від коду й переривань", size=10, color=FIELD))
    p.append(text(560, 194, "кольори чисті", size=12, color=FIELD, bold=True))
    p.append(text(W / 2, 246, "Жорсткий таймінг без такту — робота для заліза, а не для програмного циклу.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "timing-to-hardware.svg"), W, H, *p,
           title="Чому таймінг роблять залізом, а не «руками»")


# ── 6. Живлення: стрічка — це вже силова електроніка ──────────────────────────
def fig_power_current():
    W, H = 760, 250
    p = []
    p.append(rect(50, 70, 320, 96, fill="#fdf6e3", stroke="#caa24a", sw=1.8))
    p.append(text(210, 98, "Скільки їсть струму", size=12, color="#8a6d1a", bold=True))
    p.append(text(210, 124, "піксель на повну білизну ≈ 60 мА", size=10, color=INK))
    p.append(text(210, 146, "(3 × 20 мА)", size=9, color=MUTED))
    p.append(rect(410, 70, 300, 96, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(560, 100, "100 пікселів ≈ 6 А", size=14, color=POS, bold=True))
    p.append(text(560, 128, "із ніжки МК такого не взяти —", size=10, color=INK))
    p.append(text(560, 148, "треба окреме живлення", size=10, color=INK))
    p.append(text(W / 2, 198, "Тому: окремий блок 5 В, спільна земля, зсув рівнів даних, конденсатор і резистор на даних.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 222, "Інжекція живлення по довжині й номінали обв'язки — у 🔌-вставці про стрічку.",
                  size=9, color=MUTED))
    render(os.path.join(OUT, "power-current.svg"), W, H, *p,
           title="Живлення: стрічка — це вже силова електроніка")


# ── proj ⚙️ 1. Точний таймінг біта WS2812B ───────────────────────────────────
def fig_bit_timing():
    W, H = 760, 300
    p = []
    y_lo, y_hi = 150, 100
    # «0»: вузький HIGH
    x0 = 80
    w0h, w0l = 40, 86
    p.append(_pulse(x0, y_lo, y_hi, [(w0h, w0l)], sw=3, color=NEG))
    p.append(text(x0 + w0h / 2, y_hi - 12, "T0H = 0.4 мкс", size=9, color=NEG, bold=True))
    p.append(text(x0 + w0h + w0l / 2, y_lo + 16, "T0L = 0.85 мкс", size=9, color=NEG))
    p.append(text(x0 + (w0h + w0l) / 2, 76, "«0»", size=14, color=NEG, bold=True))
    p.append(line(x0, 60, x0 + w0h + w0l, 60, color="#caa24a", sw=1.4, dash="5 3"))
    p.append(text(x0 + (w0h + w0l) / 2, 50, "T ≈ 1.25 мкс", size=9, color="#8a6a14", bold=True))
    # «1»: широкий HIGH
    x1 = x0 + w0h + w0l + 24
    w1h, w1l = 80, 46
    p.append(_pulse(x1, y_lo, y_hi, [(w1h, w1l)], sw=3, color=POS))
    p.append(text(x1 + w1h / 2, y_hi - 12, "T1H = 0.8 мкс", size=9, color=POS, bold=True))
    p.append(text(x1 + w1h + w1l / 2, y_lo + 16, "T1L = 0.45 мкс", size=9, color=POS))
    p.append(text(x1 + (w1h + w1l) / 2, 76, "«1»", size=14, color=POS, bold=True))
    p.append(line(x1, 60, x1 + w1h + w1l, 60, color="#caa24a", sw=1.4, dash="5 3"))
    p.append(text(x1 + (w1h + w1l) / 2, 50, "T ≈ 1.25 мкс", size=9, color="#8a6a14", bold=True))
    # reset
    xr = x1 + w1h + w1l + 16
    p.append(line(xr, y_lo, xr + 150, y_lo, color=MUTED, sw=3))
    p.append(rect(xr, y_hi, 150, 50, fill="#eeeeee", stroke=MUTED, sw=1.2, rx=0))
    p.append(text(xr + 75, y_hi + 22, "reset / latch", size=10, color=MUTED, bold=True))
    p.append(text(xr + 75, y_hi + 38, "≥ 50 мкс LOW", size=9, color=MUTED))
    p.append(text(64, y_lo - 22, "DATA", size=10, color=INK, anchor="end", bold=True))
    # висновок
    p.append(fitbox(80, 210, W - 160, 58,
                    "Інформація — у ТРИВАЛОСТІ HIGH, не в рівні. Вийшов за допуск ±150 нс —\nпіксель прочитає хибний біт, і колір «попливе».",
                    size=10, fill="#fdf6e3", stroke="#caa24a", sw=1.4, bold=True))
    render(os.path.join(OUT, "bit-timing.svg"), W, H, *p,
           title="Таймінг бітів WS2812B: «0» і «1» — лише тривалість HIGH у вікні ~1.25 мкс")


# ── proj ⚙️ 2. Один байт → 8 RMT-символів ────────────────────────────────────
def fig_encode_byte():
    W, H = 760, 340
    p = []
    bits = [1, 0, 1, 1, 0, 0, 1, 0]   # G = 0b10110010
    p.append(text(W / 2, 64, "G = 0b10110010  (старший біт зліва, MSB-first)", size=12, color=INK, bold=True))
    n = len(bits)
    cw = 70
    gap = 10
    total = n * cw + (n - 1) * gap
    x0 = (W - total) / 2
    # ряд бітів
    by = 84
    for i, b in enumerate(bits):
        x = x0 + i * (cw + gap)
        col = POS if b else NEG
        fill = "#fdecea" if b else "#eaf0fd"
        p.append(rect(x, by, cw, 40, fill=fill, stroke=col, sw=2))
        p.append(text(x + cw / 2, by + 28, str(b), size=18, color=col, bold=True))
    p.append(text(x0 + cw / 2, by + 56, "b7", size=9, color=MUTED))
    p.append(text(x0 + (n - 1) * (cw + gap) + cw / 2, by + 56, "b0", size=9, color=MUTED))
    # ряд символів: кожен біт → пара HIGH(довж)+LOW(довж)
    sy = 188
    p.append(text(W / 2, sy - 14, "кожен біт → один RMT-символ: HIGH(тіки) + LOW(тіки)", size=10, color=INK))
    for i, b in enumerate(bits):
        x = x0 + i * (cw + gap)
        col = POS if b else NEG
        # ширина HIGH-частини
        hi_w = cw * (8.0 / 12.0) if b else cw * (4.0 / 12.0)
        p.append(rect(x, sy, hi_w, 26, fill=col, stroke=col, sw=0, rx=2))
        p.append(rect(x + hi_w, sy, cw - hi_w, 26, fill="#e4e4e4", stroke=MUTED, sw=0, rx=2))
        p.append(text(x + cw / 2, sy + 42, ("8+4" if b else "4+8"), size=9, color=col, bold=True))
        # стрілка від біта до символу
        p.append(line(x + cw / 2, by + 40, x + cw / 2, sy, color=MUTED, sw=1))
    p.append(text(W / 2, sy + 64, "tick = 0.1 мкс;  «1»: 8+4 тіки = 0.8+0.4 мкс;  «0»: 4+8 тіки = 0.4+0.8 мкс",
                  size=10, color=INK))
    # висновок
    p.append(fitbox(80, sy + 78, W - 160, 44,
                    "Кадр: encodeByte(G) → encodeByte(R) → encodeByte(B) × N пікселів → rmtWrite().\nПорядок GRB (не RGB!) і MSB-first — дві типові пастки.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.5, bold=True))
    render(os.path.join(OUT, "encode-byte.svg"), W, H, *p,
           title="Один байт каналу → 8 RMT-символів: кожен біт = пара (HIGH, LOW)")


# ── comp 🔌 1. Живлення стрічки з інжекцією ───────────────────────────────────
def fig_power_injection():
    W, H = 820, 380
    p = []
    # БЖ 5 В
    p.append(rect(30, 150, 90, 64, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(75, 176, "БЖ 5 В", size=12, color=NEG, bold=True))
    p.append(text(75, 196, "окремий", size=9, color=MUTED))
    # ESP32
    p.append(rect(30, 280, 90, 56, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(75, 304, "ESP32", size=12, color=FIELD, bold=True))
    p.append(text(75, 322, "GPIO 3.3 В", size=9, color=MUTED))
    # рівнезсувач
    p.append(rect(150, 286, 78, 44, fill="#fdf6e3", stroke="#caa24a", sw=2))
    p.append(text(189, 305, "зсувач", size=10, color="#8a6d1a", bold=True))
    p.append(text(189, 321, "3.3→5 В", size=9, color="#8a6d1a"))
    p.append(arrow(120, 308, 150, 308, color=FIELD, sw=1.8))
    # 330 Ом
    p.append(rect(252, 290, 66, 36, fill=BG, stroke="#caa24a", sw=1.8))
    p.append(text(285, 312, "330 Ω", size=10, color="#8a6d1a", bold=True))
    p.append(arrow(228, 308, 252, 308, color="#caa24a", sw=1.8))
    # стрічка з пікселів
    px_y = 150
    pxs = [(150, "піксель 1"), (290, "піксель 2"), (430, "піксель 3"), (570, "… далі")]
    for x, lab in pxs:
        muted = lab.startswith("…")
        p.append(rect(x, px_y, 120, 56, fill=("#eeeeee" if muted else "#eafaf0"),
                      stroke=(MUTED if muted else FIELD), sw=2))
        p.append(text(x + 60, px_y + 26, lab, size=10, color=(MUTED if muted else FIELD), bold=True))
        if not muted:
            p.append(text(x + 60, px_y + 44, "RGB ШІМ", size=8, color=MUTED))
    for a, b in [(270, 290), (410, 430), (550, 570)]:
        p.append(arrow(a, px_y + 28, b, px_y + 28, color=INK, sw=1.8))
    # DIN від 330Ом до пікселя1
    p.append(line(318, 308, 210, 308, color="#caa24a", sw=1.6))
    p.append(line(210, 308, 210, px_y + 56, color="#caa24a", sw=1.6))
    # +5В товста шина зверху з інжекцією
    bus_y = 118
    p.append(line(120, 170, 120, bus_y, color=POS, sw=2.5))
    p.append(line(120, bus_y, 700, bus_y, color=POS, sw=3))
    p.append(text(120, bus_y - 8, "+5 В (товстий дріт)", size=9, color=POS, anchor="start", bold=True))
    for x, lab in [(210, "ПОЧАТОК"), (350, "СЕРЕДИНА"), (630, "КІНЕЦЬ")]:
        p.append(line(x, bus_y, x, px_y, color=POS, sw=2.2))
        p.append(text(x, bus_y - 8, lab, size=8, color=POS, bold=True))
    # GND товста шина знизу
    gnd_y = 250
    p.append(line(120, 214, 120, gnd_y, color=NEG, sw=2.2))
    p.append(line(120, gnd_y, 700, gnd_y, color=NEG, sw=3))
    p.append(text(120, gnd_y + 16, "GND (товстий дріт, спільна з ESP32)", size=9, color=NEG, anchor="start", bold=True))
    for x in (210, 350, 630):
        p.append(line(x, px_y + 56, x, gnd_y, color=NEG, sw=1.6))
    p.append(line(75, 280, 75, gnd_y, color=NEG, sw=1.6))
    # 1000 мкФ
    p.append(rect(126, 150, 18, 40, fill=BG, stroke="#caa24a", sw=1.6, rx=2))
    p.append(text(170, 142, "1000 мкФ", size=9, color="#8a6d1a", anchor="start", bold=True))
    # порівняння напруги
    p.append(rect(620, 150, 180, 70, fill="#f8f8ff", stroke=INK, sw=1.3))
    p.append(text(710, 168, "Напруга вздовж стрічки", size=10, color=INK, bold=True))
    p.append(line(632, 184, 788, 208, color=POS, sw=2.4))
    p.append(text(710, 200, "без інжекції: 5.0→3.6 В", size=8, color=POS, bold=True))
    p.append(line(632, 178, 788, 178, color=FIELD, sw=2.4))
    render(os.path.join(OUT, "power-injection.svg"), W, H, *p,
           title="Живлення WS2812-стрічки з інжекцією")


# ── comp 🔌 2. Бюджет струму і просадка напруги ──────────────────────────────
def fig_current_budget():
    W, H = 820, 380
    p = []
    # ── ліва панель: бар-чарт струму ──
    p.append(rect(30, 58, 360, 296, fill="#f7f8fc", stroke="#e4e4e4", sw=1.2))
    p.append(text(210, 80, "Піковий струм (повна білизна)", size=11, color=INK, bold=True))
    p.append(text(210, 96, "I = N × 60 мА", size=10, color=MUTED))
    base = 330
    axis_x = 70
    p.append(arrow(axis_x, base, axis_x, 120, color=INK, sw=1.4))
    p.append(text(axis_x, 112, "А", size=9, color=INK))
    scale = 200.0 / 18.0   # px per A, 18A -> 200px
    bars = [(130, "30 пікс", 1.8, "2.5 А", FIELD, "#eafaf0"),
            (230, "100 пікс", 6.0, "7.5 А", "#caa24a", "#fdf6e3"),
            (330, "300 пікс", 18.0, "25 А", POS, "#fdecea")]
    for cx, lab, amps, fuse, col, fill in bars:
        bh = amps * scale
        p.append(rect(cx - 38, base - bh, 76, bh, fill=fill, stroke=col, sw=1.8, rx=0))
        p.append(text(cx, base - bh - 10, "≈ %g А" % amps, size=10, color=col, bold=True))
        p.append(text(cx, base + 16, lab, size=9, color=INK))
        p.append(text(cx, base + 30, "запоб. " + fuse, size=8, color=MUTED))
    # ── права панель: просадка напруги ──
    p.append(rect(410, 58, 380, 296, fill="#f7f8fc", stroke="#e4e4e4", sw=1.2))
    p.append(text(600, 80, "Падіння напруги по довжині", size=11, color=INK, bold=True))
    p.append(text(600, 96, "ΔU = I · R; доріжка ≈ 2 Ω/м (тонка мідь)", size=9, color=MUTED))
    ox, oy = 450, 320
    aw, ah = 310, 190
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.4))
    p.append(text(ox + aw, oy + 16, "м", size=9, color=INK))
    p.append(text(ox - 6, oy - ah + 4, "ΔU (В)", size=9, color=INK, anchor="end"))
    # межа 0.5 В
    lim_y = oy - ah * (0.5 / 2.0)
    p.append(line(ox, lim_y, ox + aw, lim_y, color="#caa24a", sw=1.6, dash="5 3"))
    p.append(text(ox + aw, lim_y - 4, "0.5 В = ліміт", size=8, color="#8a6d1a", anchor="end"))
    # тонка мідь: круто росте, упирається в стелю 2В
    def vdrop(slope_v_per_m):
        pts = []
        for i in range(0, 51):
            m = 2.0 * i / 50.0
            v = min(slope_v_per_m * m, 2.0)
            pts.append("%.1f,%.1f" % (ox + (m / 2.0) * aw, oy - (v / 2.0) * ah))
        return pts
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>'
             % (" ".join(vdrop(2.0)), POS))
    p.append(text(ox + aw * 0.55, oy - ah * 0.92, "тонка мідь (≈2 Ω/м)", size=8, color=POS, bold=True))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>'
             % (" ".join(vdrop(0.3)), FIELD))
    p.append(text(ox + aw * 0.62, oy - ah * 0.30, "товстий дріт (≈0.3 Ω/м)", size=8, color=FIELD, bold=True))
    render(os.path.join(OUT, "current-budget.svg"), W, H, *p,
           title="Бюджет струму і просадка напруги по доріжці")


if __name__ == "__main__":
    fig_problem()
    fig_pwm_inside_pixel()
    fig_daisy_chain()
    fig_bit_by_pulse_width()
    fig_timing_to_hardware()
    fig_power_current()
    fig_bit_timing()
    fig_encode_byte()
    fig_power_injection()
    fig_current_budget()
    print("OK: figures written to", OUT)
