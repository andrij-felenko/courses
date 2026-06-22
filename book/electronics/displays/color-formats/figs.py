# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0392b"
GRN = "#27ae60"
BLU = "#2457d6"


# ── direct-indexed: два способи прочитати число пікселя ───────────────────────
# Ідея: те саме число вгорі читається як готовий RGB (біти-яскравості),
# а внизу — як НОМЕР рядка в окремій таблиці кольорів.

def fig_direct_indexed():
    W, H = 720, 360
    p = []

    # ── верх: прямий колір ──
    p.append(text(40, 44, "Прямий: біти комірки — це самі R, G, B",
                  size=13, color=INK, anchor="start", bold=True))
    cx, cy, cw = 60, 60, 150
    # комірка-число, поділена на три поля
    fields = [("R", RED, "#fdecea"), ("G", GRN, "#eafaf0"), ("B", BLU, "#eaf0fd")]
    fx = cx
    for lab, col, fill in fields:
        p.append(rect(fx, cy, cw / 3, 40, fill=fill, stroke=col, sw=1.8, rx=0))
        p.append(text(fx + cw / 6, cy + 26, lab, size=15, color=col, bold=True))
        fx += cw / 3
    # стрілка до зразка кольору
    p.append(arrow(cx + cw + 12, cy + 20, cx + cw + 70, cy + 20, color=INK, sw=1.8))
    p.append(rect(cx + cw + 78, cy - 2, 64, 44, fill="#b06a2e", stroke=INK, sw=1.5))
    p.append(text(cx + cw + 78 + 32, cy + 60, "колір просто", size=11, color=MUTED))

    # ── низ: індексований ──
    p.append(line(40, 150, W - 40, 150, color="#dddddd", sw=1.2))
    p.append(text(40, 184, "Індексований: число — це НОМЕР рядка в таблиці кольорів",
                  size=13, color=INK, anchor="start", bold=True))
    ix, iy = 60, 206
    # комірка з числом 5
    p.append(rect(ix, iy, 56, 40, fill="#f6efd6", stroke=INK, sw=1.8))
    p.append(text(ix + 28, iy + 26, "5", size=17, color=INK, bold=True))
    p.append(text(ix + 28, iy + 60, "індекс", size=10, color=MUTED))

    # палітра — 8 рядків, 5-й виділено
    px, py, rowh, roww = 300, 168, 22, 150
    swatches = ["#202020", "#8e44ad", "#16a085", "#e67e22",
                "#2980b9", "#c0392b", "#f1c40f", "#7f8c8d"]
    p.append(text(px + roww / 2, py - 8, "таблиця кольорів (палітра)", size=11, color=MUTED, bold=True))
    for i, sw in enumerate(swatches):
        ry = py + i * rowh
        hot = (i == 5)
        p.append(rect(px, ry, 30, rowh, fill="#f4f6f8",
                      stroke=POS if hot else LINE, sw=2 if hot else 1.0, rx=0))
        p.append(text(px + 15, ry + 15, str(i), size=11,
                      color=POS if hot else INK, bold=hot))
        p.append(rect(px + 30, ry, roww - 30, rowh, fill=sw,
                      stroke=POS if hot else LINE, sw=2 if hot else 1.0, rx=0))
    # стрілка від індексу до 5-го рядка
    p.append(arrow(ix + 60, iy + 20, px - 6, py + 5 * rowh + rowh / 2, color=POS, sw=2))
    # стрілка від 5-го рядка до зразка
    p.append(arrow(px + roww + 6, py + 5 * rowh + rowh / 2,
                   px + roww + 60, py + 5 * rowh + rowh / 2, color=INK, sw=1.8))
    p.append(rect(px + roww + 68, py + 5 * rowh - 2, 60, rowh + 6, fill="#c0392b", stroke=INK, sw=1.5))
    p.append(text(px + roww + 68 + 30, py + 8 * rowh + 4, "колір — через довідник", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "direct-indexed.svg"), W, H, *p,
           title="Те саме число — два прочитання")


# ── rgb565: розкладка 16 біт на 5-6-5 ────────────────────────────────────────
# Ідея: показати 16 клітинок-бітів, поділених на R(5) G(6) B(5);
# зеленому дістається зайвий, 6-й біт.

def fig_rgb565():
    W, H = 720, 280
    p = []
    bx, by = 40, 90
    bw, bh = (W - 80) / 16.0, 50
    groups = [(5, "R · 5 біт", RED, "#fdecea"),
              (6, "G · 6 біт", GRN, "#eafaf0"),
              (5, "B · 5 біт", BLU, "#eaf0fd")]
    p.append(text(W / 2, 56, "Один піксель = 16 біт = 2 байти", size=13, color=INK, bold=True))
    x = bx
    bit = 15
    for n, lab, col, fill in groups:
        gx0 = x
        for _ in range(n):
            p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=1.6, rx=0))
            p.append(text(x + bw / 2, by + bh / 2 + 5, str(bit), size=11, color=col))
            bit -= 1
            x += bw
        # підпис групи під нею
        gw = n * bw
        p.append(text(gx0 + gw / 2, by + bh + 26, lab, size=13, color=col, bold=True))
    # виділити зайвий, 6-й біт зеленого (перша клітинка G-групи)
    extra_x = bx + 5 * bw
    p.append(rect(extra_x, by - 4, bw, bh + 8, fill="none", stroke=GRN, sw=2.6, rx=3))
    p.append(arrow(extra_x + bw / 2, by - 28, extra_x + bw / 2, by - 8, color=GRN, sw=2))
    p.append(text(extra_x + bw / 2, by - 36, "зайвий біт — зеленому", size=12, color=GRN, bold=True))

    p.append(text(W / 2, by + bh + 64,
                  "16 не ділиться на 3 порівну; зайвий біт дають зеленому — до нього око найприскіпливіше",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "rgb565.svg"), W, H, *p)


# ── bpp: глибина кольору ↔ розмір кадру ──────────────────────────────────────
# Ідея: три формати; що глибший колір, то більший стовпчик пам'яті,
# RGB565 — золота середина.

def fig_bpp():
    W, H = 720, 320
    p = []
    base = 250
    fmts = [
        ("RGB332", 1, "256 кольорів", "#bbbbbb"),
        ("RGB565", 2, "65 536 кольорів", FIELD),
        ("RGB888", 3, "16.7 млн кольорів", "#8a5fb0"),
    ]
    bx = 110
    bw = 120
    gap = 90
    unit = 52          # px на 1 байт/піксель
    for i, (name, bpp, cols, col) in enumerate(fmts):
        x = bx + i * (bw + gap)
        h = bpp * unit
        p.append(rect(x, base - h, bw, h, fill=col, stroke=INK, sw=1.6, rx=4))
        p.append(text(x + bw / 2, base + 22, name, size=13, color=INK, bold=True))
        p.append(text(x + bw / 2, base + 42, "%d байт/піксель" % bpp, size=11, color=MUTED))
        p.append(text(x + bw / 2, base - h - 12, cols, size=11, color=INK))
    # підкреслити RGB565
    xm = bx + 1 * (bw + gap)
    p.append(text(xm + bw / 2, base - 2 * unit - 36, "золота середина",
                  size=12, color=FIELD, bold=True))
    # вісь-підпис
    p.append(line(bx - 26, base, W - 60, base, color=INK, sw=1.4))
    p.append(text(bx - 30, base - 2 * unit, "пам'ять", size=11, color=MUTED, anchor="end"))
    p.append(text(W / 2, base + 74,
                  "Та сама картинка: глибший колір коштує пропорційно більше пам'яті кадру",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "bpp.svg"), W, H, *p,
           title="Кольори проти пам'яті: вибір глибини")


# ── palette: малий індекс веде до кольору в палітрі ──────────────────────────
# Ідея: великий кадр з однакових індексів + крихітна палітра збоку;
# підміна палітри = миттєве перефарбування.

def fig_palette():
    W, H = 720, 320
    p = []
    # кадр — сітка індексів
    gx, gy = 60, 80
    cell = 30
    cols, rows = 8, 6
    grid = [
        [0,0,1,1,1,1,0,0],
        [0,1,2,2,2,2,1,0],
        [1,2,3,3,3,3,2,1],
        [1,2,3,3,3,3,2,1],
        [0,1,2,2,2,2,1,0],
        [0,0,1,1,1,1,0,0],
    ]
    pal = ["#1f2a44", "#3a6ea5", "#7fb2e5", "#eaf2fb"]
    p.append(text(gx + cols * cell / 2, gy - 12, "кадр: лише індекси (1 байт/піксель)",
                  size=11, color=MUTED, bold=True))
    for r in range(rows):
        for c in range(cols):
            idx = grid[r][c]
            x, y = gx + c * cell, gy + r * cell
            p.append(rect(x, y, cell, cell, fill="#fbfbfb", stroke="#cccccc", sw=0.8, rx=0))
            p.append(text(x + cell / 2, y + cell / 2 + 4, str(idx), size=11, color=INK))

    # палітра
    px, py = 470, 110
    rowh = 30
    p.append(text(px + 75, py - 12, "палітра (лічені байти)", size=11, color=MUTED, bold=True))
    for i, sw in enumerate(pal):
        ry = py + i * rowh
        p.append(rect(px, ry, 28, rowh, fill="#f4f6f8", stroke=LINE, sw=1.0, rx=0))
        p.append(text(px + 14, ry + 19, str(i), size=11, color=INK, bold=True))
        p.append(rect(px + 28, ry, 120, rowh, fill=sw, stroke=LINE, sw=1.0, rx=0))
        p.append(text(px + 28 + 60, ry + 19, "RGB888", size=10,
                      color="#ffffff" if i < 2 else INK))
    p.append(arrow(gx + cols * cell + 8, gy + rows * cell / 2,
                   px - 8, py + 2 * rowh, color=POS, sw=1.8))
    p.append(text((gx + cols * cell + px) / 2, gy + rows * cell / 2 - 8,
                  "число → рядок", size=10, color=POS))
    p.append(text(W / 2, H - 22,
                  "Підмінив таблицю — і вся картинка перефарбувалася, жодного пікселя кадру не чіпаючи",
                  size=11, color=FIELD, italic=True, bold=True))
    render(os.path.join(OUT, "palette.svg"), W, H, *p,
           title="Індексований колір: кадр + палітра")


# ── alpha: напівпрозоре джерело над тлом ─────────────────────────────────────
# Ідея: src (α) над dst → змішаний out; на екран іде вже готовий колір.

def fig_alpha():
    W, H = 720, 300
    p = []
    y = 130
    bw, bh = 120, 90
    # dst
    dx = 70
    p.append(rect(dx, y, bw, bh, fill="#2457d6", stroke=INK, sw=1.5))
    p.append(text(dx + bw / 2, y + bh + 22, "тло (dst)", size=12, color=INK, bold=True))
    p.append(text(dx + bw / 2, y - 10, "те, що під ним", size=10, color=MUTED))
    # +
    p.append(text(dx + bw + 35, y + bh / 2 + 8, "+", size=26, color=INK, bold=True))
    # src напівпрозорий
    sx = dx + bw + 70
    p.append(rect(sx, y, bw, bh, fill="#c0392b", stroke=INK, sw=1.5))
    # штрихування «напівпрозорості»
    for k in range(0, int(bw + bh), 12):
        x1 = sx + max(0, k - bh); y1 = y + min(k, bh)
        x2 = sx + min(k, bw); y2 = y + max(0, k - bw)
        p.append(line(x1, y1, x2, y2, color="#ffffff", sw=0.8))
    p.append(text(sx + bw / 2, y + bh + 22, "джерело (src), α", size=12, color=INK, bold=True))
    p.append(text(sx + bw / 2, y - 10, "напівпрозоре", size=10, color=MUTED))
    # = arrow
    p.append(arrow(sx + bw + 12, y + bh / 2, sx + bw + 64, y + bh / 2, color=INK, sw=2))
    # out
    ox = sx + bw + 72
    p.append(rect(ox, y, bw, bh, fill="#6e1d7a", stroke=INK, sw=1.5))
    p.append(text(ox + bw / 2, y + bh + 22, "готовий колір (out)", size=12, color=INK, bold=True))
    p.append(text(ox + bw / 2, y - 10, "іде на екран", size=10, color=MUTED))

    p.append(text(W / 2, 50, "out = src·α + dst·(1 − α)", size=15, color=INK, bold=True))
    p.append(text(W / 2, H - 22,
                  "Скло не буває напівпрозорим — у буфер екрана лягає вже ЗМІШАНИЙ колір",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "alpha.svg"), W, H, *p)


# ── byte-order: переплутані байти + смуги від утиску глибини ──────────────────
# Ідея: ліворуч — той самий піксель у двох порядках байтів дає різний колір;
# праворуч — гладкий градієнт 24→16 біт розпадається на смуги.

def fig_byte_order():
    W, H = 720, 320
    p = []
    # ── ліво: порядок байтів ──
    p.append(text(40, 50, "Порядок байтів", size=13, color=INK, anchor="start", bold=True))
    lx, ly = 50, 80
    # два байти
    def two_bytes(x, y, hi, lo, hi_col, lo_col, label, swatch):
        out = [rect(x, y, 70, 34, fill=hi_col, stroke=INK, sw=1.4, rx=0),
               rect(x + 70, y, 70, 34, fill=lo_col, stroke=INK, sw=1.4, rx=0),
               text(x + 35, y + 22, hi, size=11, color=INK),
               text(x + 105, y + 22, lo, size=11, color=INK),
               text(x + 70, y - 8, label, size=11, color=MUTED, bold=True),
               rect(x + 150, y - 2, 44, 38, fill=swatch, stroke=INK, sw=1.4)]
        return out
    p += two_bytes(lx, ly, "старший", "молодший", "#f3dede", "#dde8f3",
                   "правильно", "#b03030")
    p += two_bytes(lx, ly + 80, "молодший", "старший", "#dde8f3", "#f3dede",
                   "переплутано", "#3050b0")
    p.append(text(lx + 97, ly + 156, "червоне стало синім", size=11, color=POS, bold=True))
    p.append(text(lx + 97, ly + 176, "(той самий клас, що RGB↔BGR)", size=10, color=MUTED))

    # ── право: банінг ──
    rx0 = 430
    p.append(text(rx0, 50, "Утиск глибини → смуги", size=13, color=INK, anchor="start", bold=True))
    # гладка смуга (24 біт)
    gy = 90
    n = 64
    bw = 240.0 / n
    for i in range(n):
        t = i / (n - 1.0)
        v = int(30 + t * 210)
        p.append(rect(rx0 + i * bw, gy, bw + 0.6, 50, fill="#%02x%02x%02x" % (v, v, v),
                      stroke="none", sw=0))
    p.append(text(rx0 + 120, gy + 70, "24 біти: плавно", size=11, color=MUTED))
    # ступінчаста смуга (16 біт) — мало рівнів
    gy2 = 180
    steps = 6
    sw = 240.0 / steps
    for i in range(steps):
        t = i / (steps - 1.0)
        v = int(30 + t * 210)
        p.append(rect(rx0 + i * sw, gy2, sw, 50, fill="#%02x%02x%02x" % (v, v, v),
                      stroke="#ffffff", sw=1.0))
    p.append(text(rx0 + 120, gy2 + 70, "16 біт: видимі смуги (banding)", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "byte-order.svg"), W, H, *p,
           title="Дві приземлені пастки формату")


if __name__ == "__main__":
    fig_direct_indexed()
    fig_rgb565()
    fig_bpp()
    fig_palette()
    fig_alpha()
    fig_byte_order()
    print("OK: figures written to", OUT)
