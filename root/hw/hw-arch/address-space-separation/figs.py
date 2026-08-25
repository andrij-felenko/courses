# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Світлі заливки під усталений вигляд рамок цього розділу.
F_BLUE = "#f3f5fd"
F_RED  = "#fdf4f4"
F_GRN  = "#eef7ee"
F_GLD  = "#fff8e8"
F_GREY = "#f4f6f8"
GOLD_LINE = "#b8860b"


# ── buses: фон Нейман (одна шина) проти Гарварда (дві шини) ───────────────────
def fig_buses():
    W, H = 760, 340
    p = [text(W / 2, 26, "Два способи з'єднати процесор із пам'яттю", size=16, bold=True)]

    # --- Ліва половина: фон Нейман ---
    lx = 190
    p.append(text(lx, 58, "Модель фон Неймана", size=14, bold=True, color=NEG))
    p.append(text(lx, 76, "одна пам'ять, одна шина", size=10, color=MUTED, italic=True))
    cpuL = rect(lx - 55, 96, 110, 46, fill=F_BLUE, stroke=NEG, sw=1.8)
    p.append(cpuL); p.append(text(lx, 124, "Процесор", size=13, bold=True))
    memL = rect(lx - 90, 246, 180, 48, fill=F_GREY)
    p.append(memL)
    p.append(text(lx, 268, "Пам'ять", size=13, bold=True))
    p.append(text(lx, 285, "команди + дані разом", size=9.5, color=MUTED))
    # одна двонапрямлена шина
    p.append(line(lx, 142, lx, 246, color=INK, sw=3))
    p.append(text(lx + 60, 196, "одна шина", size=10, color=INK))
    p.append(text(lx + 60, 210, "по черзі", size=9.5, color=MUTED, italic=True))

    # --- Права половина: Гарвард ---
    rx = 570
    p.append(text(rx, 58, "Гарвардська модель", size=14, bold=True, color=FIELD))
    p.append(text(rx, 76, "дві пам'яті, дві шини", size=10, color=MUTED, italic=True))
    cpuR = rect(rx - 55, 96, 110, 46, fill=F_GRN, stroke=FIELD, sw=1.8)
    p.append(cpuR); p.append(text(rx, 124, "Процесор", size=13, bold=True))
    memI = rect(rx - 130, 246, 110, 48, fill=F_GLD)
    memD = rect(rx + 20, 246, 110, 48, fill=F_BLUE)
    p.append(memI); p.append(text(rx - 75, 268, "Команди", size=12, bold=True)); p.append(text(rx - 75, 285, "(флеш)", size=9.5, color=MUTED))
    p.append(memD); p.append(text(rx + 75, 268, "Дані", size=12, bold=True)); p.append(text(rx + 75, 285, "(RAM)", size=9.5, color=MUTED))
    # дві окремі шини
    p.append(line(rx - 75, 142, rx - 75, 246, color=GOLD_LINE, sw=3))
    p.append(line(rx + 75, 142, rx + 75, 246, color=NEG, sw=3))
    p.append(text(rx, 196, "дві шини —", size=10, color=INK))
    p.append(text(rx, 210, "водночас", size=9.5, color=FIELD, italic=True))

    render(os.path.join(OUT, "buses.svg"), W, H, *p)


# ── map: один 32-бітний адресний простір, поділений на області ───────────────
def fig_map():
    W, H = 720, 470
    p = [text(W / 2, 26, "Один адресний простір, поділений на області", size=16, bold=True)]
    p.append(text(W / 2, 46, "32 біти адреси → 4 ГБ номерів; кожна область має своє призначення",
                  size=10.5, color=MUTED, italic=True))

    x, w = 250, 300
    rows = [
        ("0xFFFFFFFF", "", None, None),
        ("Системні регістри ядра", "керування процесором", F_GREY, LINE),
        ("Зовнішня пам'ять", "флеш/RAM за шиною, XIP", F_BLUE, NEG),
        ("Периферія", "регістри GPIO, UART, таймерів (XN)", F_RED, POS),
        ("SRAM", "змінні, стек, купа — читання/запис", F_BLUE, NEG),
        ("Код", "команди, вектори — читання/виконання", F_GLD, GOLD_LINE),
        ("0x00000000", "", None, None),
    ]
    top = 70
    band = 56
    y = top
    # верхня межа-адреса
    p.append(text(x - 8, y + 4, rows[0][0], size=10, color=MUTED, anchor="end"))
    y += 14
    for title, sub, fill, stroke in rows[1:-1]:
        p.append(rect(x, y, w, band, fill=fill, stroke=stroke, sw=1.8))
        p.append(text(x + w / 2, y + 24, title, size=13.5, bold=True))
        p.append(text(x + w / 2, y + 42, sub, size=10, color=MUTED))
        y += band + 6
    # нижня межа-адреса
    p.append(text(x - 8, y + 4, rows[-1][0], size=10, color=MUTED, anchor="end"))

    # підпис зліва: старша адреса вгорі
    p.append(text(60, top + 40, "старші", size=10, color=MUTED))
    p.append(text(60, top + 56, "адреси", size=10, color=MUTED))
    p.append(text(60, y - 20, "молодші", size=10, color=MUTED))
    p.append(text(60, y - 4, "адреси", size=10, color=MUTED))
    p.append(line(90, top + 70, 90, y - 40, color=MUTED, sw=1.2))

    # підказка справа
    box, _, _ = textbox(x + w + 90, top + 150,
                        "Старші біти адреси\nобирають область,\nмолодші — комірку\nвсередині неї",
                        size=10.5, pad=10, fill=F_GREY)
    p.append(box)

    render(os.path.join(OUT, "map.svg"), W, H, *p)


# ── perms: розділення дає права доступу — стіни між областями ─────────────────
def fig_perms():
    W, H = 720, 330
    p = [text(W / 2, 26, "Навіщо розділяти: стіни з різними правами", size=16, bold=True)]
    p.append(text(W / 2, 46, "кожна область має власний дозвіл — читати (R), писати (W), виконувати (X)",
                  size=10.5, color=MUTED, italic=True))

    cards = [
        ("Код", "R  X", "читати й виконувати,\nАЛЕ не переписувати", F_GLD, GOLD_LINE),
        ("Дані (SRAM)", "R  W", "читати й писати,\nАЛЕ не виконувати", F_BLUE, NEG),
        ("Периферія", "R  W", "читати й писати регістри,\nвиконувати — ніколи (XN)", F_RED, POS),
    ]
    cw, gap = 200, 30
    total = len(cards) * cw + (len(cards) - 1) * gap
    x0 = (W - total) / 2
    y = 80
    ch = 150
    for i, (t, perm, desc, fill, stroke) in enumerate(cards):
        cx = x0 + i * (cw + gap)
        p.append(rect(cx, y, cw, ch, fill=fill, stroke=stroke, sw=1.8))
        p.append(text(cx + cw / 2, y + 30, t, size=14, bold=True))
        p.append(text(cx + cw / 2, y + 62, perm, size=20, bold=True, color=stroke))
        p.append(mtext(cx + cw / 2, y + 92, desc, size=10.5, color=MUTED, lh=1.35))

    p.append(text(W / 2, y + ch + 34,
                  "Порушив дозвіл — процесор ловить помилку одразу, а не мовчки псує пам'ять",
                  size=11, color=INK))
    render(os.path.join(OUT, "perms.svg"), W, H, *p)


# ── mark1: перфострічка (команди) окремо від лічильників (дані) ───────────────
def fig_mark1():
    W, H = 760, 380
    p = [text(W / 2, 26, "Harvard Mark I: команди й дані на різних носіях", size=16, bold=True)]
    p.append(text(W / 2, 46, "не дві шини заради швидкості, а дві різні технології для двох робіт",
                  size=10.5, color=MUTED, italic=True))

    # --- Ліворуч: перфострічка команд ---
    lx = 195
    p.append(text(lx, 78, "Команди", size=14, bold=True, color=GOLD_LINE))
    p.append(text(lx, 96, "перфострічка, 24 доріжки", size=10, color=MUTED, italic=True))

    # стрічка: кілька рядів по 24 отвори, поділені на три поля по 8
    tx, ty = lx - 108, 116
    tw, rowh = 216, 26
    nrows = 5
    p.append(rect(tx, ty, tw, nrows * rowh, fill=F_GLD, stroke=GOLD_LINE, sw=1.8))
    # межі трьох полів
    p.append(line(tx + tw / 3, ty, tx + tw / 3, ty + nrows * rowh, color=GOLD_LINE, sw=1))
    p.append(line(tx + 2 * tw / 3, ty, tx + 2 * tw / 3, ty + nrows * rowh, color=GOLD_LINE, sw=1))
    # отвори: 24 у рядку (по 8 на поле)
    import random as _r
    _r.seed(7)
    for ri in range(nrows):
        cy = ty + ri * rowh + rowh / 2
        for ci in range(24):
            cx = tx + 6 + ci * ((tw - 12) / 23)
            filled = _r.random() < 0.4
            p.append(circle(cx, cy, 2.6,
                            fill=(INK if filled else BG),
                            stroke=(INK if filled else "#c9cdd3"), sw=1))
    # підписи трьох полів
    p.append(text(tx + tw / 6, ty + nrows * rowh + 16, "куди", size=9.5, color=MUTED))
    p.append(text(tx + tw / 2, ty + nrows * rowh + 16, "звідки", size=9.5, color=MUTED))
    p.append(text(tx + 5 * tw / 6, ty + nrows * rowh + 16, "що", size=9.5, color=MUTED))
    p.append(text(lx, ty + nrows * rowh + 40, "один ряд = одна команда", size=10, color=INK))
    p.append(text(lx, ty + nrows * rowh + 56, "читає по порядку, зверху вниз", size=9.5, color=MUTED, italic=True))

    # --- Праворуч: лічильники даних ---
    rx = 565
    p.append(text(rx, 78, "Дані", size=14, bold=True, color=NEG))
    p.append(text(rx, 96, "72 механічні лічильники", size=10, color=MUTED, italic=True))

    # сітка лічильників-коліщат
    gx, gy = rx - 120, 116
    cols, rows_ = 6, 4
    cell = 40
    for r2 in range(rows_):
        for c2 in range(cols):
            ccx = gx + c2 * cell + cell / 2
            ccy = gy + r2 * cell + cell / 2
            p.append(circle(ccx, ccy, 13, fill=F_BLUE, stroke=NEG, sw=1.5))
            p.append(line(ccx, ccy - 9, ccx, ccy - 3, color=NEG, sw=1.5))  # стрілка коліщата
    p.append(text(rx, gy + rows_ * cell + 24, "кожне — десяткове число (23 знаки)", size=10, color=INK))
    p.append(text(rx, gy + rows_ * cell + 40, "сам лічильник ще й додає-віднімає", size=9.5, color=MUTED, italic=True))

    # розділювач посередині
    p.append(line(W / 2, 110, W / 2, 300, color="#d7dbe0", sw=1.5, dash="4,5"))

    render(os.path.join(OUT, "mark1.svg"), W, H, *p)


if __name__ == "__main__":
    fig_buses()
    fig_map()
    fig_perms()
    fig_mark1()
    print("figs done")
