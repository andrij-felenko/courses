# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_F = "#eef7ee"     # заливка логіки
GREEN_S = FIELD
BLUE_F  = "#eef4ff"     # заливка пам'яті / тригерів
BLUE_S  = "#c9d6f0"
AMBER_F = "#fff7e6"     # перемикачі маршрутизації
AMBER_S = "#caa24a"
SEA     = "#eaf1fb"     # «море» маршрутизації


# ════════════════════════════════════════════════════════════════════════════
#  Фігури статті (inside-fpga.md)
# ════════════════════════════════════════════════════════════════════════════

# ── logic-cell: LUT + тригер + вихідний мультиплексор ─────────────────────────
# Ідея: атом логіки FPGA поєднує комбінаційну функцію (LUT) і пам'ять стану
# (тригер); вихідний mux обирає, віддати миттєвий результат чи зафіксований.

def fig_logic_cell():
    W, H = 720, 300
    p = []
    yc = 150

    # входи
    for i in range(4):
        y = 96 + i * 26
        p.append(line(40, y, 120, y, color=NEG, sw=1.6))
        p.append(arrow(118, y, 122, y, color=NEG, sw=1.6))
        p.append(text(34, y + 4, "in%d" % i, size=10, color=NEG, anchor="end", bold=True))

    # LUT
    p.append(rect(122, 96, 96, 78, fill=GREEN_F, stroke=GREEN_S, sw=1.8))
    p.append(text(170, 128, "LUT", size=14, color=GREEN_S, bold=True))
    p.append(text(170, 146, "таблиця", size=9, color=MUTED))
    p.append(text(170, 188, "комбінаційна функція", size=9.5, color=GREEN_S, italic=True))

    # тригер
    p.append(line(218, yc, 286, yc, color=INK, sw=1.8))
    p.append(arrow(284, yc, 288, yc, color=INK, sw=1.6))
    p.append(rect(288, yc - 26, 58, 52, fill=BLUE_F, stroke=BLUE_S, sw=1.8))
    p.append(text(317, yc + 2, "тригер", size=11, color=BLUE_S, bold=True))
    # символ фронту
    p.append('<polyline points="292,%.1f 297,%.1f 297,%.1f" fill="none" stroke="%s" stroke-width="1.3"/>'
             % (yc + 22, yc + 14, yc + 22, BLUE_S))
    p.append(text(317, yc + 48, "пам'ять стану", size=9.5, color=BLUE_S, italic=True))

    # такт на тригер
    p.append(line(317, yc + 70, 317, yc + 28, color=POS, sw=1.7))
    p.append(arrow(317, yc + 30, 317, yc + 28, color=POS, sw=1.5))
    p.append(text(317, yc + 86, "такт (clk)", size=10, color=POS, bold=True))

    # обхід тригера (комбінаційна гілка) до mux
    p.append('<polyline points="218,%.1f 250,%.1f 250,%.1f 470,%.1f" fill="none" '
             'stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>'
             % (yc, yc, yc - 56, yc - 56, MUTED))
    p.append(text(360, yc - 62, "комбінаційний вихід (повз тригер)", size=9, color=MUTED, italic=True))

    # реєстровий вихід до mux
    p.append(line(346, yc, 470, yc + 10, color=BLUE_S, sw=1.6))

    # вихідний mux (трапеція)
    mx, my = 470, yc - 24
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.7"/>'
             % (mx, my, mx + 30, my + 14, mx + 30, my + 60, mx, my + 74, AMBER_F, AMBER_S))
    p.append(text(mx + 13, yc + 4, "mux", size=10, color="#9a7322", bold=True))

    # вихід клітинки
    p.append(line(500, yc + 13, 600, yc + 13, color=GREEN_S, sw=2.0))
    p.append(arrow(598, yc + 13, 602, yc + 13, color=GREEN_S, sw=1.7))
    p.append(text(660, yc + 17, "вихід клітинки", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "logic-cell.svg"), W, H, *p,
           title="Логічна клітинка: LUT рахує, тригер запам'ятовує, mux обирає вихід")


# ── clb-grid: клітинки → логічний блок → регулярна сітка ──────────────────────
# Ідея: кілька клітинок із спільним ланцюгом переносу складають блок (CLB/LAB),
# а однакові блоки викладені сіткою по кристалу.

def fig_clb_grid():
    W, H = 720, 360
    p = []

    # ── ліворуч: один блок із чотирьох клітинок + ланцюг переносу ──
    bx, by = 60, 80
    bw, bh = 150, 200
    p.append(rect(bx, by, bw, bh, fill=GREEN_F, stroke=GREEN_S, sw=2))
    p.append(text(bx + bw / 2, by - 12, "логічний блок (CLB / LAB)", size=12, color=GREEN_S, bold=True))
    cell_h = 40
    for i in range(4):
        cy = by + 16 + i * (cell_h + 4)
        p.append(rect(bx + 16, cy, bw - 64, cell_h, fill=BG, stroke=BLUE_S, sw=1.3))
        p.append(text(bx + 16 + (bw - 64) / 2, cy + cell_h * 0.62, "LUT+тригер", size=9, color=INK))
    # ланцюг переносу — вертикальна швидка лінія крізь усі клітинки
    cxr = bx + bw - 30
    p.append(line(cxr, by + 20, cxr, by + bh - 12, color=POS, sw=2.4))
    for i in range(5):
        yy = by + 20 + i * (cell_h + 4)
        p.append(arrow(cxr, yy + 6, cxr, yy, color=POS, sw=1.6))
    p.append(text(cxr + 6, by + bh / 2, "ланцюг", size=9, color=POS, anchor="start", bold=True))
    p.append(text(cxr + 6, by + bh / 2 + 13, "переносу", size=9, color=POS, anchor="start", bold=True))

    # стрілка «повторити»
    p.append(arrow(bx + bw + 16, by + bh / 2, bx + bw + 70, by + bh / 2, color=INK, sw=2))
    p.append(text(bx + bw + 43, by + bh / 2 - 10, "повторити", size=10, color=MUTED))

    # ── праворуч: сітка однакових блоків ──
    gx, gy = 360, 70
    n = 5
    g = 52
    for r in range(n):
        for c in range(n):
            x = gx + c * g
            y = gy + r * g
            p.append(rect(x, y, g - 8, g - 8, fill=GREEN_F, stroke=GREEN_S, sw=1.2, rx=3))
    # канали між блоками (натяк маршрутизації)
    for c in range(n + 1):
        x = gx + c * g - 4
        p.append(line(x, gy - 6, x, gy + n * g - 6, color=AMBER_S, sw=0.8, dash="3 4"))
    p.append(text(gx + n * g / 2 - 4, gy - 16, "регулярна сітка однакових блоків", size=12, color=INK, bold=True))
    p.append(text(gx + n * g / 2 - 4, gy + n * g + 8, "між блоками — програмована маршрутизація",
                  size=10, color="#9a7322", italic=True))

    render(os.path.join(OUT, "clb-grid.svg"), W, H, *p,
           title="Клітинки збираються в блок, блоки — у сітку по всьому кристалу")


# ── routing: канали проводів + комутаційні матриці на перетинах ───────────────
# Ідея: між блоками тягнуться канали, на перетинах сидять перемикачі; один
# прокладений шлях показано червоним — це й «вибирає» бітстрім.

def fig_routing():
    W, H = 720, 370
    p = []

    gx, gy = 110, 70
    n = 3
    block = 60
    chan = 50
    step = block + chan

    # блоки
    centers = {}
    for r in range(n):
        for c in range(n):
            x = gx + c * step
            y = gy + r * step
            p.append(rect(x, y, block, block, fill=GREEN_F, stroke=GREEN_S, sw=1.6, rx=4))
            p.append(text(x + block / 2, y + block / 2 + 4, "блок", size=9, color=GREEN_S, bold=True))
            centers[(r, c)] = (x + block / 2, y + block / 2)

    # канали (сірі смуги) — горизонтальні й вертикальні
    for r in range(n):
        for c in range(n - 1):
            x0 = gx + c * step + block
            y0 = gy + r * step + block / 2
            p.append(line(x0, y0, x0 + chan, y0, color=MUTED, sw=6))
    for c in range(n):
        for r in range(n - 1):
            x0 = gx + c * step + block / 2
            y0 = gy + r * step + block
            p.append(line(x0, y0, x0, y0 + chan, color=MUTED, sw=6))

    # комутаційні матриці на перетинах каналів
    for r in range(n - 1):
        for c in range(n - 1):
            x = gx + c * step + block + chan / 2
            y = gy + r * step + block + chan / 2
            p.append(rect(x - 12, y - 12, 24, 24, fill=AMBER_F, stroke=AMBER_S, sw=1.6, rx=4))
            p.append(text(x, y + 4, "⊞", size=12, color="#9a7322"))

    # один прокладений зв'язок (червоний) від (0,0) до (1,2)
    (x0, y0) = centers[(0, 0)]
    path = "M%.1f %.1f " % (x0 + block / 2, y0)
    xr = gx + 0 * step + block + chan / 2
    path += "L%.1f %.1f " % (xr - 6, y0)
    path += "L%.1f %.1f " % (xr - 6, y0 + step)
    path += "L%.1f %.1f " % (gx + 2 * step, y0 + step)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, POS))
    p.append(arrow(gx + 2 * step - 2, y0 + step, gx + 2 * step + 2, y0 + step, color=POS, sw=2))
    p.append(text(gx + 2 * step + 6, y0 + step - 8, "один прокладений шлях", size=10, color=POS, anchor="start", bold=True))

    # легенда праворуч
    lx = 540
    p.append(rect(lx, 86, 18, 12, fill=None, stroke=MUTED, sw=6))
    p.append(text(lx + 26, 96, "канали проводів", size=10, color=INK, anchor="start"))
    p.append(rect(lx, 116, 18, 18, fill=AMBER_F, stroke=AMBER_S, sw=1.6, rx=4))
    p.append(text(lx + 26, 129, "комутаційні матриці", size=10, color=INK, anchor="start"))
    p.append(text(lx + 26, 145, "(перемикачі)", size=9, color=MUTED, anchor="start"))
    p.append(rect(lx, 162, 18, 18, fill=GREEN_F, stroke=GREEN_S, sw=1.6, rx=4))
    p.append(text(lx + 26, 175, "логічні блоки", size=10, color=INK, anchor="start"))

    p.append(text(W / 2, H - 16, "перемикачі вирішують, що з чим з'єднано — їхні стани задає бітстрім",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "routing.svg"), W, H, *p,
           title="Маршрутизація: канали проводів і перемикачі на перетинах")


# ── island: острови логіки в морі проводів, по краях — піни I/O ───────────────
# Ідея: загальний план FPGA — острівний: логіка-острови, маршрутизація-море,
# периметр — піни вводу-виводу; стовпці BRAM/DSP врізані серед островів.

def fig_island():
    W, H = 720, 360
    p = []

    # «море» маршрутизації
    p.append(rect(70, 56, 580, 280, fill=SEA, stroke=BLUE_S, sw=1.4, rx=8))

    # піни I/O по периметру
    def io_pad(x, y):
        return rect(x, y, 14, 14, fill="#dce8fb", stroke=NEG, sw=1.2, rx=2)
    for c in range(14):
        x = 92 + c * 40
        p.append(io_pad(x, 58))
        p.append(io_pad(x, 322))
    for r in range(6):
        y = 84 + r * 42
        p.append(io_pad(72, y))
        p.append(io_pad(636, y))
    p.append(text(W / 2, 50, "піни вводу-виводу (I/O) — по всьому периметру", size=10, color=NEG))

    # острови логіки + врізані стовпці BRAM/DSP
    cols_special = {3: ("BRAM", BLUE_F, BLUE_S), 7: ("DSP", "#f3e8d0", AMBER_S)}
    ix, iy = 110, 92
    gx, gy = 50, 40
    for c in range(10):
        for r in range(5):
            x = ix + c * gx
            y = iy + r * gy
            if c in cols_special:
                lab, fill, st = cols_special[c]
                p.append(rect(x, y, 34, 28, fill=fill, stroke=st, sw=1.4, rx=3))
                if r == 2:
                    p.append(text(x + 17, y + 18, lab, size=9, color=st, bold=True))
            else:
                p.append(rect(x, y, 34, 28, fill=GREEN_F, stroke=GREEN_S, sw=1.2, rx=3))

    # підписи
    p.append(text(170, H - 16, "острови — логічні блоки", size=10, color=GREEN_S, bold=True, anchor="start"))
    p.append(text(360, H - 16, "море — маршрутизація", size=10, color=BLUE_S, bold=True, anchor="start"))
    p.append(text(540, H - 16, "стовпці BRAM / DSP", size=10, color="#9a7322", bold=True, anchor="start"))

    render(os.path.join(OUT, "island.svg"), W, H, *p,
           title="Острівний план: логіка-острови, маршрутизація-море, береги — піни I/O")


# ── bram: тригери (марнотратно) проти готового блока RAM (двопортового) ────────
# Ідея: тримати буфер на тригерах — біт на цілу клітинку; вбудована BRAM —
# щільний блок на десятки кбіт, ще й двопортовий.

def fig_bram():
    W, H = 720, 320
    p = []

    # ── ліворуч: буфер на тригерах ──
    lx, ly = 70, 80
    p.append(text(lx + 90, ly - 14, "буфер на тригерах клітинок", size=12, color=POS, bold=True))
    for r in range(4):
        for c in range(6):
            x = lx + c * 30
            y = ly + r * 30
            p.append(rect(x, y, 24, 24, fill=BLUE_F, stroke=BLUE_S, sw=1.0, rx=3))
            p.append(text(x + 12, y + 16, "1б", size=9, color=MUTED))
    p.append(text(lx + 90, ly + 4 * 30 + 18, "біт на цілу клітинку — марнотратно", size=10, color=POS, italic=True))

    # стрілка
    p.append(arrow(lx + 200, ly + 50, lx + 250, ly + 50, color=INK, sw=2))
    p.append(text(lx + 225, ly + 38, "краще", size=10, color=MUTED))

    # ── праворуч: один блок BRAM, двопортовий ──
    rx, ry = lx + 270, 70
    bw, bh = 150, 150
    p.append(rect(rx, ry, bw, bh, fill=BLUE_F, stroke=BLUE_S, sw=2, rx=6))
    p.append(text(rx + bw / 2, ry + 40, "блочна RAM", size=13, color=BLUE_S, bold=True))
    p.append(text(rx + bw / 2, ry + 60, "(BRAM)", size=11, color=BLUE_S))
    p.append(text(rx + bw / 2, ry + 86, "18–36 кбіт", size=12, color=INK, bold=True))
    p.append(text(rx + bw / 2, ry + 106, "один щільний блок", size=9.5, color=MUTED, italic=True))

    # два порти
    p.append(line(rx - 60, ry + 36, rx, ry + 36, color=GREEN_S, sw=2))
    p.append(arrow(rx - 2, ry + 36, rx + 2, ry + 36, color=GREEN_S, sw=1.7))
    p.append(text(rx - 64, ry + 32, "порт A: пишемо", size=9.5, color=GREEN_S, anchor="end", bold=True))
    p.append(line(rx + bw, ry + 114, rx + bw + 60, ry + 114, color=NEG, sw=2))
    p.append(arrow(rx + bw + 58, ry + 114, rx + bw + 62, ry + 114, color=NEG, sw=1.7))
    p.append(text(rx + bw + 64, ry + 118, "порт B: читаємо", size=9.5, color=NEG, anchor="start", bold=True))
    p.append(text(rx + bw / 2, ry + bh + 22, "двопортова: пишемо й читаємо одночасно", size=10, color=INK, italic=True))

    render(os.path.join(OUT, "bram.svg"), W, H, *p,
           title="Буфер: тисячі тригерів проти одного готового блока RAM")


# ── dsp: множення на LUT (дорого) проти готового DSP-блока з MAC ──────────────
# Ідея: множник із LUT з'їдає сотні клітинок; DSP-блок робить «помножити й
# додати» (MAC) за такт, і сотні таких блоків працюють паралельно.

def fig_dsp():
    W, H = 720, 300
    p = []

    # ліворуч: множник на купі LUT
    lx, ly = 70, 90
    p.append(text(lx + 90, ly - 14, "множник із LUT", size=12, color=POS, bold=True))
    for r in range(5):
        for c in range(9):
            x = lx + c * 20
            y = ly + r * 20
            p.append(rect(x, y, 16, 16, fill=GREEN_F, stroke=GREEN_S, sw=0.8, rx=2))
    p.append(text(lx + 90, ly + 5 * 20 + 16, "сотні LUT на один множник", size=10, color=POS, italic=True))

    # стрілка
    p.append(arrow(lx + 200, ly + 50, lx + 250, ly + 50, color=INK, sw=2))
    p.append(text(lx + 225, ly + 38, "краще", size=10, color=MUTED))

    # праворуч: DSP-блок MAC
    rx, ry = lx + 270, 80
    # входи A, B
    p.append(text(rx - 18, ry + 30, "A", size=12, color=NEG, bold=True, anchor="end"))
    p.append(text(rx - 18, ry + 58, "B", size=12, color=NEG, bold=True, anchor="end"))
    p.append(arrow(rx - 14, ry + 30, rx + 8, ry + 30, color=NEG, sw=1.6))
    p.append(arrow(rx - 14, ry + 58, rx + 8, ry + 58, color=NEG, sw=1.6))
    # множник (×)
    p.append(circle(rx + 34, ry + 44, 22, fill="#f3e8d0", stroke=AMBER_S, sw=1.8))
    p.append(text(rx + 34, ry + 50, "×", size=20, color="#9a7322", bold=True))
    # суматор (+) з акумулятором
    p.append(arrow(rx + 56, ry + 44, rx + 84, ry + 44, color=INK, sw=1.6))
    p.append(circle(rx + 106, ry + 44, 22, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(rx + 106, ry + 51, "+", size=20, color=POS, bold=True))
    # акумулятор (зворотний зв'язок)
    p.append('<path d="M%.1f %.1f q 40 40 0 40 q -40 0 -40 -40" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 3"/>'
             % (rx + 106, ry + 66, MUTED))
    p.append(text(rx + 150, ry + 96, "сума", size=9.5, color=MUTED, anchor="start"))
    # рамка блока
    p.append(rect(rx - 6, ry + 8, 170, 88, fill=None, stroke=AMBER_S, sw=1.4, rx=8))
    p.append(text(rx + 80, ry + 4, "DSP-блок", size=12, color="#9a7322", bold=True))
    p.append(text(rx + 80, ry + 116, "MAC: A×B + сума — за один такт", size=10, color=INK, italic=True))

    p.append(text(W / 2, H - 16, "сотні DSP-блоків множать-і-додають одночасно — звідси сила у фільтрах і нейромережах",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "dsp.svg"), W, H, *p,
           title="Множення: сотні LUT проти готового DSP-блока з MAC")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури компонентної вставки (comp-hobby-fpga-boards.md)
# ════════════════════════════════════════════════════════════════════════════

# ── board-anatomy: що розпаяно навколо FPGA на платі iCE40-класу ──────────────

def fig_board_anatomy():
    W, H = 720, 380
    p = []

    # сама плата
    p.append(rect(60, 60, 600, 290, fill="#f1f5ef", stroke=GREEN_S, sw=1.6, rx=10))

    # FPGA в центрі
    cx, cy = W / 2, 205
    p.append(rect(cx - 70, cy - 50, 140, 100, fill=GREEN_F, stroke=GREEN_S, sw=2.2, rx=6))
    p.append(text(cx, cy - 6, "FPGA", size=16, color=GREEN_S, bold=True))
    p.append(text(cx, cy + 14, "поле LUT і тригерів", size=9.5, color=MUTED))

    def box(x, y, w, h, lines, fill, st):
        out = rect(x, y, w, h, fill=fill, stroke=st, sw=1.5, rx=5)
        out += mtext(x + w / 2, y + h / 2 - (len(lines) - 1) * 6 + 4, lines, size=9.5, color=INK)
        return out

    # флеш конфігурації (ліворуч-зверху)
    p.append(box(90, 86, 130, 44, ["флеш конфігурації", "(тримає схему)"], BLUE_F, BLUE_S))
    p.append(line(155, 130, cx - 60, cy - 46, color=BLUE_S, sw=1.4))
    p.append(text(200, 152, "SPI", size=9, color=BLUE_S))

    # USB-міст (ліворуч-знизу)
    p.append(box(90, 280, 130, 44, ["USB-міст", "(програмує флеш)"], AMBER_F, AMBER_S))
    p.append(line(155, 280, cx - 50, cy + 46, color=AMBER_S, sw=1.4))

    # генератор такту (зверху)
    p.append(box(cx - 65, 80, 130, 40, ["кварц / MEMS", "(спільний такт)"], "#fdecea", POS))
    p.append(line(cx, 120, cx, cy - 50, color=POS, sw=1.4))

    # стабілізатори (праворуч-зверху)
    p.append(box(500, 86, 130, 44, ["стабілізатори", "ядро + банки"], "#f6efd6", "#caa24a"))
    p.append(line(565, 130, cx + 60, cy - 46, color="#caa24a", sw=1.4))

    # світлодіоди / кнопки / PMOD (знизу-праворуч)
    p.append(box(490, 280, 140, 44, ["LED · кнопки · PMOD", "(вивід назовні)"], "#eef4ff", NEG))
    p.append(line(560, 280, cx + 55, cy + 46, color=NEG, sw=1.4))

    render(os.path.join(OUT, "board-anatomy.svg"), W, H, *p,
           title="Анатомія плати iCE40-класу: FPGA та його обов'язковий почет")


# ── two-classes: зовнішня флеш (iCE40) проти вбудованої (Gowin) ───────────────

def fig_two_classes():
    W, H = 720, 320
    p = []

    # ── ліворуч: iCE40-клас — два чипи ──
    lx = 60
    p.append(rect(lx, 70, 280, 210, fill="#f1f5ef", stroke=GREEN_S, sw=1.6, rx=10))
    p.append(text(lx + 140, 60, "iCE40-клас: схема ЗОВНІ", size=12, color=GREEN_S, bold=True))
    # FPGA
    p.append(rect(lx + 30, 120, 110, 80, fill=GREEN_F, stroke=GREEN_S, sw=2, rx=6))
    p.append(text(lx + 85, 165, "FPGA", size=13, color=GREEN_S, bold=True))
    # окрема флеш
    p.append(rect(lx + 175, 130, 80, 60, fill=BLUE_F, stroke=BLUE_S, sw=1.8, rx=5))
    p.append(text(lx + 215, 158, "флеш", size=11, color=BLUE_S, bold=True))
    p.append(text(lx + 215, 174, "SPI", size=9, color=MUTED))
    p.append(arrow(lx + 173, 160, lx + 142, 160, color=POS, sw=1.8))
    p.append(text(lx + 158, 148, "при старті", size=9, color=POS))
    p.append(text(lx + 140, 232, "два чипи поряд", size=10, color=INK))
    p.append(text(lx + 140, 252, "виходи мовчать перші мс (доки DONE=1)", size=9, color=MUTED, italic=True))

    # ── праворуч: Gowin-клас — один чип ──
    rx = 400
    p.append(rect(rx, 70, 260, 210, fill="#f1f5ef", stroke=AMBER_S, sw=1.6, rx=10))
    p.append(text(rx + 130, 60, "Gowin-клас: схема ВСЕРЕДИНІ", size=12, color="#9a7322", bold=True))
    # FPGA з вбудованою флеш
    p.append(rect(rx + 70, 120, 120, 90, fill=GREEN_F, stroke=GREEN_S, sw=2, rx=6))
    p.append(text(rx + 130, 150, "FPGA", size=13, color=GREEN_S, bold=True))
    p.append(rect(rx + 86, 162, 88, 36, fill=BLUE_F, stroke=BLUE_S, sw=1.4, rx=4))
    p.append(text(rx + 130, 184, "флеш усередині", size=9, color=BLUE_S))
    p.append(text(rx + 130, 232, "один чип", size=10, color=INK))
    p.append(text(rx + 130, 252, "вмикання фактично миттєве", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "two-classes.svg"), W, H, *p,
           title="Дві школи плат: флеш зовні (iCE40) чи всередині чипа (Gowin)")


# ── first-byte: ПК → bitstream → міст → флеш → FPGA встає → LED блимає ─────────

def fig_first_byte():
    W, H = 760, 240
    p = []
    y = 110
    bw, bh = 116, 58
    step = 142
    x = 24
    boxes = [
        ("ПК:\nbitstream", BLUE_F, BLUE_S),
        ("USB-міст:\nнесе файл", AMBER_F, AMBER_S),
        ("флеш:\nзовні/всередині", "#fdf6e3", "#caa24a"),
        ("FPGA:\nDONE = 1", GREEN_F, GREEN_S),
        ("LED:\nблимає", "#fdecea", POS),
    ]
    centers = []
    for i, (lab, fill, st) in enumerate(boxes):
        p.append(fitbox(x, y - bh / 2, bw, bh, lab, size=10, fill=fill, stroke=st, sw=1.6, bold=True))
        centers.append((x, x + bw))
        if i > 0:
            px = centers[i - 1][1]
            p.append(arrow(px + 2, y, x - 2, y, color=INK, sw=1.8))
        x += step

    p.append(text(W / 2, y + 60, "«перший байт» — це вся схема цілком, а не одна команда",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "first-byte.svg"), W, H, *p,
           title="Шлях «першого байта»: від опису на ПК до блимання світлодіода")


if __name__ == "__main__":
    # фігури статті
    fig_logic_cell()
    fig_clb_grid()
    fig_routing()
    fig_island()
    fig_bram()
    fig_dsp()
    # фігури компонентної вставки
    fig_board_anatomy()
    fig_two_classes()
    fig_first_byte()
    print("figs.py: 9 SVG записано у", OUT)
