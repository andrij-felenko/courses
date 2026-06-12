# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки §3.8.5c — «NOR-флеш W25Q-класу зблизька:
що вміє чіп — читання, стирання, посторінковий запис».

Окремий від головного figs.py розділу (його НЕ чіпаємо). Чистий Python без
залежностей. Вивід → ./img/. Стиль (AUTHORING §9) — спільні допоміжні функції
скопійовано з figs.py розділу, щоб вигляд був єдиний: білий фон, «1» червона,
«0» синій, поле/успіх зелене, стрілки через marker, sans-serif.

Три фігури, кожна несе вагу (§9) і НЕ дублює §3.6.3c (там були блок-схема,
розпіновка SOIC-8 і кеш XIP):
  fig-r08-5c-1-three-operations  три дії чипа й бітова асиметрія
                                 (читання будь-де · стирання → одиниці ·
                                  запис → нулі лише в стертому)
  fig-r08-5c-2-granularity       ієрархія стирання й цикл «стерти → записати»:
                                 байт читаєш точково, а стираєш цілим сектором
  fig-r08-5c-3-nor-vs-nand       топологія масиву: чому NOR читається побайтово
                                 (XIP), а NAND — лише сторінками
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════ Рис. 3.8.5c.1 — три дії чипа й бітова асиметрія ═════════════════
def fig_three_operations():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 34, "Що вміє чіп: три дії — і несиметрична арифметика бітів", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56,
              "читати можна будь-де; стирання повертає біти в 1 цілими блоками; запис лише ОПУСКАЄ окремі біти в 0",
              11.5, GREY, "middle", style="italic")

    # три колонки-картки
    col_w, col_h = 270, 150
    xs = [30, 325, 620]
    titles = ["ЧИТАННЯ (Read)", "СТИРАННЯ (Erase)", "ЗАПИС (Program)"]
    subs = ["будь-який байт за адресою", "цілий блок → усі біти в 1", "у стертому → окремі біти в 0"]
    cols = [GREEN, BLUE, RED]
    for x, t, sub, c in zip(xs, titles, subs, cols):
        s += rect(x, 80, col_w, col_h, "#ffffff", c, 2.2, 12)
        s += text(x + col_w / 2, 106, t, 14.5, c, "middle", "bold")
        s += text(x + col_w / 2, 126, sub, 10.5, GREY, "middle", style="italic")

    # ── читання: лінійка байтів, стрілка тицяє в один ──
    rx = xs[0] + 20
    by = 150
    for i in range(8):
        cellx = rx + i * 29
        s += rect(cellx, by, 26, 30, "#f4f7f4" if i != 5 else "#e9f6ee", GREEN if i == 5 else INK, 1.6 if i == 5 else 1.2, 4)
    s += text(rx + 5 * 29 + 13, by + 20, "?", 14, GREEN, "middle", "bold")
    s += arrow(rx + 5 * 29 + 13, by + 56, rx + 5 * 29 + 13, by + 34, GREEN, 2)
    s += text(rx + 5 * 29 + 13, by + 70, "адреса", 9.5, GREEN, "middle", "bold")
    s += text(xs[0] + col_w / 2, by + 92, "точково, миттєво — основа XIP (§3.6.3c)", 9.5, INK, "middle", "bold")

    # ── стирання: блок з нулями → блок з одиницями ──
    ex = xs[1] + 18
    ey = 150
    bits_before = "01001101"
    s += text(ex - 4, ey + 18, "до:", 10, GREY, "start")
    for i, b in enumerate(bits_before):
        s += rect(ex + 34 + i * 24, ey, 21, 24, "#fdf4f4" if b == "0" else "#f4f7f9",
                  RED if b == "0" else BLUE, 1.3, 3)
        s += text(ex + 34 + i * 24 + 10, ey + 17, b, 12, RED if b == "0" else BLUE, "middle", "bold")
    s += arrow(xs[1] + col_w / 2, ey + 32, xs[1] + col_w / 2, ey + 50, BLUE, 2.4)
    s += text(xs[1] + col_w / 2 + 64, ey + 46, "Erase", 10, BLUE, "middle", "bold")
    s += text(ex - 4, ey + 70, "по:", 10, GREY, "start")
    for i in range(8):
        s += rect(ex + 34 + i * 24, ey + 53, 21, 24, "#f4f7f9", BLUE, 1.3, 3)
        s += text(ex + 34 + i * 24 + 10, ey + 70, "1", 12, BLUE, "middle", "bold")
    s += text(xs[1] + col_w / 2, ey + 96, "усе стає 1 — і то БЛОКОМ, не байтом", 9.5, INK, "middle", "bold")

    # ── запис: одиниці → опускаємо обрані в нуль ──
    px = xs[2] + 18
    py = 150
    after = "01101001"
    s += text(px - 4, py + 18, "є:", 10, GREY, "start")
    for i in range(8):
        s += rect(px + 30 + i * 24, py, 21, 24, "#f4f7f9", BLUE, 1.3, 3)
        s += text(px + 30 + i * 24 + 10, py + 17, "1", 12, BLUE, "middle", "bold")
    s += arrow(xs[2] + col_w / 2, py + 32, xs[2] + col_w / 2, py + 50, RED, 2.4)
    s += text(xs[2] + col_w / 2 + 70, py + 46, "Program", 10, RED, "middle", "bold")
    s += text(px - 4, py + 70, "по:", 10, GREY, "start")
    for i, b in enumerate(after):
        s += rect(px + 30 + i * 24, py + 53, 21, 24, "#fdf4f4" if b == "0" else "#f4f7f9",
                  RED if b == "0" else BLUE, 1.3, 3)
        s += text(px + 30 + i * 24 + 10, py + 70, b, 12, RED if b == "0" else BLUE, "middle", "bold")
    s += text(xs[2] + col_w / 2, py + 96, "1→0 можна будь-коли; 0→1 — лише стиранням", 9.5, INK, "middle", "bold")

    # ── центральне правило асиметрії ──
    s += rect(60, 372, W - 120, 64, "#fff8e8", AMBER, 1.8, 10)
    s += text(W / 2, 396, "Головна несиметрія NOR-флеші:  запис уміє ТІЛЬКИ опускати біти 1 → 0.",
              13, INK, "middle", "bold")
    s += text(W / 2, 418, "Підняти біт назад 0 → 1 поодинці неможливо — це робить лише стирання, і відразу для цілого блока.",
              11, GREY, "middle", style="italic")

    # ── нижня плашка: швидкісна асиметрія ──
    s += rect(60, 450, W - 120, 70, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 474, "Звідси й асиметрія часу: читання — наносекунди-мікросекунди; запис сторінки — частки мілісекунди;",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 496, "стирання блока — десятки-сотні мілісекунд. Читати дешево, стирати дорого — це визначає, як таким чипом користуються.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 512, "Точні числа — за даташитом конкретного чипа (перевірити); тут важать порядки.",
              9.5, GREY, "middle", style="italic")
    save("fig-r08-5c-1-three-operations.svg", s)


# ════════════ Рис. 3.8.5c.2 — ієрархія стирання й цикл стерти→записати ════════
def fig_granularity():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 34, "Асиметрія зернистості: читаєш і пишеш дрібно, а стираєш — крупно", 19, INK, "middle", "bold")
    s += text(W / 2, 56,
              "приклад організації W25Q128: 16 МБ = 256 блоків по 64 КБ = 4096 секторів по 4 КБ = 65 536 сторінок по 256 Б",
              11, GREY, "middle", style="italic")

    # ── ієрархія як вкладені прямокутники ──
    # чіп
    cx, cy, cw, ch = 40, 86, 380, 250
    s += rect(cx, cy, cw, ch, "#fbfbfb", INK, 2, 10)
    s += text(cx + 12, cy + 22, "ЧІП — 16 МБ (W25Q128)", 12.5, INK, "start", "bold")
    s += text(cx + cw - 12, cy + 22, "Chip Erase — усе одразу", 9.5, GREY, "end", style="italic")
    # блок 64К
    bx, by, bw, bh = cx + 18, cy + 36, cw - 36, 168
    s += rect(bx, by, bw, bh, "#f4f7f9", BLUE, 1.8, 8)
    s += text(bx + 10, by + 20, "БЛОК — 64 КБ  (×256)", 11.5, BLUE, "start", "bold")
    s += text(bx + bw - 10, by + 20, "Block Erase 64K", 9, GREY, "end", style="italic")
    # сектор 4К
    sx2, sy2, sw2, sh2 = bx + 16, by + 32, bw - 32, 104
    s += rect(sx2, sy2, sw2, sh2, "#fdf6ee", AMBER, 1.8, 8)
    s += text(sx2 + 10, sy2 + 19, "СЕКТОР — 4 КБ  (×16 у блоці)", 11, "#8a6a18", "start", "bold")
    s += text(sx2 + sw2 - 10, sy2 + 19, "Sector Erase 4K — найдрібніше стирання", 9, "#8a6a18", "end", style="italic")
    # сторінки 256 Б
    pgw = (sw2 - 40) / 8
    for i in range(8):
        s += rect(sx2 + 12 + i * (pgw + 1.2), sy2 + 34, pgw, 44, "#fdf4f4", RED, 1.3, 3)
    s += text(sx2 + sw2 / 2, sy2 + 92, "16 сторінок по 256 Б — найдрібніший ЗАПИС (Page Program)", 9.5, RED, "middle", "bold")

    # підпис-стрілки збоку
    s += text(cx + cw / 2, cy + ch + 22, "читання — будь-який байт усередині · запис — сторінка · стирання — сектор/блок/чіп",
              10, INK, "middle", "bold")

    # ── цикл «стерти → записати» праворуч ──
    fx = 470
    s += rect(fx, 86, W - fx - 40, 250, "#ffffff", GREEN, 2, 12)
    s += text(fx + (W - fx - 40) / 2, 110, "Щоб змінити навіть один байт:", 13, GREEN, "middle", "bold")
    steps = [
        ("1", "ВВЕСТИ дозвіл на запис", "Write Enable — інакше чіп мовчки відмовить", INK),
        ("2", "СТЕРТИ цілий сектор 4 КБ", "усі біти сектора → 1 (десятки мс)", BLUE),
        ("3", "ЗАПИСАТИ потрібні сторінки", "опускаємо біти 1→0, по ≤256 Б за раз", RED),
        ("4", "ЧЕКАТИ, поки чіп зайнятий", "опитуємо біт Busy; нову команду — лише по його скиданню", AMBER),
    ]
    ys = 134
    for num, t, d, c in steps:
        s += circle(fx + 28, ys + 8, 13, "#ffffff", c, 2)
        s += text(fx + 28, ys + 13, num, 12, c, "middle", "bold")
        s += text(fx + 50, ys + 4, t, 11.5, c, "start", "bold")
        s += text(fx + 50, ys + 21, d, 9.5, GREY, "start")
        if num != "4":
            s += arrow(fx + 28, ys + 24, fx + 28, ys + 40, GREY, 1.6)
        ys += 48

    # ── пастка read-modify-write ──
    s += rect(60, 352, W - 120, 86, "#fff8e8", AMBER, 1.8, 10)
    s += text(W / 2, 376, "Граблі read-modify-write: апаратного «змінити один байт на місці» НЕМАЄ.",
              13, INK, "middle", "bold")
    s += text(W / 2, 398, "Хочеш переписати 1 байт у вже записаному секторі — доводиться: вичитати сектор у RAM → змінити байт →",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 416, "стерти весь сектор 4 КБ у флеші → записати сектор назад. Один байт коштує стирання й перезапису тисяч байтів.",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 432, "Саме тому під часті дрібні зміни (лічильники, журнали) такий чіп підходить погано — краще EEPROM/FRAM (§3.8.8).",
              10, "#8a6a18", "middle", "bold")

    # ── місток до зносу ──
    s += rect(60, 452, W - 120, 72, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 476, "І ще наслідок: кожне стирання потроху ЗНОШУЄ комірки (§3.6.8 — тунелювання крізь ізолятор).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 498, "Ресурс — типово близько 100 000 циклів стирання на сектор (перевірити за даташитом), потім сектор «втомлюється».",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 516, "Тому реальні файлові системи й бутлоадери стирають по черзі різні сектори, щоб не виробити один.",
              10, GREY, "middle", style="italic")
    save("fig-r08-5c-2-granularity.svg", s)


# ════════════ Рис. 3.8.5c.3 — топологія NOR vs NAND: чому NOR читається байтом ══
def fig_nor_vs_nand():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 34, "Чому NOR читається побайтово (і годиться для XIP), а NAND — ні", 19, INK, "middle", "bold")
    s += text(W / 2, 56,
              "різниця — у тому, ЯК комірки під'єднані до розрядної лінії: паралельно (NOR) чи довгим ланцюжком (NAND)",
              11, GREY, "middle", style="italic")

    # ── ЛІВО: NOR — комірки паралельно до bit line ──
    Lx = 120
    s += text(Lx, 92, "NOR", 17, GREEN, "middle", "bold")
    s += text(Lx, 110, "комірки ПАРАЛЕЛЬНО", 10.5, GREEN, "middle", "bold")
    # bit line вертикальна
    blx = Lx
    bl_top, bl_bot = 128, 300
    s += line(blx, bl_top, blx, bl_bot, INK, 2.4)
    s += text(blx + 8, bl_top - 4, "bit line", 9.5, INK, "start")
    # три комірки відгалужуються прямо до лінії
    cellsy = [148, 200, 252]
    wls = ["WL0", "WL1", "WL2"]
    for cyc, wl in zip(cellsy, wls):
        s += line(blx, cyc, blx + 46, cyc, GREEN, 2)
        s += rect(blx + 46, cyc - 13, 40, 26, "#f4f7f4", GREEN, 1.6, 4)
        s += text(blx + 66, cyc + 4, "комір.", 8.5, GREEN, "middle", "bold")
        s += line(blx + 86, cyc, blx + 120, cyc, GREY, 1.4)
        s += text(blx + 124, cyc + 4, wl, 9, GREY, "start")
    s += text(Lx, 322, "кожна комірка має ПРЯМИЙ доступ до лінії", 9.5, INK, "middle", "bold")
    s += text(Lx, 338, "→ читаємо будь-яку поодинці, за наносекунди", 9.5, GREEN, "middle", "bold")

    # ── ПРАВО: NAND — комірки в ланцюжку (string) ──
    Rx = 600
    s += text(Rx, 92, "NAND", 17, RED, "middle", "bold")
    s += text(Rx, 110, "комірки в ЛАНЦЮЖКУ", 10.5, RED, "middle", "bold")
    nblx = Rx
    s += line(nblx, 128, nblx, 150, INK, 2.4)
    s += text(nblx + 8, 132, "bit line", 9.5, INK, "start")
    # послідовний ланцюжок комірок
    chainy = [150, 196, 242, 288]
    for i, cyc in enumerate(chainy):
        s += rect(nblx - 20, cyc, 40, 30, "#fdf4f4", RED, 1.6, 4)
        s += text(nblx, cyc + 19, f"к{i}", 9.5, RED, "middle", "bold")
        if i < len(chainy) - 1:
            s += line(nblx, cyc + 30, nblx, chainy[i + 1], INK, 2.4)
    s += line(nblx, chainy[-1] + 30, nblx, chainy[-1] + 48, INK, 2.4)
    s += text(nblx + 28, chainy[0] + 20, "усі ввімкнені", 8.5, GREY, "start")
    s += text(nblx + 28, chainy[0] + 33, "послідовно", 8.5, GREY, "start")
    s += text(Rx, 322, "щоб дотягтись до однієї — струм іде КРІЗЬ сусідів", 9.5, INK, "middle", "bold")
    s += text(Rx, 338, "→ читати можна лише цілою сторінкою, не байтом", 9.5, RED, "middle", "bold")

    # розділювач
    s += line(W / 2, 120, W / 2, 348, FAINT, 1.4, dash="4,5")

    # ── порівняльна таблиця-підсумок ──
    ty = 366
    s += rect(60, ty, W - 120, 96, "#ffffff", INK, 1.6, 10)
    rows = [
        ("Випадкове читання байта", "так — будь-де", "ні — лише сторінками", GREEN, RED),
        ("XIP (код виконується «на місці»)", "так", "ні (потрібна копія в RAM)", GREEN, RED),
        ("Щільність / ціна за байт", "нижча, дорожча", "вища, дешевша", AMBER, GREEN),
        ("Де доречна", "код, малі прошивки", "масові дані: SD, eMMC, SSD", INK, INK),
    ]
    s += line(370, ty + 8, 370, ty + 88, FAINT, 1)
    s += line(645, ty + 8, 645, ty + 88, FAINT, 1)
    s += text(215, ty + 18, "властивість", 10, GREY, "middle", "bold")
    s += text(507, ty + 18, "NOR (наш W25Q)", 10.5, GREEN, "middle", "bold")
    s += text(782, ty + 18, "NAND", 10.5, RED, "middle", "bold")
    yy = ty + 38
    for name, a, b, ca, cb in rows:
        s += text(72, yy, name, 9.8, INK, "start")
        s += text(507, yy, a, 9.8, ca, "middle", "bold")
        s += text(782, yy, b, 9.8, cb, "middle", "bold")
        yy += 16.5

    # ── підсумкова плашка ──
    s += rect(60, 476, W - 120, 50, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 500, "Підсумок: W25Q-клас — це NOR. Її козир — читати будь-який байт, тож код виконують прямо з неї (XIP).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 518, "Платня за це — менший об'єм; коли байтів треба дуже багато, беруть NAND і миряться з посторінковим доступом.",
              10.5, GREY, "middle", style="italic")
    save("fig-r08-5c-3-nor-vs-nand.svg", s)


if __name__ == "__main__":
    fig_three_operations()
    fig_granularity()
    fig_nor_vs_nand()
    print("done.")
