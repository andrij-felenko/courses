# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── stack: пиріг органічних шарів, де електрон і дірка зустрічаються й гаснуть фотоном ──
# Ідея: один піксель OLED — це бутерброд тонких органічних плівок між двома
# електродами; струм заганяє дірки знизу й електрони згори, вони зустрічаються в
# середньому шарі й, об'єднавшись, віддають енергію світлом. Самосвітний — без лампи.
def fig_stack():
    W, H = 760, 430
    p = []
    lx, lw = 250, 300            # колонка шарів
    layers = [                   # (назва, висота, заливка, колір тексту)
        ("катод (метал, дзеркало)", 30, "#cfd4da", INK),
        ("шар переносу електронів", 26, "#eaf0fd", INK),
        ("випромінювальний шар", 44, "#dff0e2", INK),
        ("шар переносу дірок", 26, "#fdecea", INK),
        ("прозорий анод (ITO)", 28, "#e8eef3", INK),
        ("скло / підкладка", 26, "#f4f6f8", MUTED),
    ]
    y = 70
    ys = {}
    for name, h, fill, col in layers:
        p.append(rect(lx, y, lw, h, fill=fill, stroke=LINE, sw=1.3, rx=0))
        p.append(text(lx + lw / 2, y + h / 2 + 4.5, name, size=13, color=col))
        ys[name] = (y, h)
        y += h
    bottom = y

    # електрод-мітки і живлення
    cy0, ch0 = ys["катод (метал, дзеркало)"]
    ay0, ah0 = ys["прозорий анод (ITO)"]
    p.append(minus(lx - 26, cy0 + ch0 / 2, r=11))
    p.append(plus(lx - 26, ay0 + ah0 / 2, r=11))

    # носії заряду рухаються назустріч у випромінювальний шар
    ey0, eh0 = ys["випромінювальний шар"]
    emid = ey0 + eh0 / 2
    p.append(circle(lx + 70, cy0 + ch0 + 6, 7, fill="#eaf0fd", stroke=NEG, sw=1.6))
    p.append(text(lx + 70, cy0 + ch0 + 9.5, "e", size=9, color=NEG, bold=True))
    p.append(arrow(lx + 70, cy0 + ch0 + 16, lx + 70, emid - 8, color=NEG, sw=1.6))
    p.append(circle(lx + lw - 70, ay0 - 6, 7, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(lx + lw - 70, ay0 - 3, "h", size=9, color=POS, bold=True))
    p.append(arrow(lx + lw - 70, ay0 - 14, lx + lw - 70, emid + 8, color=POS, sw=1.6))

    # зустріч → фотон
    import math
    p.append(circle(lx + lw / 2, emid, 8, fill="#fff7cc", stroke="#d99a00", sw=1.8))
    for a in range(0, 360, 45):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        p.append(line(lx + lw / 2 + dx * 11, emid + dy * 11,
                      lx + lw / 2 + dx * 19, emid + dy * 19, color="#d99a00", sw=1.6))
    p.append(text(lx + lw / 2, emid - 26, "e + h → фотон", size=12, color="#7a5a00", bold=True))

    # світло виходить крізь прозорий анод і скло вниз (до глядача)
    p.append(arrow(lx + lw / 2, bottom + 6, lx + lw / 2, bottom + 40, color="#d99a00", sw=2.2))
    p.append(text(lx + lw / 2, bottom + 56, "світло до ока", size=12, color="#7a5a00", italic=True))

    # підписи з боків
    tb, tw, th = textbox(120, 150, "струм\nзганяє\nносії", size=12, color=NEG, fill="#f7f9ff", stroke=NEG)
    p.append(tb)
    tb2, _, _ = textbox(640, 150, "чорний =\nнема струму\n= нема світла", size=12, color=INK, fill=FILL, stroke=LINE)
    p.append(tb2)

    render(os.path.join(OUT, "stack.svg"), W, H, *p,
           title="Один піксель OLED: органічний бутерброд, що сам родить світло")


# ── drive: PMOLED світить рядок за рядком сплесками; AMOLED тримає піксель транзистором ──
# Ідея: дві геть різні схеми керування матрицею. Пасивна (PMOLED) має лише
# рядки й стовпці — світить по одному рядку за раз короткими яскравими сплесками.
# Активна (AMOLED) дає кожному пікселю свій транзистор і конденсатор, що тримає
# піксель увімкненим увесь кадр на малому струмі.
def fig_drive():
    W, H = 820, 440
    p = []

    # ── ліва панель: PMOLED ──
    p.append(text(200, 60, "PMOLED — пасивна матриця", size=15, color=INK, bold=True))
    gx, gy, cell = 80, 90, 46
    # сітка 4×4
    for r in range(4):
        for c in range(4):
            on = (r == 1)                      # активний лише один рядок за раз
            fill = "#fff2b0" if on else "#fbfbfb"
            p.append(rect(gx + c * cell, gy + r * cell, cell - 6, cell - 6,
                          fill=fill, stroke=LINE, sw=1.1, rx=0))
    # підсвічений рядок — сплеск
    p.append(text(gx - 14, gy + 1 * cell + (cell - 6) / 2 + 4, "→", size=18, color=POS, bold=True, anchor="end"))
    p.append(text(200, gy + 4 * cell + 22, "горить ОДИН рядок за раз,", size=12, color=INK))
    p.append(text(200, gy + 4 * cell + 40, "яскравим сплеском (15–20 В)", size=12, color=INK))
    tb, _, _ = textbox(200, gy + 4 * cell + 74, "темно більшу частину кадру →\nщоб бути видним, б'є струмом", size=11, color=MUTED, fill=FILL, stroke=LINE)
    p.append(tb)

    # ── розділювач ──
    p.append(line(W / 2, 75, W / 2, H - 30, color=MUTED, sw=1.2, dash="5 5"))

    # ── права панель: AMOLED ──
    p.append(text(620, 60, "AMOLED — активна матриця", size=15, color=INK, bold=True))
    gx2 = 500
    for r in range(4):
        for c in range(4):
            p.append(rect(gx2 + c * cell, gy + r * cell, cell - 6, cell - 6,
                          fill="#dff0e2", stroke=LINE, sw=1.1, rx=0))    # усі світять рівно
    p.append(text(620, gy + 4 * cell + 22, "КОЖЕН піксель світить увесь кадр,", size=12, color=INK))
    p.append(text(620, gy + 4 * cell + 40, "рівним струмом (3–5 В)", size=12, color=INK))

    # вкладка: що в комірці AMOLED — транзистор + конденсатор + OLED
    bx, by, bw, bh = 520, gy + 4 * cell + 60, 200, 34
    p.append(rect(bx, by, bw, bh, fill="#f7f9ff", stroke=NEG, sw=1.3, rx=6))
    p.append(text(bx + bw / 2, by + bh / 2 + 4, "комірка = транзистор + Cтрим + OLED", size=10.5, color=NEG))

    render(os.path.join(OUT, "drive.svg"), W, H, *p,
           title="Дві схеми керування матрицею OLED: сплеск проти утримання")


# ── burnin: однакові значення, різний знос — статичний напис лишає привид ──
# Ідея: органіка деградує від накопиченого заряду; пікселі, що горіли довше й
# яскравіше (статичний логотип/рамка), тьмяніють відносно сусідів. Подаси потім
# рівне сіре поле — а на ньому проступає темніший слід вигорілих пікселів.
def fig_burnin():
    W, H = 760, 330
    p = []
    # ліворуч: що показували довго
    sx, sy, sw, sh = 70, 80, 280, 180
    p.append(text(sx + sw / 2, 62, "горіло місяцями", size=13, color=INK, bold=True))
    p.append(rect(sx, sy, sw, sh, fill="#111317", stroke=LINE, sw=1.4, rx=8))
    # яскравий статичний напис
    p.append(rect(sx + 24, sy + 24, sw - 48, 40, fill="#ffffff", stroke="none", sw=0, rx=4))
    p.append(text(sx + sw / 2, sy + 50, "STATUS", size=20, color="#111317", bold=True))
    # рухомий вміст (тьмяний — змінювався, тож зносився рівномірно)
    p.append(text(sx + sw / 2, sy + 120, "(решта — мінлива)", size=12, color="#6a7", italic=True))

    # стрілка часу
    p.append(arrow(sx + sw + 20, H / 2, sx + sw + 80, H / 2, color=MUTED, sw=2))
    p.append(text(sx + sw + 50, H / 2 - 12, "час", size=11, color=MUTED, italic=True))

    # праворуч: подали рівне сіре — проступає привид
    bx, by = 410, 80
    p.append(text(bx + sw / 2, 62, "потім — рівне сіре поле", size=13, color=INK, bold=True))
    p.append(rect(bx, by, sw, sh, fill="#6f747b", stroke=LINE, sw=1.4, rx=8))
    # вигорілий слід — темніша смуга там, де було яскраво
    p.append(rect(bx + 24, by + 24, sw - 48, 40, fill="#5b6066", stroke="none", sw=0, rx=4))
    p.append(text(bx + sw / 2, by + 50, "STATUS", size=20, color="#7d828a", bold=True))
    tb, _, _ = textbox(bx + sw / 2, by + sh + 34, "привид: ці пікселі вигоріли\nдужче за сусідів", size=11, color=INK, fill=FILL, stroke=LINE)
    p.append(tb)

    render(os.path.join(OUT, "burnin.svg"), W, H, *p,
           title="Вигоряння: нерівномірний знос лишає слід статичної картинки")


# ── pages: відеопам'ять SSD1306 — байт = вертикальний стовпчик із 8 пікселів ──
# Ідея: пам'ять монохромного OLED-контролера складена не рядками, а сторінками.
# Екран 128×64 — це 8 сторінок по 8 пікселів заввишки; один байт у сторінці задає
# вертикальний зріз із 8 пікселів (кожен біт — свій піксель), бо так зручно драйверам стовпців.
def fig_pages():
    W, H = 820, 380
    p = []
    # ── сторінки екрана ──
    px, pw, ph = 90, 380, 26
    py = 80
    for i in range(8):
        fill = "#f0f4f7" if i % 2 == 0 else "#fbfbfb"
        p.append(rect(px, py + i * ph, pw, ph, fill=fill, stroke=MUTED, sw=1.0, rx=0))
        p.append(text(px - 10, py + i * ph + ph / 2 + 4, "стор.%d" % i, size=10, color=MUTED, anchor="end"))
    p.append(text(px + pw / 2, py - 12, "128 стовпців →", size=10, color=MUTED))
    # виділений один стовпець у сторінці 2
    p.append(rect(px + 188, py + 2 * ph, 6, ph, fill="#dff0e2", stroke=FIELD, sw=1.8, rx=0))

    # ── вкладка: розкриваємо один байт-стовпець у 8 біт ──
    bx, by, bs = 620, 96, 24
    bits = [1, 1, 0, 1, 0, 0, 1, 0]
    p.append(text(bx + bs / 2, by - 14, "1 байт = 1 стовпець", size=11, color=INK, bold=True))
    for i, b in enumerate(bits):
        fill = INK if b else BG
        p.append(rect(bx, by + i * bs, bs, bs, fill=fill, stroke=INK, sw=1.1, rx=0))
        p.append(text(bx - 8, by + i * bs + bs / 2 + 4, "b%d" % i, size=9, color=MUTED, anchor="end"))
        p.append(text(bx + bs + 8, by + i * bs + bs / 2 + 4, str(b), size=10,
                      color=INK if b else MUTED, anchor="start"))
    p.append(text(bx + bs / 2, by + 8 * bs + 18, "8 пікселів", size=10, color=MUTED))
    p.append(text(bx + bs / 2, by + 8 * bs + 32, "по вертикалі", size=10, color=MUTED))

    # стрілка від виділеного стовпця до розкладки байта
    p.append(line(px + 200, py + 2 * ph + ph / 2, bx - 30, by + 4 * bs,
                  color=FIELD, sw=1.6, dash="4 3"))
    p.append(text(W / 2, H - 18, "8 сторінок × 128 стовпців = 1024 байти (1 КБ). Один піксель не змінити окремо — чіпаєш цілий байт.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pages.svg"), W, H, *p,
           title="Сторінкова відеопам'ять: байт — це вертикальний стовпчик із 8 пікселів")


if __name__ == "__main__":
    fig_stack()
    fig_drive()
    fig_burnin()
    fig_pages()
    print("OK figs")
