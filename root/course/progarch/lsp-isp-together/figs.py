# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «LSP та ISP разом».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ───────── Фіг. 1: товстий інтерфейс → вимушена брехня → небезпечна підстановка ─────────
def fig_fat_interface():
    W, H = 940, 430
    f = [text(W / 2, 34, "Товстий інтерфейс сам виробляє порушення LSP", size=17, bold=True)]

    cy = 178
    # три стадії ланцюжка (кожна — своя рамка), центри по x
    fa, wa, ha = textbox(175, cy,
                         "Товстий IDevice\n \nread() · turnOn()\nlock() · startStream()",
                         size=13, fill="#eef1f4", stroke=MUTED, color=INK, bold=False)
    fb, wb, hb = textbox(470, cy,
                         "Датчик температури\nмусить реалізувати\nturnOn / lock / stream —\nяких він не вміє",
                         size=13, fill="#fdecea", stroke=POS, color=INK)
    fc, wc, hc = textbox(765, cy,
                         "throw «не підтримую»\nабо порожнє тіло →\nклієнт, що довірився\nIDevice, дістає сюрприз",
                         size=13, fill="#fdecea", stroke=POS, color=INK)

    # стрілки між рамками (від правого краю до лівого краю сусіда)
    f.append(arrow(175 + wa / 2, cy, 470 - wb / 2, cy, color=INK, sw=2.0))
    f.append(arrow(470 + wb / 2, cy, 765 - wc / 2, cy, color=INK, sw=2.0))
    f.extend([fa, fb, fc])

    # підписи стадій під рамками
    yl = cy + ha / 2 + 24
    f.append(text(175, yl, "ISP ✗ — усе в одному типі", size=12, bold=True, color=MUTED))
    f.append(text(470, yl, "вимушена нечесність", size=12, bold=True, color=POS))
    f.append(text(765, yl, "LSP ✗ — підстановка небезпечна", size=12, bold=True, color=POS))

    # висновок-смуга внизу
    f.append(fitbox(70, 330, W - 140, 70,
                    "Товстий інтерфейс — це фабрика порушень LSP: коли тип обіцяє більше, ніж реалізатор здатен чесно виконати,\n"
                    "кожному реалізатору лишається або брехати порожнім тілом, або падати винятком — і те, і те ламає підстановку.",
                    size=13, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "fat-interface-lsp.svg"), W, H, *f)


# ───────── Фіг. 2: розріз по здатностях лікує обидві рани ─────────
def fig_segregate():
    W, H = 1000, 470
    f = [text(W / 2, 34, "Розріз по здатностях лікує обидві рани одним рухом", size=17, bold=True)]

    # заголовки колонок
    f.append(text(260, 84, "ДО: один товстий IDevice", size=14, bold=True, color=POS))
    f.append(text(740, 84, "ПІСЛЯ: вузькі здатності", size=14, bold=True, color=FIELD))
    f.append(text(740, 110, "Readable · Switchable · Lockable · Streamable",
                  size=12, color=MUTED))

    # вертикальна межа між колонками
    f.append(line(500, 96, 500, 348, color="#c8ced6", sw=1.4))

    left = [
        "Датчик t°  —  чесно read()  ·  turnOn / lock / stream: throw",
        "Розетка  —  чесно turnOn / read  ·  lock / stream: throw",
        "Камера  —  чесно startStream  ·  read / turnOn / lock: throw",
    ]
    right = [
        "Датчик t°   →   Readable",
        "Розетка   →   Readable + Switchable",
        "Камера   →   Streamable",
    ]
    ys = [136, 208, 280]
    for s, y in zip(left, ys):
        f.append(fitbox(46, y, 424, 60, s, size=13, fill="#fdecea", stroke=POS, color=INK))
    for s, y in zip(right, ys):
        f.append(fitbox(528, y, 424, 60, s, size=13, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))

    f.append(fitbox(70, 372, W - 140, 66,
                    "Той самий розріз прибрав вимушену реалізацію (ISP ✓) і повернув чесну підстановку (LSP ✓):\n"
                    "жоден пристрій уже не стоїть за обіцянкою, якої не тримає, — а клієнт питає рівно ту здатність, що потрібна.",
                    size=13, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "segregate-capabilities.svg"), W, H, *f)


# ───────── Фіг. 3 (проєкт): матриця здатностей + диспетч хаба на межі ─────────
def fig_capability_matrix():
    W, H = 950, 440
    f = [text(W / 2, 34, "Матриця здатностей: хаб командує лише крізь наявну здатність",
              size=17, bold=True)]

    dev_x, dev_w = 24, 170
    caps = ["Readable", "Switchable", "Lockable", "Streamable"]
    cap_w = 128
    cap_x0 = dev_x + dev_w                 # 194
    call_x = cap_x0 + len(caps) * cap_w    # 706
    call_w = 214                           # 706..920

    head_y, head_h = 58, 50
    row_h = 56
    rows_y0 = head_y + head_h              # 108
    devices = ["Давач t°", "Розетка", "Замок", "Камера"]

    impl = {
        "Давач t°": {"Readable"},
        "Розетка":  {"Readable", "Switchable"},
        "Замок":    {"Lockable"},
        "Камера":   {"Streamable"},
    }
    calls = {
        "Давач t°": "— пропущено",
        "Розетка":  "turnOff()",
        "Замок":    "lock()",
        "Камера":   "startStream()",
    }

    # шапка
    f.append(fitbox(dev_x, head_y, dev_w, head_h, "пристрій ↓",
                    size=12, fill="#eef1f4", stroke=MUTED, color=MUTED, bold=True))
    for i, c in enumerate(caps):
        f.append(fitbox(cap_x0 + i * cap_w, head_y, cap_w, head_h, c,
                        size=13, fill="#eef1f4", stroke=MUTED, color=INK, bold=True))
    f.append(fitbox(call_x, head_y, call_w, head_h, "nightMode кличе",
                    size=13, fill="#eef1f4", stroke=MUTED, color=INK, bold=True))

    # рядки-пристрої
    for r, dev in enumerate(devices):
        y = rows_y0 + r * row_h
        f.append(fitbox(dev_x, y, dev_w, row_h, dev,
                        size=13, fill=FILL, stroke=MUTED, color=INK, bold=True))
        for i, c in enumerate(caps):
            x = cap_x0 + i * cap_w
            if c in impl[dev]:
                f.append(fitbox(x, y, cap_w, row_h, "✓",
                                size=20, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
            else:
                f.append(fitbox(x, y, cap_w, row_h, "·",
                                size=15, fill="#fbfcfd", stroke="#e2e6ea", color="#c8ced6"))
        skipped = (dev == "Давач t°")
        f.append(fitbox(call_x, y, call_w, row_h, calls[dev], size=13,
                        fill=("#fdf3f0" if skipped else "#eafaf0"),
                        stroke=(MUTED if skipped else FIELD),
                        color=(MUTED if skipped else INK), bold=not skipped))

    by = rows_y0 + len(devices) * row_h + 14      # 108 + 224 + 14 = 346
    f.append(fitbox(24, by, W - 48, 76,
                    "Хаб не питає «якого ти типу?» — він питає «чи вмієш?». Давач має лише Readable, якої нічний режим не чіпає,\n"
                    "тож його мовчки пропускають — кинути виняток о третій ночі просто нема звідки.",
                    size=13, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "capability-matrix.svg"), W, H, *f)


# ───────── Фіг. 4 (вставка hist): система друку Xerox — до і після ─────────
def fig_xerox_job():
    W, H = 1080, 520
    f = [text(540, 30, "Система друку Xerox: товстий Job — і розтин на клієнтські інтерфейси",
              size=16, bold=True)]

    # заголовки колонок
    f.append(text(285, 66, "ДО", size=15, bold=True, color=POS))
    f.append(text(285, 88, "усе в одному класі Job", size=12, color=MUTED))
    f.append(text(800, 66, "ПІСЛЯ", size=15, bold=True, color=FIELD))
    f.append(text(800, 88, "інтерфейс на кожен тип задачі, зшитий через DIP", size=12, color=MUTED))

    # вертикальна межа між колонками
    f.append(line(540, 104, 540, 428, color="#c8ced6", sw=1.4))

    # ── ЛІВОРУЧ: три клієнти → один товстий Job ──
    cxs = [165, 285, 405]
    labels = ["Клієнт\nдруку", "Клієнт\nстеплера", "Клієнт\nфаксу"]
    cbot = 134
    for cx, lb in zip(cxs, labels):
        fr, w, h = textbox(cx, 134, lb, size=11, fill=FILL, stroke=MUTED, color=INK)
        f.append(fr)
        cbot = 134 + h / 2
    jb, jw, jh = textbox(285, 296,
                         "Job  (товстий)\nprint · staple · fax\nscan · queue\ncancel · status · …",
                         size=12, fill="#fdecea", stroke=POS, color=INK)
    jtop = 296 - jh / 2
    for cx, aim in zip(cxs, [285 - jw * 0.30, 285, 285 + jw * 0.30]):
        f.append(arrow(cx, cbot + 7, aim, jtop - 5, color=INK, sw=1.6))
    f.append(jb)
    f.append(text(285, 374, "найдрібніша зміна Job →", size=11, bold=True, color=POS))
    f.append(text(285, 393, "~1 година перезбирання й розгортання", size=11, color=POS))

    # ── ПРАВОРУЧ: клієнт → свій вузький інтерфейс → один Job, що реалізує всі ──
    rxs = [660, 800, 940]
    rlabels = ["Клієнт\nдруку", "Клієнт\nстеплера", "Клієнт\nфаксу"]
    ifaces = ["«PrintJob»", "«StapleJob»", "«FaxJob»"]
    rc_bot, if_top, if_bot = {}, {}, {}
    for cx, lb in zip(rxs, rlabels):
        fr, w, h = textbox(cx, 130, lb, size=11, fill=FILL, stroke=MUTED, color=INK)
        f.append(fr)
        rc_bot[cx] = 130 + h / 2
    for cx, nm in zip(rxs, ifaces):
        fr, w, h = textbox(cx, 228, nm, size=12, fill="#eafaf0", stroke=FIELD, color=INK, bold=True)
        f.append(fr)
        if_top[cx], if_bot[cx] = 228 - h / 2, 228 + h / 2
    # клієнт → інтерфейс (суцільна: «залежить від»)
    for cx in rxs:
        f.append(arrow(cx, rc_bot[cx] + 6, cx, if_top[cx] - 5, color=INK, sw=1.6))
    jb2, jw2, jh2 = textbox(800, 346, "Job\nреалізує всі три інтерфейси",
                            size=12, fill=FILL, stroke=INK, color=INK)
    j2top = 346 - jh2 / 2
    # інтерфейс → Job (пунктир: «реалізує», DIP — напрям залежності перевернуто)
    for cx, aim in zip(rxs, [800 - jw2 * 0.28, 800, 800 + jw2 * 0.28]):
        f.append(line(cx, if_bot[cx] + 6, aim, j2top - 5, color=FIELD, sw=1.5, dash="5 4"))
    f.append(jb2)
    f.append(text(800, 402, "зміна торкається лише свого інтерфейсу — інші клієнти незворушні",
                  size=11, color=FIELD))

    # висновок-смуга внизу
    f.append(fitbox(90, 448, 900, 58,
                    "Ліки: перед єдиним Job — вузький інтерфейс на кожен тип задачі (PrintJob, StapleJob, …), і клієнт залежить лише від свого.\n"
                    "Один клас Job реалізує їх усі; напрям залежності перевернуто через DIP, тож зміна більше не тягне за собою чужих клієнтів.",
                    size=12, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "xerox-job-before-after.svg"), W, H, *f)


# ───────── Фіг. 5 (вставка hist): від болю на проєкті — до літери в SOLID ─────────
def fig_isp_timeline():
    W, H = 1140, 300
    f = [text(570, 30, "Від болю на живому проєкті — до літери «I» в SOLID", size=16, bold=True)]

    y0 = 152
    f.append(line(70, y0, 1070, y0, color=MUTED, sw=2.0))

    xs = [100, 288, 476, 664, 852, 1040]
    above = [True, False, True, False, True, False]
    dot_c = [MUTED, POS, FIELD, INK, FIELD, INK]
    box_fill = [FILL, "#fdecea", "#eafaf0", FILL, "#eafaf0", FILL]
    box_str = [MUTED, POS, FIELD, MUTED, FIELD, MUTED]
    texts = [
        "1991\nЗасновано\nObject Mentor",
        "поч.–сер. 1990-х\nКонсалтинг у Xerox:\nсистема друку",
        "1996\nISP названо:\nC++ Report",
        "2000\n«Design Principles\n& Design Patterns»",
        "2002\nКнига PPP\n(Prentice Hall)",
        "2004\nМ. Фезерс склав\nакронім SOLID",
    ]
    bw, bh = 172, 82
    for x, up, dc, bf, bs, tx in zip(xs, above, dot_c, box_fill, box_str, texts):
        if up:
            by = y0 - 12 - bh
            f.append(line(x, by + bh, x, y0, color=MUTED, sw=1.2))
        else:
            by = y0 + 12
            f.append(line(x, y0, x, by, color=MUTED, sw=1.2))
        f.append(fitbox(x - bw / 2, by, bw, bh, tx, size=12, fill=bf, stroke=bs, color=INK, bold=True))
        f.append(circle(x, y0, 6, fill=dc, stroke=BG, sw=2))

    render(os.path.join(IMG, "isp-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fat_interface()
    fig_segregate()
    fig_capability_matrix()
    fig_xerox_job()
    fig_isp_timeline()
    print("OK: fat-interface-lsp, segregate-capabilities, capability-matrix, xerox-job-before-after, isp-timeline")
