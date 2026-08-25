# -*- coding: utf-8 -*-
"""Фігури до теми «Карта пам'яті» (і до вставки comp-real-memory-map).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── спільний примітив: смуга-регіон на вертикальному стовпчику адрес ─────────
def region(x, y, w, h, label, ro, fill):
    """Смуга регіону: рамка + назва + позначка RO/RW справа всередині."""
    out = rect(x, y, w, h, fill=fill, stroke=INK, sw=1.4, rx=3)
    out += text(x + 12, y + h / 2 + 4, label, size=12, color=INK, anchor="start", bold=True)
    tag = "RO" if ro else "RW"
    col = MUTED if ro else FIELD
    out += text(x + w - 12, y + h / 2 + 4, tag, size=10, color=col, anchor="end", bold=True)
    return out


# ── fig map: адресний простір поділено на регіони ───────────────────────────
# Ідея: один стовпчик адрес від 0 угору; незмінне внизу, мінливе вгорі; купа й
# стек ростуть назустріч у спільний вільний простір.
def fig_map():
    W, H = 700, 470
    cx = W / 2
    bw = 300
    bx = cx - bw / 2
    top = 60
    p = []

    # вісь адрес зліва зі стрілкою «вищі адреси вгору»
    ax = bx - 38
    p.append(arrow(ax, H - 40, ax, top - 8, color=MUTED, sw=1.6))
    p.append(text(ax - 6, top + 4, "вищі", size=10, color=MUTED, anchor="end"))
    p.append(text(ax - 6, top + 18, "адреси", size=10, color=MUTED, anchor="end"))
    p.append(text(ax - 6, H - 44, "0", size=12, color=MUTED, anchor="end", bold=True))

    # регіони згори вниз (вищі адреси — вгорі)
    rows = [
        ("стек ↓", False, "#fdecea", 46),
        ("вільний простір", None, "#fafafa", 92),
        ("купа ↑", False, "#eafaf0", 46),
        (".bss", False, "#eafaf0", 40),
        (".data", False, "#eafaf0", 40),
        (".rodata", True, "#eef2f7", 40),
        (".text", True, "#eef2f7", 40),
    ]
    y = top
    band = {}
    for lab, ro, fill, h in rows:
        if ro is None:
            p.append(rect(bx, y, bw, h, fill=fill, stroke="#cccccc", sw=1.2, rx=3))
            p.append(text(cx, y + h / 2 + 4, lab, size=11, color=MUTED, italic=True))
        else:
            p.append(region(bx, y, bw, h, lab, ro, fill))
        band[lab] = (y, h)
        y += h

    # стрілки росту стека (вниз) і купи (вгору) у вільний простір
    fy, fh = band["вільний простір"]
    p.append(arrow(cx, fy + 6, cx, fy + fh - 6, color=POS, sw=2.0))
    p.append(arrow(cx, fy + fh - 6, cx, fy + 6, color=FIELD, sw=2.0))

    # підписи-групи праворуч
    rx = bx + bw + 16
    p.append(text(rx, top + 60, "ростуть", size=10, color=INK, anchor="start"))
    p.append(text(rx, top + 74, "назустріч", size=10, color=INK, anchor="start"))
    ty, th = band[".text"]
    p.append(text(rx, ty + th / 2 + 4, "незмінне (RO)", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "map.svg"), W, H, *p,
           title="Адресний простір поділено на регіони")


# ── fig regions: таблиця — що тримає кожен регіон ───────────────────────────
# Ідея: шпаргалка «регіон → що лежить → RO/RW → де живе фізично».
def fig_regions():
    W, H = 720, 360
    p = []
    x0 = 30
    cols = [("Регіон", 110), ("Що лежить", 300), ("Доступ", 90), ("Де живе", 150)]
    rowh = 38
    y = 56

    # шапка
    x = x0
    for name, w in cols:
        p.append(rect(x, y, w, rowh, fill="#eef2f7", stroke=INK, sw=1.3, rx=0))
        p.append(text(x + w / 2, y + rowh / 2 + 4, name, size=11, color=INK, bold=True))
        x += w
    y += rowh

    rows = [
        (".text", "інструкції програми", "RO", "Flash"),
        (".rodata", "сталі: рядки, таблиці", "RO", "Flash"),
        (".data", "глобальні з початковим значенням", "RW", "RAM"),
        (".bss", "глобальні, нульові на старті", "RW", "RAM"),
        ("купа", "динамічні дані на запит ↑", "RW", "RAM"),
        ("стек", "виклики й локальні ↓", "RW", "RAM"),
    ]
    for reg, what, acc, where in rows:
        x = x0
        vals = [reg, what, acc, where]
        for (name, w), v in zip(cols, vals):
            ro = (acc == "RO")
            fill = "#eef2f7" if ro else "#f6fbf7"
            p.append(rect(x, y, w, rowh, fill=fill, stroke="#d0d5db", sw=1.0, rx=0))
            anchor = "start" if name in ("Що лежить",) else "middle"
            tx = x + 10 if anchor == "start" else x + w / 2
            col = INK
            if name == "Доступ":
                col = MUTED if ro else FIELD
            p.append(text(tx, y + rowh / 2 + 4, v, size=11, color=col, anchor=anchor,
                          bold=(name in ("Регіон", "Доступ"))))
            x += w
        y += rowh

    p.append(text(W / 2, y + 24, "RO (незмінне) — у Flash; RW (змінне) — у RAM",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "regions.svg"), W, H, *p,
           title="Що тримає кожен регіон")


# ── fig grow: стек і купа ростуть назустріч ─────────────────────────────────
# Ідея: один спільний запас, два рухливі пожильці з протилежних кінців;
# зійшлися — зіткнення.
def fig_grow():
    W, H = 700, 320
    p = []
    bx, bw = 120, 460
    top, bot = 70, 250

    # рамка вільного простору
    p.append(rect(bx, top, bw, bot - top, fill="#fafafa", stroke="#cccccc", sw=1.2, rx=4))

    # стек згори
    sh = 54
    p.append(rect(bx, top, bw, sh, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    p.append(text(bx + bw / 2, top + sh / 2 + 4, "стек — виклики, локальні", size=12, color=INK, bold=True))
    p.append(arrow(bx + bw / 2, top + sh + 6, bx + bw / 2, top + sh + 46, color=POS, sw=2.2))
    p.append(text(bx + bw / 2 + 12, top + sh + 30, "росте вниз", size=11, color=POS, anchor="start", bold=True))

    # купа знизу
    hh = 54
    p.append(rect(bx, bot - hh, bw, hh, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(bx + bw / 2, bot - hh / 2 + 4, "купа — динамічні дані", size=12, color=INK, bold=True))
    p.append(arrow(bx + bw / 2, bot - hh - 6, bx + bw / 2, bot - hh - 46, color=FIELD, sw=2.2))
    p.append(text(bx + bw / 2 + 12, bot - hh - 28, "росте вгору", size=11, color=FIELD, anchor="start", bold=True))

    # спільний запас у центрі
    p.append(text(bx + bw / 2, (top + sh + bot - hh) / 2 + 4, "спільний вільний простір",
                  size=11, color=MUTED, italic=True))

    # попередження про зіткнення
    p.append(text(W / 2, bot + 40, "зійдуться — зіткнення (переповнення)",
                  size=12, color=POS, bold=True))

    render(os.path.join(IMG, "grow.svg"), W, H, *p,
           title="Два рухливі регіони ділять один запас")


# ── fig mcu: карта МК — Flash, RAM, периферія в різних діапазонах ────────────
# Ідея: на МК регіони фізично розкладені по різних видах пам'яті + окремий
# діапазон периферії (регістри, не пам'ять).
def fig_mcu():
    W, H = 700, 420
    p = []
    cx = W / 2
    bw = 240
    bx = cx - bw / 2
    top = 58

    blocks = [
        ("периферія", "регістри керування\n(GPIO, таймери, UART)", "#fdf6e3", "#b8860b", 78),
        ("RAM (SRAM)", ".data · .bss · купа · стек\nлетка, швидка", "#eafaf0", FIELD, 92),
        ("Flash", ".text (код) · .rodata (сталі)\nнелетка, постійна", "#eef2f7", NEG, 92),
    ]
    # «дірки» між блоками — порожні діапазони адрес
    gap = 30
    y = top
    for title, sub, fill, col, h in blocks:
        p.append(rect(bx, y, bw, h, fill=fill, stroke=col, sw=1.8, rx=5))
        p.append(text(cx, y + 24, title, size=14, color=INK, bold=True))
        p.append(mtext(cx, y + 44, sub, size=10.5, color=MUTED))
        y += h
        if (title, sub) != (blocks[-1][0], blocks[-1][1]):
            p.append(text(cx, y + gap / 2 + 4, "· · ·  незайнятий простір  · · ·",
                          size=9.5, color="#b0b0b0", italic=True))
            y += gap

    # підпис: різні діапазони адрес
    rx = bx + bw + 18
    p.append(text(rx, top + 40, "окремі", size=10, color=INK, anchor="start"))
    p.append(text(rx, top + 54, "діапазони", size=10, color=INK, anchor="start"))
    p.append(text(rx, top + 68, "адрес", size=10, color=INK, anchor="start"))

    p.append(text(W / 2, y + 26, "та сама числова адреса у Flash і в RAM — різні комірки",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "mcu.svg"), W, H, *p,
           title="На МК: Flash, RAM і периферія — у різних діапазонах")


# ── fig mmio: пам'ять-відображений ввід-вивід ───────────────────────────────
# Ідея: та сама команда ST за «звичайною» адресою кладе в RAM, а за адресою
# периферії — смикає залізо (світлодіод).
def fig_mmio():
    W, H = 720, 320
    p = []
    # ядро зліва
    core, cw, ch = textbox(90, 150, "ядро\nST r, [адреса]", size=12, bold=True,
                           fill="#eef2f7", stroke=INK, sw=1.8, pad=12)
    p.append(core)

    # дві адреси-цілі праворуч
    ax = 420
    # RAM
    ramb = rect(ax, 60, 220, 70, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=5)
    p.append(ramb)
    p.append(text(ax + 110, 90, "адреса в RAM", size=12, color=INK, bold=True))
    p.append(text(ax + 110, 112, "→ значення лягло у змінну", size=10.5, color=MUTED))

    # периферія
    perb = rect(ax, 180, 220, 70, fill="#fdf6e3", stroke="#b8860b", sw=1.6, rx=5)
    p.append(perb)
    p.append(text(ax + 110, 210, "адреса периферії", size=12, color=INK, bold=True))
    p.append(text(ax + 110, 232, "→ регістр смикнув залізо", size=10.5, color=MUTED))

    # стрілки від ядра
    p.append(arrow(90 + cw / 2, 150, ax - 4, 95, color=FIELD, sw=1.8))
    p.append(arrow(90 + cw / 2, 150, ax - 4, 215, color="#b8860b", sw=1.8))

    # світлодіод як наслідок
    p.append(circle(ax + 250, 215, 12, fill="#fff3b0", stroke="#b8860b", sw=2))
    for a in range(0, 360, 45):
        import math
        rad = math.radians(a)
        x1 = ax + 250 + 16 * math.cos(rad)
        y1 = 215 + 16 * math.sin(rad)
        x2 = ax + 250 + 24 * math.cos(rad)
        y2 = 215 + 24 * math.sin(rad)
        p.append(line(x1, y1, x2, y2, color="#b8860b", sw=1.6))

    p.append(text(W / 2, H - 16, "та сама команда — різний наслідок, бо різна адреса",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "mmio.svg"), W, H, *p,
           title="Пам'ять-відображений ввід-вивід: адреса вирішує")


# ── fig ladder (вставка): карта в RM — один стовпчик адрес, три потрібні ─────
def fig_ladder():
    W, H = 640, 470
    p = []
    cx = 250
    bw = 260
    bx = cx - bw / 2
    top, bot = 58, 430

    p.append(rect(bx, top, bw, bot - top, fill="#fafafa", stroke="#cccccc", sw=1.2, rx=4))
    # межі адрес
    p.append(text(bx - 10, top + 6, "0xFFFF_FFFF", size=10, color=MUTED, anchor="end"))
    p.append(text(bx - 10, bot, "0x0000_0000", size=10, color=MUTED, anchor="end"))

    # три зайняті смуги + дірки між ними
    bands = [
        ("периферія", "регістри заліза", "#fdf6e3", "#b8860b", 70, 60),
        ("SRAM", "змінні, стек, купа", "#eafaf0", FIELD, 195, 70),
        ("Flash / ROM", "код, сталі", "#eef2f7", NEG, 320, 70),
    ]
    for lab, sub, fill, col, y, h in bands:
        p.append(rect(bx, y, bw, h, fill=fill, stroke=col, sw=1.8, rx=4))
        p.append(text(cx, y + 26, lab, size=13, color=INK, bold=True))
        p.append(text(cx, y + 46, sub, size=10, color=MUTED))

    # «дірки»
    for yy in (130, 265):
        p.append(text(cx, yy, "· · · дірка (пам'яті немає) · · ·",
                      size=9.5, color="#b0b0b0", italic=True))

    # праворуч — підпис «три потрібні адреси»
    rx = bx + bw + 22
    p.append(text(rx, top + 20, "щодня потрібні", size=11, color=INK, anchor="start", bold=True))
    p.append(text(rx, top + 38, "лише три:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(rx, 95, "→ де периферія", size=10, color="#b8860b", anchor="start"))
    p.append(text(rx, 230, "→ де SRAM", size=10, color=FIELD, anchor="start"))
    p.append(text(rx, 355, "→ де Flash", size=10, color=NEG, anchor="start"))

    render(os.path.join(IMG, "ladder.svg"), W, H, *p,
           title="Карта в reference manual — стовпчик адрес")


# ── fig rmrow (вставка): як читати один рядок таблиці memory map ─────────────
def fig_rmrow():
    W, H = 720, 340
    p = []
    x0 = 30
    cols = [("ім'я", 130), ("base address", 180), ("end address", 180), ("доступ / шина", 170)]
    rowh = 40
    y = 70

    # шапка
    x = x0
    for name, w in cols:
        p.append(rect(x, y, w, rowh, fill="#eef2f7", stroke=INK, sw=1.3, rx=0))
        p.append(text(x + w / 2, y + rowh / 2 + 4, name, size=11, color=INK, bold=True))
        x += w
    y += rowh

    rows = [
        ("Flash", "0x0800_0000", "0x080F_FFFF", "R / шина команд"),
        ("SRAM1", "0x2000_0000", "0x2002_FFFF", "R/W / шина даних"),
        ("Peripheral", "0x4000_0000", "0x5FFF_FFFF", "R/W / шина даних"),
    ]
    for nm, base, end, acc in rows:
        x = x0
        for (name, w), v in zip(cols, (nm, base, end, acc)):
            p.append(rect(x, y, w, rowh, fill=BG, stroke="#d0d5db", sw=1.0, rx=0))
            mono = name in ("base address", "end address")
            p.append(text(x + w / 2, y + rowh / 2 + 4, v, size=11 if not mono else 12,
                          color=INK, bold=(name == "ім'я")))
            x += w
        y += rowh

    # пояснення під таблицею
    p.append(text(x0, y + 28, "розмір = end − base + 1", size=12, color=POS, anchor="start", bold=True))
    p.append(text(x0, y + 50,
                  "напр. SRAM1: 0x2002_FFFF − 0x2000_0000 + 1 = 0x30000 = 196 608 Б ≈ 192 КБ",
                  size=10.5, color=MUTED, anchor="start"))
    p.append(text(x0, y + 70, "шина команд = код-простір · шина даних = пам'ять даних (Гарвард наживо)",
                  size=10, color=MUTED, anchor="start", italic=True))

    render(os.path.join(IMG, "rmrow.svg"), W, H, *p,
           title="Один рядок таблиці «Memory map»: чотири поля")


if __name__ == "__main__":
    fig_map()
    fig_regions()
    fig_grow()
    fig_mcu()
    fig_mmio()
    fig_ladder()
    fig_rmrow()
    print("OK: figures written to", IMG)
