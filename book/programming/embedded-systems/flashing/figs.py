# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#a9791f"   # завантажувач / автоматика — теплий, відмінний від POS/NEG/FIELD


# ── the-link: дорога образу ПК → USB → перетворювач → UART → чіп ───────────────
# Ідея: образ виходить з ПК по USB, перетворювач робить із нього послідовний
# потік TX/RX, той тече у Flash; у новіших чипів власний USB — ланки менше.

def fig_the_link():
    W, H = 720, 320
    p = []
    y = 140
    bh = 84

    # ПК
    pc, pcw, pch = textbox(95, y, "ПК\n(образ .bin)", size=12, bold=True,
                           color=NEG, fill="#eaf0fd", stroke=NEG, sw=2, min_w=120)
    p.append(pc)
    # перетворювач
    cv, cvw, cvh = textbox(285, y, "перетворювач\nUSB ↔ UART", size=12, bold=True,
                           fill=FILL, stroke=INK, sw=1.8, min_w=150)
    p.append(cv)
    # чіп з Flash усередині
    chip_x, chip_w = 470, 220
    p.append(rect(chip_x, y - 60, chip_w, 120, fill="#fbfcff", stroke=INK, sw=2))
    p.append(text(chip_x + chip_w / 2, y - 38, "Мікроконтролер", size=12, bold=True, color=MUTED))
    p.append(fitbox(chip_x + 18, y - 18, chip_w - 36, 56, "Flash\n(сюди ляже образ)",
                    size=11, bold=True, color=NEG, fill="#eef3ff", stroke=NEG, sw=1.4))

    # стрілки з підписами каналу
    p.append(arrow(95 + pcw / 2, y, 285 - cvw / 2 - 2, y, color=INK, sw=2.2))
    p.append(text((95 + pcw / 2 + 285 - cvw / 2) / 2, y - 12, "USB", size=10, bold=True, color=MUTED))
    p.append(arrow(285 + cvw / 2, y, chip_x - 2, y, color=INK, sw=2.2))
    p.append(text((285 + cvw / 2 + chip_x) / 2, y - 12, "TX/RX", size=10, bold=True, color=MUTED))

    # нижня примітка про власний USB
    p.append(fitbox(110, 250, 500, 48,
                    "Новіші чипи (S3, C3…) мають власний USB — перетворювач зайвий, чіп під'єднується прямо",
                    size=11, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.4))

    render(os.path.join(OUT, "the-link.svg"), W, H, *p,
           title="Дорога образу: з ПК по USB, через перетворювач у послідовний потік, у чіп")


# ── run-vs-flash-mode: два режими чипа ────────────────────────────────────────
# Ідея: ліворуч — звичайний режим (виконує програму), праворуч — режим прошивки
# (слухає лінію); унизу — що перемикає (скидання + GPIO0, автоматично платою).

def fig_run_vs_flash():
    W, H = 720, 320
    p = []
    panel_y, panel_h = 70, 150

    # ліва панель — звичайний режим
    p.append(rect(40, panel_y, 300, panel_h, fill="none", stroke="#dcdcdc", sw=2))
    p.append(text(190, panel_y + 26, "Звичайний режим", size=13, bold=True, color=FIELD))
    p.append(fitbox(95, panel_y + 50, 190, 70, "ВИКОНУЄ\nвашу програму",
                    size=13, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2))

    # права панель — режим прошивки
    p.append(rect(380, panel_y, 300, panel_h, fill="none", stroke="#dcdcdc", sw=2))
    p.append(text(530, panel_y + 26, "Режим прошивки", size=13, bold=True, color=NEG))
    p.append(fitbox(435, panel_y + 50, 190, 70, "СЛУХАЄ лінію,\nчекає команд запису",
                    size=12, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=2))

    # нижня плашка — що перемикає
    p.append(fitbox(90, 248, 540, 52,
                    "Перемикає: скидання + затиснута завантажувальна ніжка (GPIO0) — автоматично платою, не руками",
                    size=11, bold=True, color=GOLD, fill="#fbf3df", stroke=GOLD, sw=1.6))

    render(os.path.join(OUT, "run-vs-flash-mode.svg"), W, H, *p,
           title="Два режими чипа: біжить чи слухає")


# ── rom-bootloader: чіп прошиває сам себе ─────────────────────────────────────
# Ідея: ПК лише диктує байти по дроту; усередині чипа їх приймає незмінний
# ROM-завантажувач і власноруч пише Flash. Незнищенний → чіп не «закам'яніє».

def fig_rom_bootloader():
    W, H = 740, 300
    p = []
    y = 150

    # ПК
    pc, pcw, _ = textbox(85, y, "ПК\n(диктує байти)", size=12, bold=True,
                         color=NEG, fill="#eaf0fd", stroke=NEG, sw=2, min_w=120)
    p.append(pc)

    # чіп — рамка з двома блоками всередині
    chip_x, chip_w = 230, 420
    p.append(rect(chip_x, 70, chip_w, 160, fill="#fbfcff", stroke=INK, sw=2.2))
    p.append(text(chip_x + chip_w / 2, 92, "Мікроконтролер", size=12, bold=True, color=MUTED))

    bl = fitbox(chip_x + 22, 120, 200, 84, "ROM-завантажувач\n(заводський, незмінний)",
                size=11, bold=True, color=GOLD, fill="#fbf3df", stroke=GOLD, sw=2)
    p.append(bl)
    fl = fitbox(chip_x + chip_w - 160, 120, 130, 84, "Flash\n(образ)",
                size=12, bold=True, color=NEG, fill="#eef3ff", stroke=NEG, sw=2)
    p.append(fl)

    # стрілки: ПК → завантажувач (дріт), завантажувач → Flash (пише)
    p.append(arrow(85 + pcw / 2, y, chip_x - 2, y, color=INK, sw=2.4))
    p.append(text((85 + pcw / 2 + chip_x) / 2, y - 12, "дріт", size=10, color=MUTED))
    p.append(arrow(chip_x + 22 + 200, 162, chip_x + chip_w - 160 - 2, 162, color=FIELD, sw=2.4))
    p.append(text((chip_x + 222 + chip_x + chip_w - 160) / 2, 150, "пише", size=10, bold=True, color=FIELD))

    # нижня думка
    p.append(text(W / 2, 268,
                  "ROM незнищенний → першу й будь-яку наступну прошивку приймає він; чіп не «закам'яніє»",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "rom-bootloader.svg"), W, H, *p,
           title="Чіп прошиває сам себе: ПК диктує, ROM-завантажувач пише Flash")


# ── protocol: три дії розмови — стерти, блоки з перевіркою, звірити ────────────
# Ідея: ланцюжок із трьох кроків; під ним — чому блоки несуть контрольну суму
# (дріт неідеальний).

def fig_protocol():
    W, H = 760, 320
    p = []
    y = 120
    bw, bh = 200, 96
    xs = [40, 280, 520]
    cells = [
        ("1. Стерти", "флеш пишеться\nлише по чистому", POS, "#fdecea"),
        ("2. Блоки + сума", "до кожного блоку —\nконтрольна сума", NEG, "#eaf0fd"),
        ("3. Звірити", "чи лягло саме те,\nщо слали", FIELD, "#eafaf0"),
    ]
    centers = []
    for i, (head, body, col, fill) in enumerate(cells):
        x = xs[i]
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2))
        p.append(text(x + bw / 2, y + 26, head, size=13, bold=True, color=col))
        p.append(line(x + 16, y + 38, x + bw - 16, y + 38, color=col, sw=1.2))
        p.append(mtext(x + bw / 2, y + 60, body, size=10.5, color=INK))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1] + 2, y + bh / 2, x - 2, y + bh / 2, color=INK, sw=2.4))

    # схема блоку: дані + хвіст контрольної суми
    by = 252
    p.append(rect(160, by, 320, 44, fill="#13202a", stroke="#0a141b", sw=1.4))
    p.append(text(200, by + 28, "блок даних", size=11, bold=True, color="#7fe0a0", anchor="start"))
    p.append(rect(380, by + 6, 92, 32, fill="#351313", stroke=POS, sw=1.4))
    p.append(text(426, by + 27, "сума", size=10, bold=True, color="#f0b0b0"))
    p.append(text(W / 2, by + 70, "дріт неідеальний — тому кожен блок перевіряють контрольною сумою",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "protocol.svg"), W, H, *p,
           title="Розмова ПК із ROM-завантажувачем: стерти → блоки з перевіркою → звірити")


# ── upload-sequence: повний цикл за кнопкою Upload ─────────────────────────────
# Ідея: шість пронумерованих кроків у ряд — від скидання до запуску нового коду.

def fig_upload_sequence():
    W, H = 960, 260
    p = []
    y = 120
    bw, bh = 142, 92
    gap = 4
    steps = [
        ("скидання", "→ режим прошивки", GOLD, "#fbf3df"),
        ("ROM-завантажувач", "слухає лінію", NEG, "#eaf0fd"),
        ("стерти", "ділянку Flash", POS, "#fdecea"),
        ("передати блоки", "завантажувач пише", NEG, "#eaf0fd"),
        ("звірити", "контрольні суми", FIELD, "#eafaf0"),
        ("скинути", "→ біжить НОВЕ", GOLD, "#fbf3df"),
    ]
    x = 24
    centers = []
    for i, (head, body, col, fill) in enumerate(steps):
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.8))
        p.append(circle(x + 18, y + 18, 11, fill=BG, stroke=col, sw=2))
        p.append(text(x + 18, y + 22, str(i + 1), size=12, bold=True, color=col))
        p.append(fitbox(x + 6, y + 36, bw - 12, 22, head, size=11, bold=True, color=col,
                        fill="none", stroke="none", sw=0))
        p.append(text(x + bw / 2, y + 78, body, size=9, color=MUTED))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1], y + bh / 2, x - 1, y + bh / 2, color=INK, sw=1.8))
        x += bw + gap

    p.append(text(W / 2, 244,
                  "«Upload» = скидання → слухати → стерти → записати з перевіркою → скинути → бігти",
                  size=12, bold=True, color=INK))

    render(os.path.join(OUT, "upload-sequence.svg"), W, H, *p,
           title="Натиснув «Upload» — що сталося за лаштунками")


# ── transfer-time: час заливання = розмір ÷ швидкість ──────────────────────────
# Ідея: дві смуги в одному масштабі — той самий образ на 460800 та 115200 бод;
# швидша летить за ~4 с, повільніша повзе ~16 с.

def fig_transfer_time():
    W, H = 720, 300
    p = []
    p.append(text(W / 2, 56, "образ 182 КБ ≈ 186 000 байтів · ~10 бітів на байт",
                  size=12, color=MUTED, italic=True))

    # дві смуги, спільна вісь часу: ширина пропорційна часу (4 с і 16 с)
    bx0 = 200
    full = 460                          # px на 16 с (повільніша смуга)
    sec = full / 16.0
    rows = [
        ("460800 бод", "46 080 байтів/с", 4.0, "≈ 4 с", FIELD, "#eafaf0"),
        ("115200 бод", "11 520 байтів/с", 16.0, "≈ 16 с", POS, "#fdecea"),
    ]
    y = 110
    for lab, rate, t, res, col, fill in rows:
        p.append(text(60, y + 4, lab, size=12.5, bold=True, color=INK, anchor="start"))
        p.append(text(60, y + 22, rate, size=9.5, color=MUTED, anchor="start"))
        w = sec * t
        p.append(rect(bx0, y - 14, w, 40, fill=fill, stroke=col, sw=1.8))
        p.append(text(bx0 + w + 12, y + 12, res, size=15, bold=True, color=col, anchor="start"))
        y += 90

    p.append(fitbox(90, 250, 540, 42,
                    "Швидкість задирають якомога вище; завелику дріт не тягне — доводиться відступати",
                    size=11, bold=True, color=GOLD, fill="#fbf3df", stroke=GOLD, sw=1.4))

    render(os.path.join(OUT, "transfer-time.svg"), W, H, *p,
           title="Скільки триває заливання: час = розмір ÷ швидкість")


# ── slip: SLIP-кадрування потоку байтів ───────────────────────────────────────
# Ідея: суцільний потік байтів ріжеться байтом-роздільником 0xC0 на кадри; той
# самий байт усередині даних екранують (0xC0 → 0xDB 0xDC).

def fig_slip():
    W, H = 720, 300
    p = []
    y = 110
    cw, ch = 56, 44
    x = 60
    seq = [
        ("C0", POS, "#fdecea"),
        ("дані", INK, FILL),
        ("дані", INK, FILL),
        ("C0", POS, "#fdecea"),
        ("дані", INK, FILL),
        ("C0", POS, "#fdecea"),
    ]
    for lab, col, fill in seq:
        p.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=1.8, rx=4))
        p.append(text(x + cw / 2, y + ch / 2 + 5, lab, size=12,
                      bold=(lab == "C0"), color=col))
        x += cw + 6
    p.append(text(60, y - 16, "потік байтів по UART", size=11, color=MUTED, anchor="start"))
    p.append(text(60 + cw / 2, y + ch + 22, "межа", size=9, color=POS))
    p.append(text(60 + 3 * (cw + 6) + cw / 2, y + ch + 22, "межа", size=9, color=POS))

    # екранування: коли 0xC0 трапляється в даних
    ey = 215
    p.append(text(60, ey, "0xC0 у даних →  екранують:", size=12, color=INK, anchor="start"))
    box1, w1, _ = textbox(360, ey - 4, "0xC0", size=12, bold=True, color=POS, fill="#fdecea", stroke=POS)
    p.append(box1)
    p.append(arrow(360 + w1 / 2 + 6, ey - 4, 440, ey - 4, color=INK, sw=2))
    box2, w2, _ = textbox(510, ey - 4, "0xDB 0xDC", size=12, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG)
    p.append(box2)

    p.append(text(W / 2, 272, "так на голому UART виходить надійний обмін пакетами",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "slip.svg"), W, H, *p,
           title="SLIP ріже потік на кадри байтом-роздільником 0xC0")


# ── sequence: чотири кроки прошивки ───────────────────────────────────────────
# Ідея: SYNC → stub у RAM → FLASH блоками → перевірка MD5; кожен крок несе свою
# роль (зв'язок, швидкість, запис, гарантія).

def fig_sequence():
    W, H = 760, 280
    p = []
    y = 110
    bw, bh = 160, 100
    xs = [30, 220, 410, 600]
    steps = [
        ("SYNC", "рукостискання:\nчіп на зв'язку?", GOLD, "#fbf3df"),
        ("STUB у RAM", "швидкий\n«прошивач»", NEG, "#eaf0fd"),
        ("FLASH блоками", "стерти й писати,\nкожен блок із сумою", POS, "#fdecea"),
        ("перевірка MD5", "звірити суму\nрегіону", FIELD, "#eafaf0"),
    ]
    centers = []
    for i, (head, body, col, fill) in enumerate(steps):
        x = xs[i]
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=2))
        p.append(text(x + bw / 2, y + 28, head, size=12.5, bold=True, color=col))
        p.append(line(x + 14, y + 40, x + bw - 14, y + 40, color=col, sw=1.2))
        p.append(mtext(x + bw / 2, y + 62, body, size=10, color=INK))
        centers.append((x, x + bw))
        if i > 0:
            p.append(arrow(centers[i - 1][1] + 2, y + bh / 2, x - 2, y + bh / 2, color=INK, sw=2.2))

    p.append(text(W / 2, 250,
                  "сума кожного блоку ловить спотворення в дорозі; MD5 наприкінці доводить — лягло саме те, що слали",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "sequence.svg"), W, H, *p,
           title="Чотири кроки esptool: SYNC → stub → FLASH → перевірка MD5")


if __name__ == "__main__":
    fig_the_link()
    fig_run_vs_flash()
    fig_rom_bootloader()
    fig_protocol()
    fig_upload_sequence()
    fig_transfer_time()
    fig_slip()
    fig_sequence()
    print("OK: figures written to", OUT)
