# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BITON  = "#27ae60"   # біт = 1
BITOFF = "#e8ebee"   # біт = 0
CLKCOL = "#2457d6"


def bitcell(x, y, w, h, v, size=15):
    fill = "#dcf3e4" if v else BITOFF
    stroke = BITON if v else "#9aa3ac"
    col = INK if v else MUTED
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=4)
    out += text(x + w / 2, y + h / 2 + size * 0.35, str(v), size=size, color=col, bold=True)
    return out


# ── Фігура 1: простір ↔ час. Байт «усі разом» → байт «по черзі» ──────────────
def fig_space_time():
    W, H = 760, 340
    bits = [1, 0, 1, 1, 0, 0, 1, 0]     # 0xB2, MSB..LSB
    parts = []

    # Лівий бік: паралель — 8 дротів, усі разом, у ту саму мить
    lx, ly = 40, 70
    cw, ch = 34, 34
    parts.append(text(lx + 4 * cw, ly - 26, "Паралельно: 8 дротів, усі біти в ту саму мить",
                      size=14, bold=True, anchor="middle"))
    for i, v in enumerate(bits):
        cx = lx + i * cw
        parts.append(bitcell(cx, ly, cw, ch, v))
        # дротик праворуч від кожної комірки
        parts.append(line(cx + cw, ly + ch / 2, cx + cw + 10, ly + ch / 2, color="#9aa3ac", sw=1.4))
        parts.append(text(cx + cw / 2, ly + ch + 16, "D%d" % (7 - i), size=10, color=MUTED))
    parts.append(text(lx + 4 * cw, ly + ch + 44, "8 ліній · 1 такт", size=12, color=MUTED))

    # Стрілка-перетворювач
    ax = lx + 8 * cw + 28
    box, bw, bh = textbox(ax + 40, ly + ch / 2, "перетворення\nпаралель → послідовно",
                          size=12, fill="#fff7e6", stroke="#d99a00", bold=True)
    parts.append(box)
    parts.append(arrow(lx + 8 * cw + 12, ly + ch / 2, ax + 40 - bw / 2 - 6, ly + ch / 2, color="#d99a00"))
    parts.append(arrow(ax + 40 + bw / 2 + 6, ly + ch / 2, ax + 40 + bw / 2 + 40, ly + ch / 2, color="#d99a00"))

    # Правий бік: послідовно — один дріт, біти в часі
    sx, sy = 70, 220
    parts.append(text(W / 2, sy - 34, "Послідовно: 1 дріт, ті самі біти по черзі в часі",
                      size=14, bold=True, anchor="middle"))
    tot = W - 2 * sx
    step = tot / 8.0
    parts.append(line(sx, sy + ch / 2, sx + tot, sy + ch / 2, color="#9aa3ac", sw=1.4))
    for i, v in enumerate(bits):
        cx = sx + i * step + (step - cw) / 2
        parts.append(bitcell(cx, sy, cw, ch, v))
    # вісь часу
    parts.append(arrow(sx, sy + ch + 22, sx + tot, sy + ch + 22, color=MUTED, sw=1.4))
    parts.append(text(sx + tot, sy + ch + 40, "час →", size=12, color=MUTED, anchor="end"))
    parts.append(text(sx, sy + ch + 40, "перший (старший) біт", size=11, color=MUTED, anchor="start"))
    parts.append(text(sx + tot, sy - 12, "останній (молодший)", size=11, color=MUTED, anchor="end"))

    render(os.path.join(OUT, 'space-time.svg'), W, H, *parts)


# ── Фігура 2: тайминг — дані на лінії, синхронні до такту, MSB першим ────────
def fig_timing():
    W, H = 760, 300
    bits = [1, 0, 1, 1, 0, 0, 1, 0]     # 0xB2
    parts = []

    x0, y_clk, y_dat = 90, 70, 190
    amp = 40
    n = len(bits)
    step = (W - x0 - 40) / n
    hi = lambda y: y - amp
    lo = lambda y: y

    parts.append(text(x0 - 10, hi(y_clk) - 14, "SCLK (такт)", size=13, bold=True, anchor="start"))
    parts.append(text(x0 - 10, hi(y_dat) - 14, "DATA (дані)", size=13, bold=True, anchor="start"))

    # такт: n імпульсів, дані міняються перед фронтом, читаються на фронті
    clk = []
    for i in range(n):
        bx = x0 + i * step
        mid = bx + step / 2
        clk += [line(bx, lo(y_clk), mid, lo(y_clk), color=CLKCOL, sw=2),
                line(mid, lo(y_clk), mid, hi(y_clk), color=CLKCOL, sw=2),
                line(mid, hi(y_clk), bx + step, hi(y_clk), color=CLKCOL, sw=2),
                line(bx + step, hi(y_clk), bx + step, lo(y_clk), color=CLKCOL, sw=2)]
        # позначка фронту, на якому приймач читає
        parts.append(line(mid, hi(y_dat) - 6, mid, lo(y_clk) + 6, color="#c0392b", sw=1, dash="3 3"))
    parts.extend(clk)

    # дані: рівень тримається весь такт, підпис біта
    prev = None
    for i, v in enumerate(bits):
        bx = x0 + i * step
        y = hi(y_dat) if v else lo(y_dat)
        # вертикальний перехід на межі такту
        if prev is not None and prev != v:
            parts.append(line(bx, hi(y_dat) if prev else lo(y_dat), bx, y, color=INK, sw=2))
        parts.append(line(bx, y, bx + step, y, color=INK, sw=2))
        parts.append(text(bx + step / 2, lo(y_dat) + 26, "b%d=%d" % (7 - i, v), size=11,
                          color=(BITON if v else MUTED)))
        prev = v

    parts.append(text(W / 2, H - 22,
                      "На кожен фронт такту приймач бере один біт; спершу йде старший (MSB)",
                      size=12, color=MUTED, anchor="middle"))
    parts.append(text(x0 + step / 2, hi(y_dat) - 30, "перший", size=10, color="#c0392b", anchor="middle"))

    render(os.path.join(OUT, 'timing.svg'), W, H, *parts)


# ── Фігура 3: round-trip PISO → одна лінія → SIPO, і чому не паралельна шина ──
def fig_roundtrip():
    W, H = 780, 360
    parts = []

    # TX: серіалізатор (PISO)
    tx, ty = 96, 120
    b1, w1, h1 = textbox(tx + 80, ty + 40, "Серіалізатор\n(PISO)", size=13,
                         fill="#eef4ff", stroke=CLKCOL, bold=True, min_w=150)
    parts.append(b1)
    parts.append(text(tx + 80, ty - 6, "передавач", size=12, color=MUTED, anchor="middle"))
    # паралельний вхід (8 стрілочок у бік PISO)
    for i in range(8):
        yy = ty + 8 + i * ((h1 - 16) / 7.0)
        parts.append(arrow(tx - 40, yy, tx + 80 - w1 / 2 - 4, yy, color="#9aa3ac", sw=1.3))
    parts.append(mtext(tx - 44, ty + 36, ["8 біт", "разом"], size=11, color=MUTED, anchor="end"))

    # одна лінія (лейн) з рухомими бітами
    lane_x1 = tx + 80 + w1 / 2 + 4
    rx = W - 96 - 150
    lane_x2 = rx - 4
    ly = ty + 40
    parts.append(line(lane_x1, ly, lane_x2, ly, color=INK, sw=2.4))
    seq = [1, 0, 1, 1, 0, 0, 1, 0]
    cw = 22
    span = (lane_x2 - lane_x1) - cw
    for i, v in enumerate(seq):
        cx = lane_x1 + 6 + i * (span / 7.0)
        parts.append(bitcell(cx, ly - cw / 2, cw, cw, v, size=12))
    parts.append(text((lane_x1 + lane_x2) / 2, ly - 26,
                      "1 лінія (або 1 диференціальна пара): біти по черзі", size=12, bold=True))
    parts.append(text((lane_x1 + lane_x2) / 2, ly + 34, "такт вбудований або окремий",
                      size=11, color=MUTED))

    # RX: десеріалізатор (SIPO)
    b2, w2, h2 = textbox(rx + 75, ty + 40, "Десеріалізатор\n(SIPO)", size=13,
                         fill="#eef4ff", stroke=CLKCOL, bold=True, min_w=150)
    parts.append(b2)
    parts.append(text(rx + 75, ty - 6, "приймач", size=12, color=MUTED, anchor="middle"))
    for i in range(8):
        yy = ty + 8 + i * ((h2 - 16) / 7.0)
        parts.append(arrow(rx + 75 + w2 / 2 + 4, yy, rx + 75 + w2 / 2 + 34, yy, color="#9aa3ac", sw=1.3))
    parts.append(mtext(rx + 75 + w2 / 2 + 38, ty + 36, ["8 біт", "разом"], size=11, color=MUTED, anchor="start"))

    # Нижня плашка: чому не паралельна шина
    note, nw, nh = textbox(W / 2, H - 46,
        "Паралельна шина з 8 дротів на високій швидкості страждає від різнобою затримок (skew),\n"
        "наведень (crosstalk) і завад (EMI). Один лейн знімає різнобій дріт-до-дроту за побудовою.",
        size=11.5, fill="#fdf3f2", stroke="#c0392b")
    parts.append(note)

    render(os.path.join(OUT, 'roundtrip.svg'), W, H, *parts)


# ── Фігура 4 (hist): три щаблі однієї думки — Ґаусс → Бодо → старт-стоп кадр ──
def fig_hist_frame():
    W, H = 780, 430
    parts = []

    STARTC = "#c0392b"   # стартовий біт
    STOPC  = "#2457d6"   # стоповий біт
    IDLE   = "#e8ebee"   # спокій (mark)

    def dcell(x, y, w, h, v, size=13):
        fill = "#dcf3e4" if v else BITOFF
        stroke = BITON if v else "#9aa3ac"
        col = INK if v else MUTED
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=3)
        out += text(x + w / 2, y + h / 2 + size * 0.35, str(v), size=size, color=col, bold=True)
        return out

    def labelbox(x, y, w, h, s, fill, stroke, size=12):
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5, rx=3)
        out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=INK, bold=True)
        return out

    data = [1, 0, 1, 1, 0]     # п'ять біт даних (умовна літера)
    cw, ch = 40, 34

    # ── Щабель 1: Ґаусс-Вебер 1834 — п'ять двійкових елементів ──
    y1 = 62
    parts.append(text(30, y1 - 20, "Ґаусс і Вебер, 1834: літера = 5 двійкових елементів",
                      size=13.5, bold=True, anchor="start"))
    x = 30
    for v in data:
        parts.append(dcell(x, y1, cw, ch, v))
        x += cw + 6
    parts.append(text(x + 96, y1 + ch / 2 + 5, "2⁵ = 32 комбінації", size=12.5,
                      color=MUTED, anchor="middle"))

    # ── Щабель 2: код Бодо 1876 — ті самі 5 біт, тепер машинні ──
    y2 = 176
    parts.append(text(30, y2 - 20, "Код Бодо, 1876: ті самі 5 біт — але набирає й друкує машина",
                      size=13.5, bold=True, anchor="start"))
    x = 30
    for i, v in enumerate(data):
        parts.append(dcell(x, y2, cw, ch, v))
        parts.append(text(x + cw / 2, y2 + ch + 15, "b%d" % i, size=10, color=MUTED))
        x += cw + 6
    parts.append(mtext(x + 118, y2 + ch / 2 - 4, ["фіксована довжина →", "приймач лише рахує позиції"],
                       size=11, color=MUTED, anchor="middle"))

    # ── Щабель 3: старт-стопний кадр телетайпа ──
    y3 = 300
    parts.append(text(30, y3 - 20, "Старт-стопний кадр телетайпа (поч. XX ст.): без спільного такту",
                      size=13.5, bold=True, anchor="start"))
    x = 30
    # спокій зліва
    parts.append(labelbox(x, y3, 52, ch, "спокій", IDLE, "#9aa3ac", size=10))
    parts.append(text(x + 26, y3 + ch + 14, "mark", size=9, color=MUTED))
    x += 52 + 4
    # старт
    parts.append(labelbox(x, y3, 46, ch, "старт", "#fdecea", STARTC, size=10.5))
    parts.append(text(x + 23, y3 + ch + 14, "space", size=9, color=STARTC))
    x += 46 + 4
    # 5 біт даних
    for i, v in enumerate(data):
        parts.append(dcell(x, y3, 34, ch, v, size=12))
        x += 34 + 3
    # стоп
    x += 1
    parts.append(labelbox(x, y3, 44, ch, "стоп", "#eaf0fd", STOPC, size=10.5))
    parts.append(text(x + 22, y3 + ch + 14, "mark", size=9, color=STOPC))
    x += 44 + 4
    parts.append(labelbox(x, y3, 52, ch, "спокій", IDLE, "#9aa3ac", size=10))

    # дужка «5 біт даних» під групою
    d0 = 30 + 52 + 4 + 46 + 4
    d1 = d0 + 5 * 34 + 4 * 3
    parts.append(line(d0, y3 + ch + 22, d1, y3 + ch + 22, color=BITON, sw=1.4))
    parts.append(text((d0 + d1) / 2, y3 + ch + 38, "5 біт даних", size=11, color=BITON, anchor="middle"))

    # ── Нижня плашка: те саме дожило до UART ──
    note, nw, nh = textbox(W / 2, H - 26,
        "У UART — той самий кадр: старт · біти даних · стоп. Змінилося лише число бітів даних (5 → 8);\n"
        "стартовий біт і досі синхронізує приймача на кожному символі, без окремого дроту такту.",
        size=11.5, fill="#fff7e6", stroke="#d99a00")
    parts.append(note)

    render(os.path.join(OUT, 'hist-frame.svg'), W, H, *parts)


if __name__ == '__main__':
    fig_space_time()
    fig_timing()
    fig_roundtrip()
    fig_hist_frame()
    print("figs done ->", OUT)
