# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Спільні кольори клітинок (поверх палітри svgkit)
GRID   = "#dfe3e8"   # лінії сітки пікселів
ONPIX  = "#1f2937"   # засвічений піксель (темний)
GREYPX = "#9aa4b2"   # півтон (антиаліас)
GHOST  = "#cdd5df"   # «ідеальна» геометрія поверх сітки


def grid(ox, oy, cols, rows, cell, stroke=GRID, sw=1.0):
    """Порожня сітка cols×rows від (ox,oy), клітинка cell px."""
    out = []
    for c in range(cols):
        for r in range(rows):
            out.append(rect(ox + c * cell, oy + r * cell, cell, cell,
                            fill="none", stroke=stroke, sw=sw, rx=0))
    return out


def cell_fill(ox, oy, c, r, cell, color=ONPIX):
    return rect(ox + c * cell + 1, oy + r * cell + 1, cell - 2, cell - 2,
                fill=color, stroke="none", sw=0, rx=0)


def bres(x0, y0, x1, y1):
    """Канонічний цілочисловий Брезенхем — повертає список клітинок (x,y).
    Завжди завершується (крок по знаку, перевірка точного кінця)."""
    pts = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        pts.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x += sx
        if e2 <= dx:
            err += dx; y += sy
    return pts


# ── rasterization: ідеальна форма проти обраних пікселів ──────────────────────
# Ідея: ліворуч гладка тонка лінія; праворуч її растр — сходинки клітинок, бо
# косу лінію інакше на квадратну сітку не покласти.

def fig_rasterization():
    W, H = 720, 330
    cell = 26
    cols, rows = 9, 7
    p = []

    # ── ліворуч: ідеальна лінія над блідою сіткою ──
    ox1, oy1 = 60, 60
    p += grid(ox1, oy1, cols, rows, cell, stroke="#eceff3")
    p.append(line(ox1 + 0.3 * cell, oy1 + (rows - 0.4) * cell,
                  ox1 + (cols - 0.3) * cell, oy1 + 0.4 * cell, color=INK, sw=2.6))
    p.append(text(ox1 + cols * cell / 2, oy1 + rows * cell + 28,
                  "ідеальна лінія — нескінченно тонка", size=12, color=MUTED))

    # ── праворуч: та сама лінія, растеризована (Брезенхем) ──
    ox2, oy2 = 410, 60
    p += grid(ox2, oy2, cols, rows, cell)
    # цілочисловий хід по довшій (X) осі
    for (x, y) in bres(0, rows - 1, cols - 1, 0):
        p.append(cell_fill(ox2, oy2, x, y, cell))
    # бліда «ідеальна» лінія поверх — видно сходинки
    p.append(line(ox2 + 0.5 * cell, oy2 + (rows - 0.5) * cell,
                  ox2 + (cols - 0.5) * cell, oy2 + 0.5 * cell, color=POS, sw=1.6))
    p.append(text(ox2 + cols * cell / 2, oy2 + rows * cell + 28,
                  "растр — клітинки складаються у сходинки", size=12, color=MUTED))

    render(os.path.join(OUT, "rasterization.svg"), W, H, *p,
           title="Растеризація: неперервну форму вкладають у дискретну сітку")


# ── rect-spans: заливка спанами проти заливки по пікселю ──────────────────────
# Ідея: один прямокутник двічі; ліворуч рядки-смуги (мало операцій), праворуч
# окремі клітинки (багато операцій).

def fig_rect_spans():
    W, H = 720, 320
    cell = 26
    cols, rows = 8, 6
    p = []

    # ── ліворуч: спани (цілі рядки) ──
    ox1, oy1 = 60, 64
    p += grid(ox1, oy1, cols, rows, cell, stroke="#eceff3")
    for r in range(rows):
        p.append(rect(ox1 + 1, oy1 + r * cell + 3, cols * cell - 2, cell - 6,
                      fill="#dbe6ff", stroke=NEG, sw=1.6, rx=3))
        p.append(arrow(ox1 + 6, oy1 + r * cell + cell / 2,
                       ox1 + cols * cell - 6, oy1 + r * cell + cell / 2, color=NEG, sw=1.4))
    p.append(text(ox1 + cols * cell / 2, oy1 + rows * cell + 28,
                  "%d спанів — %d швидких операцій" % (rows, rows),
                  size=12, color=NEG, bold=True))

    # ── праворуч: окремі пікселі ──
    ox2, oy2 = 410, 64
    p += grid(ox2, oy2, cols, rows, cell)
    for r in range(rows):
        for c in range(cols):
            p.append(cell_fill(ox2, oy2, c, r, cell, color="#f2c9c4"))
    p.append(text(ox2 + cols * cell / 2, oy2 + rows * cell + 28,
                  "%d окремих set_pixel" % (cols * rows),
                  size=12, color=POS, bold=True))

    render(os.path.join(OUT, "rect-spans.svg"), W, H, *p,
           title="Прямокутник заливають рядками-спанами, а не по пікселю")


# ── line: крок по довшій осі + ціла похибка ───────────────────────────────────
# Ідея: показати растеризовану лінію, підписати, що крок іде по X (довша вісь),
# а зсув Y вирішує ціла похибка «наскільки лінія відійшла від рядка».

def fig_line():
    W, H = 720, 340
    cell = 30
    cols, rows = 13, 7
    ox, oy = 40, 64
    p = []
    p += grid(ox, oy, cols, rows, cell)

    # Брезенхем для пологої лінії (dx > dy): крокуємо по X
    x0, y0, x1, y1 = 0, 5, 12, 1
    for (x, y) in bres(x0, y0, x1, y1):
        p.append(cell_fill(ox, oy, x, y, cell))

    # ідеальна лінія поверх (центри кінцевих клітинок)
    p.append(line(ox + (x0 + 0.5) * cell, oy + (y0 + 0.5) * cell,
                  ox + (x1 + 0.5) * cell, oy + (y1 + 0.5) * cell, color=POS, sw=1.8))

    # підпис осей кроку
    p.append(arrow(ox, oy + rows * cell + 16, ox + cols * cell, oy + rows * cell + 16,
                   color=NEG, sw=1.6))
    p.append(text(ox + cols * cell / 2, oy + rows * cell + 36,
                  "крок по довшій осі X — рівно один піксель на крок",
                  size=12, color=NEG, bold=True, anchor="middle"))
    p.append(text(ox + (cols - 0.2) * cell, oy - 12,
                  "ідеальна лінія", size=11, color=POS, anchor="end"))
    p.append(text(ox + 2 * cell, oy - 12,
                  "зсув Y вирішує ціла похибка", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "line.svg"), W, H, *p,
           title="Лінія Брезенхема: крок по довшій осі, ціла похибка вирішує зсув")


# ── circle: один октант → вісім точок симетрією ───────────────────────────────
# Ідея: порахувати дугу однієї восьмої, решту дістати дзеркаленням координат.

def fig_circle():
    W, H = 720, 430
    cell = 22
    R = 7
    cols = rows = 2 * R + 1
    ox = W / 2 - R * cell        # сітка завширшки (2R+1)·cell
    oy = 48                       # під заголовком
    cx, cy = ox + R * cell, oy + R * cell
    p = []
    p += grid(ox, oy, cols, rows, cell, stroke="#eef1f4")

    # осі через центр
    p.append(line(ox, cy, ox + cols * cell, cy, color=GREYPX, sw=1.0, dash="4 4"))
    p.append(line(cx, oy, cx, oy + rows * cell, color=GREYPX, sw=1.0, dash="4 4"))
    # діагональ октанта
    p.append(line(cx, cy, cx + (R + 0.5) * cell, cy - (R + 0.5) * cell,
                  color=GREYPX, sw=1.0, dash="4 4"))

    def put(c, r, color):
        # координати в клітинках від центру (центр = R,R)
        p.append(cell_fill(ox, oy, R + c, R - r, cell, color=color))

    # midpoint circle: октант x∈[0..], y від R, поки y>=x
    x, y = 0, R
    d = 1 - R
    octant = []
    while x <= y:
        octant.append((x, y))
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1

    # порахований октант — темний; сім дзеркал — світліші
    for (x, y) in octant:
        sym = [(x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)]
        put(x, y, ONPIX)                       # сам октант
        for (sx, sy) in sym[1:]:
            put(sx, sy, GREYPX)                # дзеркала

    p.append(text(cx + (R + 0.3) * cell, cy - (R + 0.1) * cell,
                  "1/8 рахуємо", size=11, color=INK, anchor="start"))
    p.append(text(cx, oy + rows * cell + 26,
                  "одна обчислена точка октанта → вісім точок кола дзеркаленням",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "circle.svg"), W, H, *p,
           title="Коло: рахуємо один октант, тиражуємо симетрією на вісім")


# ── text: рядок як низка блітів гліфів зі зсувом курсора ───────────────────────
# Ідея: кожна літера — бітмап-гліф; малювання блітить їх підряд і посуває курсор;
# моноширинний крок сталий, пропорційний — свій на літеру.

def fig_text():
    W, H = 720, 320
    p = []

    # маленькі гліфи 5×7 для пари літер
    def glyph(ox, oy, rowsbits, cell, color=ONPIX):
        out = []
        for r, bits in enumerate(rowsbits):
            for c, b in enumerate(bits):
                if b == "1":
                    out.append(rect(ox + c * cell, oy + r * cell, cell, cell,
                                    fill=color, stroke="none", rx=0))
        return out

    GH = {
        "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
        "i": ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    }
    cell = 9

    # ── моноширинний рядок: однаковий крок ──
    y0 = 70
    p.append(text(40, y0 - 14, "моноширинний — крок однаковий", size=12,
                  color=INK, anchor="start", bold=True))
    step = 7 * cell
    x = 60
    for ch in "HiHi":
        p.append(rect(x - 4, y0, step, 7 * cell + 8, fill="none",
                      stroke="#dfe3e8", sw=1.0, rx=2))
        p += glyph(x, y0 + 4, GH[ch], cell)
        x += step
    # стрілки курсора
    cx = 60
    for _ in range(4):
        p.append(arrow(cx, y0 + 7 * cell + 22, cx + step - 6, y0 + 7 * cell + 22,
                       color=NEG, sw=1.4))
        cx += step
    p.append(text(60, y0 + 7 * cell + 40, "крок курсора сталий — «i» висить у порожнечі",
                  size=11, color=MUTED, anchor="start"))

    # ── пропорційний рядок: крок свій ──
    y1 = 210
    p.append(text(40, y1 - 14, "пропорційний — крок свій на літеру", size=12,
                  color=INK, anchor="start", bold=True))
    widths = {"H": 7, "i": 3}
    x = 60
    for ch in "HiHi":
        w = widths[ch] * cell
        p.append(rect(x - 2, y1, w + 4, 7 * cell + 8, fill="none",
                      stroke="#dfe3e8", sw=1.0, rx=2))
        p += glyph(x, y1 + 4, GH[ch], cell)
        p.append(arrow(x, y1 + 7 * cell + 22, x + w, y1 + 7 * cell + 22,
                       color=FIELD, sw=1.4))
        x += w + 4
    p.append(text(60, y1 + 7 * cell + 40, "вузьке «i» зсуває курсор менше — текст щільніший",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "text.svg"), W, H, *p,
           title="Текст: бліт гліфів підряд зі зсувом курсора")


# ── alias-clip: сходинки/згладжування + відсікання до вікна ───────────────────
# Ідея: ліворуч та сама коса лінія — ступінчаста й згладжена сірими крайовими;
# праворуч відсікання прямокутником вікна.

def fig_alias_clip():
    W, H = 720, 330
    cell = 26
    cols, rows = 8, 7
    p = []

    # ── ліворуч: аліас проти згладжування ──
    ox1, oy1 = 50, 60
    p += grid(ox1, oy1, cols, rows, cell, stroke="#eceff3")
    # ступінчаста (суцільні темні) — нижня половина клітинок ходу
    steps = bres(0, 6, 7, 0)
    for (x, y) in steps:
        p.append(cell_fill(ox1, oy1, x, y, cell, color=ONPIX))
        # сірий «сусід» зверху — натяк на згладжування
        if y - 1 >= 0:
            p.append(cell_fill(ox1, oy1, x, y - 1, cell, color="#c3cad4"))
    p.append(line(ox1 + 0.5 * cell, oy1 + (rows - 0.5) * cell,
                  ox1 + (cols - 0.5) * cell, oy1 + 0.5 * cell, color=POS, sw=1.4))
    p.append(text(ox1 + cols * cell / 2, oy1 + rows * cell + 26,
                  "темні + сірі краї = згладжування", size=12, color=MUTED))

    # ── праворуч: відсікання до вікна ──
    ox2, oy2 = 430, 60
    p += grid(ox2, oy2, cols, rows, cell, stroke="#eceff3")
    # вікно (видима ділянка)
    win = (1, 1, 5, 4)   # c0,r0,w,h у клітинках
    wc, wr, ww, wh = win
    p.append(rect(ox2 + wc * cell, oy2 + wr * cell, ww * cell, wh * cell,
                  fill="#eafaf0", stroke=FIELD, sw=2.0, rx=2))
    # лінія, що тягнеться за межі вікна
    lx0, ly0, lx1, ly1 = -0.3, 5.5, 7.3, 0.5
    # частина у вікні — суцільна, поза — пунктир (відрізане)
    p.append(line(ox2 + (wc) * cell, oy2 + 4.2 * cell,
                  ox2 + (wc + ww) * cell, oy2 + 1.6 * cell, color=INK, sw=2.4))
    p.append(line(ox2 + lx0 * cell, oy2 + ly0 * cell,
                  ox2 + wc * cell, oy2 + 4.2 * cell, color=GREYPX, sw=1.8, dash="5 4"))
    p.append(line(ox2 + (wc + ww) * cell, oy2 + 1.6 * cell,
                  ox2 + lx1 * cell, oy2 + ly1 * cell, color=GREYPX, sw=1.8, dash="5 4"))
    p.append(text(ox2 + (wc + ww / 2) * cell, oy2 + (wr + wh) * cell - 6,
                  "вікно", size=11, color=FIELD, bold=True))
    p.append(text(ox2 + cols * cell / 2, oy2 + rows * cell + 26,
                  "що за межами вікна — відрізають до малювання", size=12, color=MUTED))

    render(os.path.join(OUT, "alias-clip.svg"), W, H, *p,
           title="Згладжування країв і відсікання примітива до вікна")


if __name__ == "__main__":
    fig_rasterization()
    fig_rect_spans()
    fig_line()
    fig_circle()
    fig_text()
    fig_alias_clip()
    print("OK: figures written to", OUT)
