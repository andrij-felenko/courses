# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Кадр у пам'яті: framebuffer і RGB565».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
RED   = "#c0392b"   # канал R
GRN   = "#1e8449"   # канал G
BLU   = "#2457d6"   # канал B
TFT   = "#1f78b4"
GOLD  = "#b9770e"
OK    = "#27ae60"
COLD  = "#5b6b7a"


# ── 1. Розклад бітів RGB565: чому зелений — 6 ────────────────────────────────
def fig_bits():
    W, H = 760, 340
    f = [text(W / 2, 28, "Один піксель RGB565 = 16 бітів у трьох полях", size=16, bold=True)]

    # 16 клітинок бітів: 5 R, 6 G, 5 B
    x0, y0, cell = 60, 70, 40
    groups = [("R", RED, 5, "#fdecea"), ("G", GRN, 6, "#eafaf0"), ("B", BLU, 5, "#eef2fb")]
    i = 0
    for name, col, n, fill in groups:
        gx = x0 + i * cell
        for k in range(n):
            x = x0 + i * cell + k * cell
            f.append(rect(x, y0, cell, cell, fill=fill, stroke=col, sw=1.8, rx=3))
            f.append(text(x + cell / 2, y0 + 26, name, size=13, color=col, bold=True))
        # дужка-підпис поля
        f.append(line(gx + 2, y0 + cell + 8, gx + n * cell - 2, y0 + cell + 8, color=col, sw=2.2))
        levels = 2 ** n
        f.append(text(gx + n * cell / 2, y0 + cell + 26,
                      "%d біт → %d рівнів" % (n, levels), size=10.5, color=col, bold=True))
        i += n
    # номери бітів (15 ліворуч … 0 праворуч)
    f.append(text(x0 + 6, y0 - 8, "біт 15 (старший)", size=9, color=MUTED, anchor="start"))
    f.append(text(x0 + 16 * cell - 6, y0 - 8, "біт 0 (молодший)", size=9, color=MUTED, anchor="end"))

    # чому зелений ширший
    f.append(rect(60, 205, 640, 66, fill="#f4f6f8", stroke=GRN, sw=1.6))
    f.append(mtext(380, 232,
                   "зелений дістає зайвий біт не випадково: у людському оці зелених колбочок\n"
                   "найбільше, і саме в зеленому ми найгостріше бачимо переходи — 64 його\n"
                   "рівні маскують сходинки там, де 32 було б помітно мало",
                   size=10.5, color=INK, lh=1.35))

    f.append(text(W / 2, 300, "5 + 6 + 5 = 16 → рівно один uint16_t, 65 536 кольорів",
                  size=12, color=INK, bold=True))
    f.append(text(W / 2, 324,
                  "COLMOD 0x55 в ініціалізації — це і є обіцянка контролеру: чекай на такі пікселі",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "bits.svg"), W, H, *f)


# ── 2. Пастка порядку байтів: uint16 в RAM проти дротів SPI ──────────────────
def fig_byteorder():
    W, H = 760, 360
    f = [text(W / 2, 28, "Пастка: пам'ять — молодший байт першим, дріт — старший", size=15.5, bold=True)]

    color = "0xF800"  # чистий червоний RGB565
    f.append(text(W / 2, 54, "колір червоний = 0xF800 (R=31, G=0, B=0)", size=11, color=RED, bold=True))

    # злитий uint16
    ux, uy = 300, 78
    f.append(rect(ux, uy, 160, 34, fill="#fdecea", stroke=RED, sw=2))
    f.append(text(ux + 80, uy + 23, "0xF800", size=13, color=RED, bold=True))
    f.append(text(ux + 80, uy - 6, "одне 16-бітне число", size=9.5, color=MUTED))

    # РЯД 1 — як лежить у RAM (little-endian: молодший 0x00 за меншою адресою)
    ry = 160
    f.append(text(90, ry - 14, "у RAM мікроконтролера (little-endian):", size=10.5, color=INK, anchor="start", bold=True))
    ram = [("addr N", "0x00", COLD, "молодший байт"), ("addr N+1", "0xF8", RED, "старший байт")]
    for i, (addr, val, col, note) in enumerate(ram):
        x = 130 + i * 210
        f.append(rect(x, ry, 190, 44, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 55, ry + 27, val, size=13, color=col, bold=True))
        f.append(text(x + 130, ry + 20, addr, size=9, color=MUTED))
        f.append(text(x + 130, ry + 34, note, size=8.5, color=MUTED, italic=True))

    # стрілка «наївно вилили як є»
    f.append(arrow(340, ry + 52, 340, ry + 92, color=POS, sw=2))
    f.append(text(360, ry + 74, "вилив байти «як лежать»", size=9.5, color=POS, anchor="start", italic=True))

    # РЯД 2 — що прийшло в контролер (він читає старший першим)
    wy = 264
    f.append(text(90, wy - 14, "по SPI контролер чекає старший байт ПЕРШИМ:", size=10.5, color=INK, anchor="start", bold=True))
    wire = [("1-й на дроті", "0x00", COLD), ("2-й на дроті", "0xF8", RED)]
    for i, (ord_, val, col) in enumerate(wire):
        x = 130 + i * 210
        f.append(rect(x, wy, 190, 40, fill="#fff3e0", stroke=GOLD, sw=1.8))
        f.append(text(x + 55, wy + 25, val, size=13, color=col, bold=True))
        f.append(text(x + 130, wy + 25, ord_, size=9, color=MUTED))
    f.append(text(W / 2, wy + 62,
                  "контролер зібрав 0x00F8 = темно-синій → «червоне стало синім»: не панель, а неперевернутий байт",
                  size=10.5, color=POS, bold=True))
    render(os.path.join(IMG, "byteorder.svg"), W, H, *f)


# ── 3. Адресне вікно GRAM: CASET · RASET · RAMWR ─────────────────────────────
def fig_window():
    W, H = 760, 360
    f = [text(W / 2, 28, "Пишемо не «в точку», а у вікно: CASET · RASET · RAMWR", size=15, bold=True)]

    # сітка-екран ліворуч
    gx, gy, gs, n = 70, 70, 24, 8
    for r in range(n):
        for c in range(n):
            inside = 2 <= c <= 5 and 1 <= r <= 4
            fill = "#d6ecff" if inside else "#f4f6f8"
            f.append(rect(gx + c * gs, gy + r * gs, gs, gs,
                          fill=fill, stroke="#c7ced6", sw=1, rx=0))
    # рамка вікна
    f.append(rect(gx + 2 * gs, gy + 1 * gs, 4 * gs, 4 * gs, fill="none", stroke=TFT, sw=2.4, rx=0))
    f.append(text(gx + 4 * gs, gy + n * gs + 20, "вікно (2,1)…(5,4)", size=10, color=TFT, bold=True))
    # осі
    f.append(text(gx - 8, gy + gs / 2, "x→", size=9, color=MUTED, anchor="end"))
    f.append(text(gx + n * gs / 2, gy - 8, "стовпці", size=9, color=MUTED))

    # три команди праворуч
    cmds = [
        ("CASET 0x2A", "x_start … x_end", "межі стовпців", TFT),
        ("RASET 0x2B", "y_start … y_end", "межі рядків",   TFT),
        ("RAMWR 0x2C", "потік пікселів",  "лити RGB565 поспіль", OK),
    ]
    cx, cy0, cw, ch = 400, 84, 300, 60
    for i, (cmd, arg, note, col) in enumerate(cmds):
        yy = cy0 + i * (ch + 14)
        f.append(rect(cx, yy, cw, ch, fill=FILL, stroke=col, sw=1.8))
        f.append(text(cx + 16, yy + 24, cmd, size=12.5, color=col, bold=True, anchor="start"))
        f.append(text(cx + 16, yy + 44, arg, size=11, color=INK, anchor="start"))
        f.append(text(cx + cw - 14, yy + 36, note, size=9.5, color=MUTED, anchor="end", italic=True))
        if i < 2:
            f.append(arrow(cx + cw / 2, yy + ch, cx + cw / 2, yy + ch + 14, color=INK, sw=1.6))

    f.append(text(W / 2, 336,
                  "задав вікно двома командами — і контролер сам розкладає потік по рядках, автоінкремент адреси",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "window.svg"), W, H, *f)


# ── 4. Дві стратегії: повний кадр у RAM проти малювання смугою в GRAM ────────
def fig_strategy():
    W, H = 760, 360
    f = [text(W / 2, 28, "Дві стратегії під тісну пам'ять МК", size=16, bold=True)]

    # ЛІВА: повний кадр у RAM
    lx = 60
    f.append(rect(lx, 66, 300, 250, fill="#eef4f8", stroke=TFT, sw=2))
    f.append(text(lx + 150, 90, "повний кадр у RAM", size=13, color=TFT, bold=True))
    f.append(rect(lx + 60, 110, 180, 110, fill="#d6ecff", stroke=TFT, sw=1.6))
    f.append(text(lx + 150, 168, "fb[W·H]", size=13, color=INK, bold=True))
    f.append(mtext(lx + 150, 244,
                   "малюй будь-де, будь-коли,\nнакладай шари — тоді одним\nмахом виштовхни на панель",
                   size=10, color=INK, lh=1.3))
    f.append(text(lx + 150, 300, "ціна: 320×240×2 ≈ 150 КБ RAM", size=10, color=POS, bold=True))

    # ПРАВА: смуга + пряме малювання в GRAM
    rx = 400
    f.append(rect(rx, 66, 300, 250, fill="#fff8e6", stroke=GOLD, sw=2))
    f.append(text(rx + 150, 90, "смуга → у GRAM панелі", size=13, color=GOLD, bold=True))
    # три смуги
    for i in range(3):
        yy = 108 + i * 24
        fill = "#ffe4a3" if i == 1 else "#fff3e0"
        f.append(rect(rx + 60, yy, 180, 20, fill=fill, stroke=GOLD, sw=1.3))
    f.append(text(rx + 150, 122 + 24, "малий буфер на кілька рядків", size=9.5, color=MUTED))
    f.append(mtext(rx + 150, 214,
                   "намалюй смугу — виштовхни —\nповтори; або пиши прямо в GRAM\nчерез вікно, зовсім без буфера",
                   size=10, color=INK, lh=1.3))
    f.append(text(rx + 150, 292, "ціна: RAM у рази менше,", size=10, color=OK, bold=True))
    f.append(text(rx + 150, 308, "але губиться довільний доступ", size=10, color=POS, bold=True))

    render(os.path.join(IMG, "strategy.svg"), W, H, *f)


# ── 5. set_window(): чотири байти меж кожної осі, старший перший ──────────────
def fig_setwindow():
    W, H = 760, 380
    f = [text(W / 2, 28, "set_window(): дві 16-бітні межі → чотири байти, старший перший", size=14.5, bold=True)]

    # приклад: стовпці 30..69  (0x001E .. 0x0045)
    f.append(text(W / 2, 52, "приклад: x0=30 (0x001E), x1=69 (0x0045)", size=11, color=INK))

    # рядок команди CASET 0x2A
    cx0, cy = 70, 84
    f.append(rect(cx0, cy, 120, 40, fill="#eef4f8", stroke=TFT, sw=1.9))
    f.append(text(cx0 + 60, cy + 18, "CASET", size=12, color=TFT, bold=True))
    f.append(text(cx0 + 60, cy + 33, "0x2A (команда)", size=9, color=MUTED))
    f.append(arrow(cx0 + 120, cy + 20, cx0 + 150, cy + 20, color=INK, sw=1.8))

    # чотири байти-аргументи
    bx0 = cx0 + 160
    bytes4 = [("0x00", "x0 старший", COLD), ("0x1E", "x0 молодший", TFT),
              ("0x00", "x1 старший", COLD), ("0x45", "x1 молодший", TFT)]
    bw = 118
    for i, (val, note, col) in enumerate(bytes4):
        x = bx0 + i * (bw + 6)
        f.append(rect(x, cy, bw, 40, fill=FILL, stroke=col, sw=1.7))
        f.append(text(x + bw / 2, cy + 20, val, size=13, color=col, bold=True))
        f.append(text(x + bw / 2, cy + 34, note, size=8.3, color=MUTED))
    # той факт, що байтів чотири
    f.append(text(W / 2, cy + 62, "чотири байти = дві координати по два байти, кожна СТАРШИМ уперед",
                  size=10.5, color=POS, bold=True))

    # код-натяк на пакування
    ry = 190
    box, bw2, bh2 = textbox(W / 2, ry + 44,
        "buf[0] = x0 >> 8;   buf[1] = x0 & 0xFF;\n"
        "buf[2] = x1 >> 8;   buf[3] = x1 & 0xFF;",
        size=12.5, pad=14, fill="#0d1b2a", stroke=TFT, sw=1.6, color="#eaf2ff", bold=False)
    f.append(box)
    f.append(text(W / 2, ry + 8, "у коді set_window() пакує так (старший байт першим):",
                  size=10.5, color=INK))

    # RASET + RAMWR коротко нижче
    yy = 300
    seq = [("RASET 0x2B", "так само 4 байти рядків y0,y1", TFT),
           ("RAMWR 0x2C", "далі лити потік RGB565", OK)]
    for i, (cmd, note, col) in enumerate(seq):
        x = 90 + i * 300
        f.append(rect(x, yy, 280, 44, fill=FILL, stroke=col, sw=1.7))
        f.append(text(x + 16, yy + 20, cmd, size=12, color=col, bold=True, anchor="start"))
        f.append(text(x + 16, yy + 37, note, size=9.5, color=MUTED, anchor="start"))
    f.append(text(W / 2, yy + 68,
                  "переставиш старший↔молодший у будь-якій парі — вікно з'їде або обріжеться",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "setwindow.svg"), W, H, *f)


# ── 6. Гарячий шлях заливки: наївний цикл проти DMA + HW-swap + CS-низько ─────
def fig_hotpath():
    W, H = 760, 400
    f = [text(W / 2, 28, "Гарячий шлях заливки: де народжується швидкість", size=16, bold=True)]

    # ЛІВА колонка — наївно
    lx = 46
    f.append(rect(lx, 60, 320, 300, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(lx + 160, 84, "наївно — по пікселю", size=13, color=POS, bold=True))
    bad = [
        "for кожен піксель:",
        "  swap16() вручну в циклі",
        "  підняти CS  →  байт  →  опустити CS",
        "  чекати кінця передачі (CPU стоїть)",
    ]
    for i, s in enumerate(bad):
        f.append(text(lx + 20, 116 + i * 30, s, size=10.5, color=INK, anchor="start"))
    f.append(line(lx + 20, 240, lx + 300, 240, color=POS, sw=1, dash="4,4"))
    f.append(mtext(lx + 160, 268,
                   "тисячі разів: зайвий swap, смикання CS\nна кожен байт, процесор чекає шину —\nкадр повзе, батарея тане",
                   size=10, color=POS, lh=1.32))
    f.append(text(lx + 160, 340, "повільно, гаряче", size=11.5, color=POS, bold=True))

    # ПРАВА колонка — гарячий шлях
    rx = 394
    f.append(rect(rx, 60, 320, 300, fill="#eafaf0", stroke=OK, sw=2))
    f.append(text(rx + 160, 84, "гарячий шлях — блоком", size=13, color=OK, bold=True))
    good = [
        "перевернути колір РАЗ перед циклом",
        "CS ↓ один раз на весь блок",
        "залізо міняє байти на льоту (HW swap)",
        "великий блок → DMA, CPU вільний",
        "CS ↑ після всього блоку",
    ]
    for i, s in enumerate(good):
        f.append(text(rx + 20, 116 + i * 27, s, size=10.5, color=INK, anchor="start"))
    f.append(line(rx + 20, 258, rx + 300, 258, color=OK, sw=1, dash="4,4"))
    f.append(mtext(rx + 160, 286,
                   "одна підготовка — і DMA жене буфер\nсам, поки процесор рахує наступний\nкадр; шина зайнята корисним, не CS",
                   size=10, color=INK, lh=1.32))
    f.append(text(rx + 160, 340, "швидко, холодно", size=11.5, color=OK, bold=True))

    f.append(text(W / 2, 384,
                  "та сама трійця CASET·RASET·RAMWR — різниця лише в тому, ЯК ти віддаєш потік",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "hotpath.svg"), W, H, *f)


# ── 7. Розвилка high color: 5-5-5 з бітом-сиротою проти 5-6-5 (для hist) ──────
def fig_high555vs565():
    W, H = 760, 360
    f = [text(W / 2, 28, "Один зайвий біт: службі (5-5-5) чи кольору (5-6-5)?", size=15.5, bold=True)]

    cell = 40
    x0 = 110

    # ── РЯД 1: 5-5-5, шістнадцятий біт — сирота ──
    y1 = 70
    f.append(text(x0 - 16, y1 - 12, "5-5-5  «Thousands» — 32 768 кольорів",
                  size=11, color=MUTED, anchor="start", bold=True))
    # 1 біт-сирота
    f.append(rect(x0, y1, cell, cell, fill="#ececec", stroke=MUTED, sw=1.8, rx=3))
    f.append(text(x0 + cell / 2, y1 + 26, "A?", size=12, color=MUTED, bold=True))
    # 5 R, 5 G, 5 B
    groups555 = [("R", RED, 5, "#fdecea"), ("G", GRN, 5, "#eafaf0"), ("B", BLU, 5, "#eef2fb")]
    i = 1
    for name, col, n, fill in groups555:
        for k in range(n):
            x = x0 + (i + k) * cell
            f.append(rect(x, y1, cell, cell, fill=fill, stroke=col, sw=1.8, rx=3))
            f.append(text(x + cell / 2, y1 + 26, name, size=12, color=col, bold=True))
        i += n
    f.append(text(x0 + cell / 2, y1 + cell + 16, "біт-сирота", size=8.6, color=MUTED, italic=True))
    # роль зайвого біта — у вільній смузі під клітинами ряду 1 (не наповзає на самі клітини)
    f.append(mtext(x0 + 11 * cell, y1 + cell + 20,
                   "зайвий біт → alpha / overlay /\n«яскравість» або просто ігнор",
                   size=9.5, color=MUTED, anchor="middle", lh=1.3))

    # ── РЯД 2: 5-6-5, біт вкладено в зелений ──
    y2 = 180
    f.append(text(x0 - 16, y2 - 12, "5-6-5  «high color» — 65 536 кольорів",
                  size=11, color=GRN, anchor="start", bold=True))
    groups565 = [("R", RED, 5, "#fdecea"), ("G", GRN, 6, "#eafaf0"), ("B", BLU, 5, "#eef2fb")]
    i = 0
    for name, col, n, fill in groups565:
        for k in range(n):
            x = x0 + (i + k) * cell
            fill2 = "#c8f0d6" if (name == "G" and k == 5) else fill
            f.append(rect(x, y2, cell, cell, fill=fill2, stroke=col, sw=1.8, rx=3))
            f.append(text(x + cell / 2, y2 + 26, name, size=12, color=col, bold=True))
        i += n
    # позначити «той самий біт» стрілкою від сироти вниз до 6-го зеленого
    gx6 = x0 + 10 * cell + cell / 2   # 6-й зелений: сирота(1)+R(5)+G(6-й=позиція 11) → індекс 10
    f.append(arrow(x0 + cell / 2, y1 + cell + 22, gx6, y2 - 6, color=GRN, sw=2))
    # підпис стрілки — у вільній смузі під клітинами ряду 2, над підсумковою рамкою
    f.append(text(gx6, y2 + cell + 22,
                  "той самий біт — у зелений", size=9.5, color=GRN, italic=True, anchor="middle"))

    # підсумок
    f.append(rect(60, 288, 640, 54, fill="#f4f6f8", stroke=GRN, sw=1.6))
    f.append(mtext(380, 310,
                   "16 ÷ 3 = 5 із залишком 1 — біт неподільний, комусь дістається цілим.\n"
                   "око найгостріше в зеленому → 6-й біт кладуть туди, де він найпомітніший",
                   size=10.5, color=INK, lh=1.34))
    render(os.path.join(IMG, "high555vs565.svg"), W, H, *f)


# ── 8. Чесне округлення 8→5: відкидання проти дублювання старших бітів ────────
def fig_quantize():
    W, H = 780, 420
    f = [text(W / 2, 28, "Утиск 8→5 біт: чому просте відкидання гасить біле", size=15.5, bold=True)]

    # шкала 0..255 угорі — вихідний 8-бітний канал
    sx, sw_, sy = 70, 640, 66
    f.append(text(sx, sy - 12, "8-бітний канал (0…255): 256 рівнів", size=10.5, color=INK, anchor="start", bold=True))
    f.append(rect(sx, sy, sw_, 22, fill="#eef2fb", stroke=BLU, sw=1.6))
    f.append(text(sx - 6, sy + 16, "0", size=10, color=MUTED, anchor="end"))
    f.append(text(sx + sw_ + 6, sy + 16, "255", size=10, color=MUTED, anchor="start"))

    # ── ЛІВА: тільки відкинути молодші 3 біти (v>>3) ──
    lx, ly = 70, 150
    f.append(rect(lx, ly, 320, 210, fill="#fdecea", stroke=POS, sw=1.9))
    f.append(text(lx + 160, ly + 24, "просто відкинути: v >> 3", size=12.5, color=POS, bold=True))
    # 255 → 31 → назад
    steps_bad = [
        "255 = 1111 1111",
        "  >> 3  →  11111 = 31   (5 біт)",
        "назад у 8 біт: 31 << 3",
        "  = 1111 1000 = 248",
    ]
    for i, s in enumerate(steps_bad):
        f.append(text(lx + 20, ly + 58 + i * 26, s, size=11, color=INK, anchor="start"))
    f.append(line(lx + 20, ly + 168, lx + 300, ly + 168, color=POS, sw=1, dash="4,4"))
    f.append(text(lx + 160, ly + 190, "255 → 248: біле недотягнуло, ледь сіре",
                  size=10.5, color=POS, bold=True))

    # ── ПРАВА: дублювати старші біти вниз ──
    rx = 420
    f.append(rect(rx, ly, 320, 210, fill="#eafaf0", stroke=OK, sw=1.9))
    f.append(text(rx + 160, ly + 24, "дублювати старші вниз", size=12.5, color=OK, bold=True))
    steps_good = [
        "5 біт = 11111 = 31",
        "8 біт = (31<<3) | (31>>2)",
        "  1111 1000 | 0000 0111",
        "  = 1111 1111 = 255",
    ]
    for i, s in enumerate(steps_good):
        f.append(text(rx + 20, ly + 58 + i * 26, s, size=11, color=INK, anchor="start"))
    f.append(line(rx + 20, ly + 168, rx + 300, ly + 168, color=OK, sw=1, dash="4,4"))
    f.append(text(rx + 160, ly + 190, "255 → 255: діапазон повний, біле чисте",
                  size=10.5, color=OK, bold=True))

    f.append(text(W / 2, 400,
                  "поле вузьке — точність губиться завжди; питання лише, куди «липне» край шкали",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "quantize.svg"), W, H, *f)


# ── 9. MADCTL і напрям розгортки: який кут стає (0,0) для вікна ───────────────
def fig_madctl():
    W, H = 780, 430
    f = [text(W / 2, 28, "MADCTL крутить розгортку: те саме вікно лягає в інший кут", size=15, bold=True)]
    f.append(text(W / 2, 52, "MX (стовпці), MY (рядки), MV (обмін осей) — три біти визначають початок і хід адреси",
                  size=10.5, color=MUTED))

    def panel(px, py, title, origin, arrows, col):
        gs, n = 22, 6
        f.append(text(px + n * gs / 2, py - 12, title, size=11, color=col, bold=True))
        for r in range(n):
            for c in range(n):
                f.append(rect(px + c * gs, py + r * gs, gs, gs, fill="#f4f6f8", stroke="#cdd4dc", sw=0.9, rx=0))
        # позначити (0,0) кут кружком
        ox, oy = origin
        cx = px + (0 if ox == 0 else n * gs)
        cy = py + (0 if oy == 0 else n * gs)
        f.append(circle(cx, cy, 7, fill=col, stroke=col, sw=1))
        f.append(text(cx + (10 if ox == 0 else -10), cy + (18 if oy == 0 else -10),
                      "(0,0)", size=9, color=col, bold=True,
                      anchor="start" if ox == 0 else "end"))
        # стрілка ходу першого рядка
        (ax1, ay1, ax2, ay2) = arrows
        f.append(arrow(px + ax1 * gs, py + ay1 * gs, px + ax2 * gs, py + ay2 * gs, color=col, sw=2))

    # чотири орієнтації
    panel(60, 110, "MX=0 MY=0 (0°)", (0, 0), (0.5, 0.5, 5.5, 0.5), TFT)
    panel(300, 110, "MX=1 MY=0 (дзерк. X)", (1, 0), (5.5, 0.5, 0.5, 0.5), GOLD)
    panel(540, 110, "MX=1 MY=1 (180°)", (1, 1), (5.5, 5.5, 0.5, 5.5), RED)

    # MV — обмін осей
    panel(300, 290, "MV=1 (обмін X↔Y, 90°)", (0, 0), (0.5, 0.5, 0.5, 5.5), GRN)

    f.append(rect(540, 285, 200, 110, fill="#f4f6f8", stroke=INK, sw=1.4))
    f.append(mtext(640, 312,
                   "той самий CASET/RASET —\nале «стовпець» і «рядок»\nтепер міряються від\nіншого кута й в інший бік",
                   size=10, color=INK, lh=1.34))

    f.append(text(W / 2, 415,
                  "картинка «перевернулась» чи «дзеркальна» — крути MADCTL, а не переставляй пікселі",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "madctl.svg"), W, H, *f)


# ── 10. Смуга: елемент на межі двох смуг обробляється двічі ───────────────────
def fig_strip():
    W, H = 780, 420
    f = [text(W / 2, 28, "Малювання смугами: елемент на стику ріжеться й малюється двічі", size=14.5, bold=True)]

    # екран праворуч, поділений на смуги
    ex, ey, ew, eh = 470, 70, 240, 300
    nstrip = 5
    sh = eh / nstrip
    f.append(text(ex + ew / 2, ey - 12, "екран, поділений на 5 смуг", size=10.5, color=INK, bold=True))
    for i in range(nstrip):
        fill = "#fff3e0" if i % 2 == 0 else "#f4f6f8"
        f.append(rect(ex, ey + i * sh, ew, sh, fill=fill, stroke=GOLD, sw=1.3, rx=0))
        f.append(text(ex - 8, ey + i * sh + sh / 2 + 4, "смуга %d" % i, size=9, color=MUTED, anchor="end"))
    # коло-елемент, що лежить на межі смуг 1 і 2
    ccx, ccy, cr = ex + ew / 2, ey + 2 * sh, 40
    f.append(circle(ccx, ccy, cr, fill="none", stroke=TFT, sw=2.4))
    f.append(line(ex, ey + 2 * sh, ex + ew, ey + 2 * sh, color=POS, sw=2.2, dash="6,4"))
    f.append(text(ccx, ccy - cr - 8, "коло на стику смуг 1|2", size=9.5, color=TFT, bold=True))
    f.append(text(ex + ew + 10, ey + 2 * sh, "межа", size=9, color=POS, anchor="start", bold=True))

    # ліворуч — логіка обробки
    lx = 50
    f.append(rect(lx, 80, 380, 300, fill="#f4f6f8", stroke=INK, sw=1.5))
    f.append(text(lx + 190, 106, "як обробляється кожна смуга", size=12, color=INK, bold=True))
    logic = [
        "для кожної смуги s:",
        "   clear(buf)               // малий буфер W×sh",
        "   встав межі вікна: y0=s·sh … y1",
        "   намалюй у buf усі елементи,",
        "      обрізавши їх до цієї смуги",
        "   виштовхни buf у GRAM (RAMWR)",
    ]
    for i, s in enumerate(logic):
        f.append(text(lx + 20, 138 + i * 27, s, size=10.5, color=INK, anchor="start"))
    f.append(line(lx + 20, 312, lx + 360, 312, color=INK, sw=1, dash="4,4"))
    f.append(mtext(lx + 190, 338,
                   "коло перетинає межу → його верхня дуга\nмалюється у смузі 1, нижня — у смузі 2:\nдвічі порахований, кожен раз обрізаний",
                   size=10, color=POS, lh=1.32))

    f.append(text(W / 2, 405,
                  "ціна економії RAM — втрата довільного доступу: малюєш з оглядкою на поточну смугу",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "strip.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bits()
    fig_byteorder()
    fig_window()
    fig_strategy()
    fig_setwindow()
    fig_hotpath()
    fig_high555vs565()
    fig_quantize()
    fig_madctl()
    fig_strip()
    print("OK: 10 figures ->", IMG)
