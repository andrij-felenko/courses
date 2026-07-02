# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: ELF як самоописна коробка проти голого .bin ────────────────────
def fig_overview():
    W, H = 720, 340
    frags = []

    # Ліворуч — ELF: коробка з підписаними полицями
    ex, ey, ew = 60, 70, 250
    frags.append(text(ex + ew / 2, 52, "ELF (.elf)", size=16, bold=True, color=NEG))
    rows = [
        ("Заголовок: «я ELF, ось моя карта»", FILL),
        (".text — код", "#eef3ff"),
        (".data — початкові дані", "#eef3ff"),
        (".bss — нулі (лише розмір)", "#eef3ff"),
        ("таблиця символів (імена→адреси)", "#e9f7ef"),
        ("зневадж. дані (DWARF)", "#e9f7ef"),
        ("таблиця секцій: що де лежить", FILL),
    ]
    rh = 32
    y = ey
    for label, col in rows:
        frags.append(fitbox(ex, y, ew, rh - 4, label, size=12, fill=col))
        y += rh

    # Праворуч — голий .bin: суцільна смуга байтів
    bx, by, bw = 470, 70, 190
    frags.append(text(bx + bw / 2, 52, "голий образ (.bin)", size=16, bold=True, color=POS))
    frags.append(rect(bx, by, bw, rh * 7 - 4, fill="#fdecea", stroke=POS))
    frags.append(mtext(bx + bw / 2, by + 92,
                       ["самі байти,", "рядком, без міток:", "де код, де дані —", "ніде не написано"],
                       size=13, color=INK))

    # Стрілка перетворення
    frags.append(arrow(ex + ew + 12, H / 2 + 8, bx - 12, H / 2 + 8, color=INK, sw=2))
    frags.append(text((ex + ew + bx) / 2, H / 2 - 6, "objcopy", size=12, bold=True, color=MUTED))
    frags.append(text((ex + ew + bx) / 2, H / 2 + 30, "викидає все зайве", size=11, color=MUTED))

    render(os.path.join(IMG, 'overview.svg'), W, H, *frags)


# ── Фігура 2: два погляди на ті самі байти — секції й сегменти ────────────────
def fig_two_views():
    W, H = 720, 330
    frags = []
    frags.append(text(W / 2, 30, "Ті самі байти — два погляди", size=16, bold=True))

    # Спільна смуга даних посередині
    dx, dw = 90, 540
    dy, dh = 150, 46
    frags.append(rect(dx, dy, dw, dh, fill="#f0f0f0", stroke=LINE))
    # умовні кордони всередині
    for fx in (dx + 150, dx + 300, dx + 420):
        frags.append(line(fx, dy, fx, dy + dh, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(W / 2, dy + dh / 2 + 5, "байти образу", size=12, color=MUTED))

    # Погляд лінкера — секції (згори): дрібні іменовані шматки
    secs = [(".text", dx, 150), (".rodata", dx + 150, 60),
            (".data", dx + 210, 90), (".symtab", dx + 300, 120),
            (".debug", dx + 420, 120)]
    for name, x, w in secs:
        frags.append(fitbox(x, 78, w - 4, 28, name, size=11, fill="#eef3ff", stroke=NEG))
    frags.append(text(dx - 8, 92, "секції", size=13, bold=True, color=NEG, anchor="end"))
    frags.append(text(dx - 8, 110, "(лінкер)", size=10, color=MUTED, anchor="end"))
    for name, x, w in secs:
        frags.append(line(x + w / 2, 106, x + w / 2, dy, color=NEG, sw=0.8, dash="2,3"))

    # Погляд завантажувача — сегменти (знизу): великі шматки з правами
    segs = [("LOAD  R-X (код)", dx, 210), ("LOAD  RW- (дані)", dx + 210, 210)]
    for name, x, w in segs:
        frags.append(fitbox(x, dy + dh + 26, w - 4, 30, name, size=12, fill="#e9f7ef", stroke=FIELD))
    frags.append(text(dx - 8, dy + dh + 44, "сегменти", size=13, bold=True, color=FIELD, anchor="end"))
    frags.append(text(dx - 8, dy + dh + 62, "(завантажувач)", size=10, color=MUTED, anchor="end"))
    for name, x, w in segs:
        frags.append(line(x + w / 2, dy + dh, x + w / 2, dy + dh + 26, color=FIELD, sw=0.8, dash="2,3"))

    render(os.path.join(IMG, 'two-views.svg'), W, H, *frags)


# ── Фігура 3: конвеєр — ELF для збірки/зневадження, .bin у чіп ────────────────
def fig_pipeline():
    W, H = 720, 300
    frags = []

    # ELF у центрі-ліворуч
    b, w, h = textbox(150, 150, ["elf: код + дані +", "символи + DWARF"], size=13,
                      fill="#eef3ff", stroke=NEG)
    frags.append(b)
    frags.append(text(150, 150 - h / 2 - 12, "лінкер видає", size=11, color=MUTED))

    # Гілка вгору — зневаджувач (тримає символи)
    b2, w2, h2 = textbox(560, 78, ["зневаджувач (GDB):", "адреса → ім'я, рядок"], size=12,
                         fill="#e9f7ef", stroke=FIELD)
    frags.append(b2)
    frags.append(arrow(150 + w / 2 + 6, 130, 560 - w2 / 2 - 6, 90, color=FIELD, sw=1.8))
    frags.append(text(360, 96, "увесь ELF (з символами)", size=11, color=FIELD))

    # Гілка вниз — objcopy → .bin → чіп (символи відкинуто)
    b3, w3, h3 = textbox(430, 225, [".bin: самі байти", "коду й даних"], size=12,
                         fill="#fdecea", stroke=POS)
    frags.append(b3)
    frags.append(arrow(150 + w / 2 + 6, 175, 430 - w3 / 2 - 6, 215, color=POS, sw=1.8))
    frags.append(text(300, 214, "objcopy: лишає", size=11, color=POS))
    frags.append(text(300, 230, "лише байти у Flash", size=11, color=POS))

    b4, w4, h4 = textbox(640, 225, ["Flash", "чипа"], size=13, fill=FILL)
    frags.append(b4)
    frags.append(arrow(430 + w3 / 2 + 6, 225, 640 - w4 / 2 - 6, 225, color=INK, sw=1.8))

    render(os.path.join(IMG, 'pipeline.svg'), W, H, *frags)


# ── Фігура 4 (hist): родовід форматів a.out → COFF → ELF ─────────────────────
def fig_lineage():
    W, H = 720, 380
    frags = []
    frags.append(text(W / 2, 30, "Родовід форматів об'єктних файлів UNIX", size=16, bold=True))

    # Три покоління — вертикальні картки з підписом-роком і головною межею
    cards = [
        (55, "a.out", "1971",
         ["«assembler output»", "фіксована структура,", "без іменованих секцій"],
         "#fdecea", POS,
         ["тісно: спільні", "бібліотеки не влазять"]),
        (285, "COFF", "1983",
         ["перші іменовані", "секції; ще заскладний", "для динаміки"],
         FILL, MUTED,
         ["динамічні", "бібліотеки — мука"]),
        (515, "ELF", "1988",
         ["довільні секції +", "погляд-сегменти;", "процесор у заголовку"],
         "#eef3ff", NEG,
         ["гнучкий, незалежний", "від ядра"]),
    ]
    cw = 150
    cy = 70
    ch = 132
    for x, name, year, body, fill, edge, tail in cards:
        frags.append(rect(x, cy, cw, ch, fill=fill, stroke=edge))
        frags.append(text(x + cw / 2, cy + 26, name, size=17, bold=True, color=edge))
        frags.append(text(x + cw / 2, cy + 44, year, size=12, color=MUTED))
        frags.append(mtext(x + cw / 2, cy + 68, body, size=11, color=INK, lh=1.25))
        b, _, _ = textbox(x + cw / 2, cy + ch + 34, tail, size=11, fill=BG, stroke=edge)
        frags.append(b)

    # Стрілки поколінь
    frags.append(arrow(55 + cw + 6, cy + ch / 2, 285 - 6, cy + ch / 2, color=INK, sw=2))
    frags.append(arrow(285 + cw + 6, cy + ch / 2, 515 - 6, cy + ch / 2, color=INK, sw=2))

    # Нижня смуга — стандартизація TIS
    b, _, _ = textbox(W / 2, cy + ch + 96,
                      ["1993: комітет TIS робить ELF спільним стандартом",
                       "(v1.1 — жовтень 1993; v1.2 — травень 1995)"],
                      size=12, fill="#e9f7ef", stroke=FIELD)
    frags.append(b)

    render(os.path.join(IMG, 'lineage.svg'), W, H, *frags)


# ── Фігура (comp-dwarf): сім'я секцій .debug_* і як GDB читає адресу ──────────
def fig_dwarf_sections():
    W, H = 720, 400
    frags = []
    frags.append(text(W / 2, 30, "DWARF: секції .debug_* усередині ELF", size=16, bold=True))

    ex, ey, ew = 50, 66, 250
    frags.append(text(ex + ew / 2, 56, "ELF: секції .debug_*", size=13, bold=True, color=NEG))
    rows = [
        (".debug_info", "дерево описів (DIE):", "функції, типи, змінні"),
        (".debug_abbrev", "словник скорочень", "для .debug_info"),
        (".debug_line", "програма-автомат:", "адреса → файл:рядок"),
        (".debug_str", "спільний пул", "імен-рядків"),
        (".debug_frame", "як розкрутити", "стек викликів"),
    ]
    rh = 56
    y = ey
    for name, l1, l2 in rows:
        frags.append(rect(ex, y, ew, rh - 6, fill="#eef3ff", stroke=NEG, sw=1))
        frags.append(text(ex + 10, y + 20, name, size=12, bold=True, color=NEG, anchor="start"))
        frags.append(text(ex + 10, y + 36, l1, size=10.5, color=INK, anchor="start"))
        frags.append(text(ex + 10, y + 49, l2, size=10.5, color=MUTED, anchor="start"))
        y += rh

    gx = 430
    b0, w0, h0 = textbox(gx + 80, 96, ["процесор став на", "адресі 0x0800_4a12"],
                         size=12, fill="#fdecea", stroke=POS)
    frags.append(b0)

    b1, w1, h1 = textbox(gx + 80, 214,
                         ["GDB читає DWARF", "і перекладає:", "",
                          "blink(),  led.c:42", "count == 7"],
                         size=12, fill="#e9f7ef", stroke=FIELD)
    frags.append(b1)
    frags.append(arrow(gx + 80, 96 + h0 / 2 + 4, gx + 80, 214 - h1 / 2 - 4, color=FIELD, sw=1.8))
    frags.append(text(gx + 80, 160, "через DWARF", size=11, color=FIELD))

    frags.append(arrow(ex + ew + 8, ey + rh * 2.5, gx - 12, 150, color=INK, sw=1.6))

    render(os.path.join(IMG, 'dwarf-sections.svg'), W, H, *frags)


# ── Фігура (comp-dwarf): дерево DIE й таблиця адреса↔рядок ────────────────────
def fig_dwarf_die():
    W, H = 720, 400
    frags = []
    frags.append(text(W / 2, 30, "Що кодує DWARF: дерево описів і карта рядків", size=16, bold=True))

    frags.append(text(175, 58, ".debug_info — дерево DIE", size=13, bold=True, color=NEG))
    b, bw, bh = textbox(175, 92, "модуль led.c", size=11, fill=FILL, stroke=NEG)
    frags.append(b)
    fb, fbw, fbh = textbox(175, 156, "функція blink()", size=11, fill="#eef3ff", stroke=NEG)
    frags.append(fb)
    frags.append(line(175, 92 + bh / 2, 175, 156 - fbh / 2, color=NEG, sw=1))
    kids = [("змінна count", 85, 240, "#eef3ff"),
            ("тип int (4 б)", 275, 240, "#e9f7ef"),
            ("змінна led_pin", 95, 300, "#eef3ff"),
            ("область { }", 275, 300, FILL)]
    for label, cx, cy, col in kids:
        kb, kbw, kbh = textbox(cx, cy, label, size=10.5, fill=col, stroke=MUTED, sw=1)
        frags.append(kb)
    frags.append(line(175, 156 + fbh / 2, 85, 240 - 14, color=NEG, sw=0.8))
    frags.append(line(175, 156 + fbh / 2, 275, 240 - 14, color=NEG, sw=0.8))
    frags.append(line(175, 156 + fbh / 2, 95, 300 - 14, color=NEG, sw=0.8))
    frags.append(text(175, 356, "кожен вузол — тег + атрибути", size=10, color=MUTED, italic=True))

    tx, tw = 428, 252
    frags.append(text(tx + tw / 2, 58, ".debug_line — карта адреса↔рядок", size=12.5, bold=True, color=FIELD))
    rows = [("адреса", "файл:рядок"),
            ("0x0800_4a00", "led.c:40"),
            ("0x0800_4a0c", "led.c:41"),
            ("0x0800_4a12", "led.c:42"),
            ("0x0800_4a1e", "led.c:43")]
    ry, rhh = 74, 44
    for i, (a, s) in enumerate(rows):
        hd = (i == 0)
        col = "#e9f7ef" if hd else (BG if i % 2 else "#f4faf6")
        frags.append(rect(tx, ry, tw, rhh, fill=col, stroke=FIELD if hd else LINE, sw=1 if hd else 0.6))
        hit = a.startswith("0x0800_4a12")
        frags.append(text(tx + 12, ry + rhh / 2 + 5, a, size=11.5, bold=hd or hit,
                          color=(POS if hit else INK), anchor="start"))
        frags.append(text(tx + 140, ry + rhh / 2 + 5, s, size=11.5, bold=hd or (s == "led.c:42"),
                          color=(POS if s == "led.c:42" else INK), anchor="start"))
        ry += rhh
    frags.append(text(tx + tw / 2, ry + 20, "автомат розгортає код у цю таблицю", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, 'dwarf-die.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_overview()
    fig_two_views()
    fig_pipeline()
    fig_lineage()
    fig_dwarf_sections()
    fig_dwarf_die()
    print("figures written")
