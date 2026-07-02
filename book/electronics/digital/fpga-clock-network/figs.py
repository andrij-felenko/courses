# -*- coding: utf-8 -*-
"""Фігури до статті «Тактова мережа FPGA» (book/electronics/digital/fpga-clock-network).
Чотири фігури:
  skew.svg    — проблема: такт звичайними проводами приходить у різний час → перегони
  htree.svg   — рішення: збалансоване H-дерево, однакова довжина шляху до кожного листка
  network.svg — ієрархія: вхідний пін → буфер → хребет → регіони → гілки до тригерів
  enable.svg  — правильно/неправильно: дозвіл такту (CE) проти врізання логіки в такт
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ─────────────────────────────────────────────────────────
def ff(x, y, w=52, h=44, label="FF", clk_side="bottom"):
    """Тригер-прямокутник із входом такту. Повертає (svg, dict-вузлів)."""
    out = [rect(x, y, w, h, fill="#ffffff", stroke=INK, sw=1.8, rx=4)]
    out.append(text(x + w / 2, y + h / 2 + 5, label, size=13, color=INK, bold=True))
    # клинець такту на лівому боці
    cy = y + h - 10
    out.append(line(x, cy - 5, x + 9, cy, color=INK, sw=1.6))
    out.append(line(x, cy + 5, x + 9, cy, color=INK, sw=1.6))
    nodes = {"clk": (x, cy), "left": (x, y + h / 2), "right": (x + w, y + h / 2),
             "top": (x + w / 2, y), "bot": (x + w / 2, y + h)}
    return "".join(out), nodes


def buf(cx, cy, r=15, label=None, color=FIELD):
    """Буфер-трикутник (підсилювач такту)."""
    out = ['<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="#eef7f0" stroke="%s" stroke-width="2"/>'
           % (cx - r, cy - r, cx + r, cy, cx - r, cy + r, color)]
    if label:
        out.append(text(cx - r - 6, cy + 4, label, size=11, color=color, bold=True, anchor="end"))
    return "".join(out), (cx - r, cy), (cx + r, cy)


# ════════════════════════════════════════════════════════════════════════════
# 1. skew.svg — той самий такт звичайними проводами приходить у різний час
# ════════════════════════════════════════════════════════════════════════════
def fig_skew():
    W, H = 680, 340
    f = []
    f.append(text(W / 2, 30, "Такт звичайними проводами: різна довжина → різний час приходу",
                  size=14, bold=True))

    # джерело такту ліворуч
    srcx, srcy = 70, 180
    f.append(circle(srcx, srcy, 16, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(srcx, srcy + 5, "clk", size=12, color=POS, bold=True))
    f.append(text(srcx, srcy + 40, "джерело", size=11, color=MUTED))

    # три тригери на різній «відстані» — з ламаними проводами різної довжини
    s1, n1 = ff(360, 90, label="A")
    s2, n2 = ff(430, 180, label="B")
    s3, n3 = ff(540, 270, label="C")
    f.append(s1); f.append(s2); f.append(s3)

    # проводи різної довжини (звивисті = довші), із «перемикачами» маршрутизації
    def wander(x0, y0, x1, y1, extra, col):
        # ламана з проміжними точками, щоб показати «гуляння» по загальній сітці
        pts = [(x0, y0)]
        midx = (x0 + x1) / 2
        pts.append((midx - extra, y0))
        pts.append((midx - extra, (y0 + y1) / 2))
        pts.append((midx + extra, (y0 + y1) / 2))
        pts.append((midx + extra, y1))
        pts.append((x1, y1))
        seg = []
        for i in range(len(pts) - 1):
            seg.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=col, sw=2.0))
        # маленькі квадратики-перемикачі на згинах
        for px, py in pts[1:-1]:
            seg.append(rect(px - 3, py - 3, 6, 6, fill="#ffffff", stroke=MUTED, sw=1.2, rx=1))
        return "".join(seg)

    f.append(wander(srcx + 16, srcy, n1["clk"][0], n1["clk"][1], 10, INK))
    f.append(wander(srcx + 16, srcy, n2["clk"][0], n2["clk"][1], 30, INK))
    f.append(wander(srcx + 16, srcy, n3["clk"][0], n3["clk"][1], 60, INK))

    # підписи різного часу приходу
    f.append(text(n1["right"][0] + 10, n1["right"][1] + 4, "такт о 0.5 нс", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(n2["right"][0] + 10, n2["right"][1] + 4, "такт о 1.4 нс", size=11, color=POS, anchor="start", bold=True))
    f.append(text(n3["right"][0] + 10, n3["right"][1] + 4, "такт о 2.9 нс", size=11, color=POS, anchor="start", bold=True))

    body, _, _ = textbox(W / 2, 316,
                         "Розбіг приходу (перекіс) з’їдає запас часу й ламає передачі між тригерами",
                         size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)
    render(os.path.join(IMG, "skew.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. htree.svg — збалансоване дерево: рівні шляхи до всіх листків
# ════════════════════════════════════════════════════════════════════════════
def fig_htree():
    W, H = 640, 440
    f = []
    f.append(text(W / 2, 30, "Збалансоване дерево такту: до кожного тригера — однакова довжина",
                  size=14, bold=True))

    cx, cy = W / 2, 235
    # корінь
    f.append(circle(cx, 70, 15, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx, 75, "clk", size=11, color=POS, bold=True))
    f.append(line(cx, 85, cx, cy, color=FIELD, sw=2.6))            # стовбур

    # рівень 1: горизонталь
    x1a, x1b = cx - 150, cx + 150
    f.append(line(x1a, cy, x1b, cy, color=FIELD, sw=2.6))
    # рівень 2: вертикалі
    for xx in (x1a, x1b):
        f.append(line(xx, cy - 90, xx, cy + 90, color=FIELD, sw=2.6))
        # буфери на розгалуженні
        f.append(circle(xx, cy, 4, fill=FIELD, stroke=FIELD))
    f.append(circle(cx, cy, 4, fill=FIELD, stroke=FIELD))

    # листки — 8 тригерів на кінцях гілок, усі на однаковій «глибині»
    leaf_y = [cy - 90, cy + 90]
    leaf_x = [x1a, x1b]
    tx = []
    for xx in leaf_x:
        for yy in leaf_y:
            # коротка гілка до тригера
            f.append(line(xx, yy, xx, yy + (18 if yy > cy else -18), color=FIELD, sw=2.2))
            ffy = yy + 20 if yy > cy else yy - 64
            s, n = ff(xx - 26, ffy, w=52, h=40, label="")
            f.append(s)
            f.append(text(xx, ffy + 24, "T", size=12, color=INK, bold=True))

    # підпис вузлів-буферів — збоку, не поверх ліній
    f.append(text(cx + 12, cy + 22, "у вузлах — буфери", size=10, color=FIELD, anchor="start"))
    body, _, _ = textbox(W / 2, 412,
                         "Однакова кількість «сходинок» і однакова довжина проводу → такт приходить усюди майже одночасно",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "htree.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. network.svg — ієрархія: пін → буфер → хребет → регіони → гілки
# ════════════════════════════════════════════════════════════════════════════
def fig_network():
    W, H = 700, 430
    f = []
    f.append(text(W / 2, 28, "Шлях такту через кристал: спеціальний пін → буфер → хребет → регіони",
                  size=14, bold=True))

    # кристал — велика рамка, поділена на 4 регіони
    gx, gy, gw, gh = 90, 60, 520, 300
    f.append(rect(gx, gy, gw, gh, fill="#fbfcfd", stroke=INK, sw=1.6, rx=8))
    midx = gx + gw / 2
    midy = gy + gh / 2
    # сітка регіонів (пунктир)
    f.append(line(midx, gy, midx, gy + gh, color="#d5d9df", sw=1.2, dash="5 5"))
    f.append(line(gx, midy, gx + gw, midy, color="#d5d9df", sw=1.2, dash="5 5"))
    for lx, ly, lab in [(gx + 20, gy + 22, "регіон"), (midx + 20, gy + 22, "регіон"),
                        (gx + 20, midy + 22, "регіон"), (midx + 20, midy + 22, "регіон")]:
        f.append(text(lx, ly, lab, size=10, color=MUTED, anchor="start"))

    # спеціальний вхідний пін такту зліва
    pinx, piny = 40, midy
    f.append(rect(pinx - 22, piny - 12, 30, 24, fill="#fdecea", stroke=POS, sw=1.8, rx=3))
    f.append(text(pinx - 7, piny + 4, "clk", size=10, color=POS, bold=True))
    f.append(text(pinx - 7, piny + 34, "спец.\nпін", size=9, color=MUTED) if False else
             mtext(pinx - 7, piny + 30, ["спец.", "пін"], size=9, color=MUTED))

    # глобальний буфер біля входу в кристал
    bfx = gx + 40
    sb, bin_, bout = buf(bfx, midy, r=14, label="буфер", color=FIELD)
    f.append(line(pinx + 8, midy, bin_[0], bin_[1], color=INK, sw=2.0))
    f.append(sb)

    # центральний вертикальний ХРЕБЕТ
    spinex = midx
    f.append(line(bout[0], midy, spinex, midy, color=FIELD, sw=3))
    f.append(line(spinex, gy + 20, spinex, gy + gh - 20, color=FIELD, sw=3))
    f.append(text(spinex + 8, gy + 40, "хребет", size=11, color=FIELD, bold=True, anchor="start"))

    # горизонтальні відводи в кожен регіон-ряд + гілки до кількох тригерів
    for ry in (gy + gh * 0.28, gy + gh * 0.72):
        f.append(line(spinex, ry, gx + gw - 30, ry, color=FIELD, sw=2.4))       # у праву половину
        f.append(line(spinex, ry, gx + 40, ry, color=FIELD, sw=2.4))            # у ліву половину
        for tx in (gx + 70, gx + 150, midx + 70, midx + 150):
            f.append(line(tx, ry, tx, ry + 16, color=FIELD, sw=1.8))
            f.append(rect(tx - 9, ry + 16, 18, 16, fill="#ffffff", stroke=INK, sw=1.4, rx=2))
    f.append(text(gx + 150, gy + gh * 0.28 - 8, "рядкові відводи → гілки до тригерів",
                  size=9, color=MUTED, anchor="start"))

    body, _, _ = textbox(W / 2, 402,
                         "Один буфер живить хребет, хребет — рядкові відводи регіонів, ті — короткі гілки до кожного тригера",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "network.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. enable.svg — дозвіл такту (правильно) проти врізання логіки в такт (зле)
# ════════════════════════════════════════════════════════════════════════════
def fig_enable():
    W, H = 700, 330
    f = []

    # ── ЛІВОРУЧ: зле — вентиль у лінії такту ──
    lx = 30
    f.append(text(lx + 150, 40, "ЗЛЕ: врізати логіку в такт", size=13, color=POS, bold=True, anchor="middle"))
    # такт → І-вентиль (з en) → тригер
    f.append(circle(lx + 20, 150, 12, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(lx + 20, 154, "clk", size=9, color=POS, bold=True))
    # вентиль І
    gx0 = lx + 90
    f.append('<path d="M %.0f %.0f L %.0f %.0f A 22 22 0 0 1 %.0f %.0f L %.0f %.0f Z" fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
             % (gx0, 128, gx0 + 20, 128, gx0 + 20, 172, gx0, 172, POS))
    f.append(text(gx0 + 10, 108, "&", size=13, color=POS, bold=True))
    f.append(line(lx + 32, 150, gx0, 150, color=INK, sw=1.8))
    f.append(line(gx0, 165, gx0 - 30, 165, color=INK, sw=1.6))
    f.append(text(gx0 - 34, 169, "en", size=10, color=MUTED, anchor="end"))
    s, n = ff(gx0 + 70, 128, label="FF")
    f.append(s)
    f.append(line(gx0 + 42, 150, n["clk"][0], n["clk"][1], color=INK, sw=1.8))
    f.append(text(gx0 + 96, 200, "викривлений такт:", size=10, color=POS, anchor="middle"))
    f.append(text(gx0 + 96, 214, "збій, перекіс, поза деревом", size=10, color=POS, anchor="middle"))

    # роздільник
    f.append(line(W / 2 + 6, 60, W / 2 + 6, 280, color="#d5d9df", sw=1.4, dash="6 6"))

    # ── ПРАВОРУЧ: добре — дозвіл на вході тригера, такт цілий ──
    rx = W / 2 + 40
    f.append(text(rx + 150, 40, "ДОБРЕ: дозвіл (CE), такт цілий", size=13, color=FIELD, bold=True, anchor="middle"))
    f.append(circle(rx + 20, 150, 12, fill="#eef7f0", stroke=FIELD, sw=1.8))
    f.append(text(rx + 20, 154, "clk", size=9, color=FIELD, bold=True))
    # тригер із окремим входом CE
    s2, n2 = ff(rx + 150, 128, w=64, h=52, label="FF")
    f.append(s2)
    # такт прямо в клинець
    f.append(line(rx + 32, 150, n2["clk"][0], n2["clk"][1], color=FIELD, sw=2.4))
    # окремий вхід CE зверху збоку
    f.append(line(rx + 90, 138, n2["left"][0], n2["left"][1] - 6, color=NEG, sw=1.8))
    f.append(text(rx + 86, 134, "en (CE)", size=10, color=NEG, anchor="end"))
    f.append(text(rx + 182, 205, "такт іде рівним деревом,", size=10, color=FIELD, anchor="middle"))
    f.append(text(rx + 182, 219, "тригер сам вирішує: брати чи ні", size=10, color=FIELD, anchor="middle"))

    body, _, _ = textbox(W / 2, 300,
                         "Такт не чіпаємо — керуємо входом дозволу; коли en=0, тригер тримає старе значення",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "enable.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. cmb-block.svg — узагальнений блок керування тактами: входи → нутро → виходи
# ════════════════════════════════════════════════════════════════════════════
def fig_cmb_block():
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 28, "Блок керування тактами: типові входи, нутро й виходи",
                  size=14, bold=True))

    # центральний блок-менеджер
    bx, by, bw, bh = 250, 80, 220, 250
    f.append(rect(bx, by, bw, bh, fill="#eef7f0", stroke=FIELD, sw=2, rx=8))
    f.append(text(bx + bw / 2, by + 24, "менеджер тактів", size=13, color=FIELD, bold=True))
    # нутро — три сходинки: ÷M → ФЧД+ГКН(×) → ÷O
    f.append(mtext(bx + bw / 2, by + 62,
                   ["÷M   (вхідний дільник)", "ФЧД → фільтр → ГКН", "×  синтез частоти",
                    "÷O₁ ÷O₂ ÷O₃  (виходи)"],
                   size=11, color=INK, lh=1.7))

    # ── входи зліва ──
    inx = 60
    ins = [(by + 55, "опорний такт", NEG, "REFCLK"),
           (by + 120, "скид", POS, "RST"),
           (by + 185, "зворотний зв’язок", FIELD, "CLKFB")]
    for iy, lab, col, tag in ins:
        f.append(rect(inx - 20, iy - 12, 34, 24, fill="#ffffff", stroke=col, sw=1.6, rx=3))
        f.append(text(inx - 3, iy + 4, tag, size=9, color=col, bold=True))
        f.append(arrow(inx + 14, iy, bx, iy, color=col, sw=2))
        f.append(text(inx - 3, iy - 20, lab, size=10, color=MUTED))

    # ── виходи справа: кілька синтезованих тактів ──
    outx = bx + bw
    outs = [(by + 60, "100 МГц", NEG),
            (by + 110, "200 МГц", NEG),
            (by + 160, "25 МГц, фаза +90°", FIELD)]
    for oy, lab, col in outs:
        f.append(arrow(outx, oy, outx + 90, oy, color=col, sw=2))
        f.append(text(outx + 96, oy + 4, lab, size=11, color=col, anchor="start", bold=True))

    # LOCKED — окремий вихід-прапорець
    ly = by + bh - 26
    f.append(arrow(outx, ly, outx + 90, ly, color=POS, sw=2))
    f.append(text(outx + 96, ly + 4, "LOCKED (захопив)", size=11, color=POS, anchor="start", bold=True))

    # петля зворотного зв’язку: вихід → назад у CLKFB (пунктир)
    fb_y = by + bh + 40
    f.append(line(outx + 40, outs[0][0], outx + 40, fb_y, color=FIELD, sw=1.6, dash="5 4"))
    f.append(line(outx + 40, fb_y, inx - 3, fb_y, color=FIELD, sw=1.6, dash="5 4"))
    f.append(line(inx - 3, fb_y, inx - 3, by + 185 + 12, color=FIELD, sw=1.6, dash="5 4"))
    f.append(text((outx + 40 + inx) / 2, fb_y - 6,
                  "петля зворотного зв’язку вирівнює фазу виходу з опорою",
                  size=10, color=FIELD))
    render(os.path.join(IMG, "cmb-block.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. cmb-vco.svg — вікно ГКН: чому множник/дільник не будь-які
# ════════════════════════════════════════════════════════════════════════════
def fig_cmb_vco():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 28, "Внутрішній генератор мусить лягти у вікно частот",
                  size=14, bold=True))

    # горизонтальна вісь частоти
    ax0, ax1, ay = 80, 620, 150
    f.append(line(ax0, ay, ax1, ay, color=INK, sw=1.6))
    f.append(text(ax1, ay + 24, "частота ГКН", size=11, color=MUTED, anchor="end"))

    # дозволене вікно (зелена смуга) між f_min і f_max
    wx0, wx1 = 230, 470
    f.append(rect(wx0, ay - 22, wx1 - wx0, 44, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=4))
    f.append(text((wx0 + wx1) / 2, ay + 5, "дозволене вікно ГКН", size=11, color=FIELD, bold=True))
    f.append(line(wx0, ay - 30, wx0, ay + 30, color=FIELD, sw=1.4, dash="4 3"))
    f.append(line(wx1, ay - 30, wx1, ay + 30, color=FIELD, sw=1.4, dash="4 3"))
    f.append(text(wx0, ay - 38, "f_min", size=10, color=FIELD, bold=True))
    f.append(text(wx1, ay - 38, "f_max", size=10, color=FIELD, bold=True))

    # три позначки: замалий множник (нижче вікна), у вікні, завеликий (вище)
    marks = [(150, "×N замалий:\nнижче f_min → не захопить", POS),
             ((wx0 + wx1) / 2, "×N доречний:\nу вікні → захопить", FIELD),
             (560, "×N завеликий:\nвище f_max → не захопить", POS)]
    for mx, lab, col in marks:
        f.append(circle(mx, ay, 6, fill=col, stroke=col))
        body, bw, bh = textbox(mx, ay + 70, lab, size=10, color=col,
                               fill="#ffffff", stroke=col, sw=1.4)
        f.append(body)

    # підказка внизу
    body, _, _ = textbox(W / 2, 300,
                         "f_ГКН = f_опорна · N / M мусить лягти між f_min і f_max — інакше LOCKED не підніметься",
                         size=11, color=INK, fill="#fdecea", stroke=POS)
    f.append(body)
    render(os.path.join(IMG, "cmb-vco.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. cmb-lock.svg — часова діаграма: скид → захоплення → LOCKED → лише тоді вихід
# ════════════════════════════════════════════════════════════════════════════
def fig_cmb_lock():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 28, "Порядок пуску: доки не LOCKED — виходу не вірити",
                  size=14, bold=True))

    x0, x1 = 130, 660
    # три доріжки сигналів
    tracks = [("RST", 80, POS), ("LOCKED", 155, FIELD), ("вихід у логіку", 230, NEG)]
    for lab, y, col in tracks:
        f.append(text(x0 - 12, y + 4, lab, size=11, color=col, anchor="end", bold=True))
        f.append(line(x0, y, x1, y, color="#e3e6ea", sw=1.0))  # базова лінія

    # моменти подій
    t_rel = 240   # відпустили скид
    t_lock = 470  # піднявся LOCKED

    # RST: високий до t_rel, потім низький
    yR = 80
    f.append(line(x0, yR - 22, t_rel, yR - 22, color=POS, sw=2.4))
    f.append(line(t_rel, yR - 22, t_rel, yR, color=POS, sw=2.4))
    f.append(line(t_rel, yR, x1, yR, color=POS, sw=2.4))
    f.append(text((x0 + t_rel) / 2, yR - 30, "скид активний", size=10, color=POS))
    f.append(text(t_rel + 6, yR - 8, "відпустили скид", size=9, color=MUTED, anchor="start"))

    # LOCKED: низький до t_lock, потім високий
    yL = 155
    f.append(line(x0, yL, t_lock, yL, color=FIELD, sw=2.4))
    f.append(line(t_lock, yL, t_lock, yL - 22, color=FIELD, sw=2.4))
    f.append(line(t_lock, yL - 22, x1, yL - 22, color=FIELD, sw=2.4))
    f.append(text((t_rel + t_lock) / 2, yL + 18, "захоплення (мкс)", size=10, color=MUTED))
    f.append(text(t_lock + 6, yL - 30, "захопив", size=10, color=FIELD, anchor="start", bold=True))

    # вихід у логіку: до t_lock — «не вірити» (штрихом), після — робочий
    yO = 230
    f.append(line(x0, yO, t_lock, yO, color=NEG, sw=2.0, dash="4 4"))
    f.append(line(t_lock, yO, x1, yO, color=NEG, sw=2.4))
    f.append(text((x0 + t_lock) / 2, yO + 20, "нестабільно — не вмикати логіку", size=10, color=POS))
    f.append(text((t_lock + x1) / 2, yO - 12, "робочі такти", size=10, color=NEG, bold=True))

    # вертикальні пунктири-«моменти»
    for tx in (t_rel, t_lock):
        f.append(line(tx, 60, tx, 250, color="#c7ccd2", sw=1.0, dash="3 4"))

    body, _, _ = textbox(W / 2, 322,
                         "Тримай решту схеми в скиді, доки LOCKED не стане «1»; зняв скид з менеджера — знову чекай LOCKED",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "cmb-lock.svg"), W, H, *f)


if __name__ == "__main__":
    fig_skew()
    fig_htree()
    fig_network()
    fig_enable()
    fig_cmb_block()
    fig_cmb_vco()
    fig_cmb_lock()
    print("OK: 7 фігур у", IMG)
