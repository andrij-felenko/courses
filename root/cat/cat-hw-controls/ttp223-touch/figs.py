# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «TTP223 — сенсорний давач дотику».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def block(cx, cy, w, h, s, size=13, fill=FILL, stroke=LINE):
    """Прямокутний блок фіксованої ширини з підписом усередині (fitbox)."""
    return fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size, fill=fill, stroke=stroke, sw=1.8)


# ── 1. Внутрішній тракт TTP223 ────────────────────────────────────────────────
def fig_block():
    W, H = 1240, 400
    f = [text(W / 2, 32, "Усередині TTP223: ємність пластинки → база + поріг → режим → вихід Q",
              size=15, bold=True)]

    row = 175
    bw, bh = 168, 84
    xs = [140, 372, 604, 836]
    labels = ["вимірювач\nємності", "фон\n(автокалібр.)", "поріг\n(порівняння)", "логіка режиму\nTOG · AHLB"]
    for x, lab in zip(xs, labels):
        f.append(block(x, row, bw, bh, lab))
    for i in range(len(xs) - 1):
        f.append(arrow(xs[i] + bw / 2, row, xs[i + 1] - bw / 2, row))

    # вхід: пластинка I згори в першу клітину
    f.append(text(140, row - bh / 2 - 32, "пластинка (вхід I)", size=12, color=FIELD, bold=True))
    f.append(text(140, row - bh / 2 - 16, "палець ↔ мідь: +ΔC", size=10.5, color=MUTED))
    f.append(arrow(140, row - bh / 2 - 4, 140, row - bh / 2 + 8, color=FIELD))

    # пояснення під блоками (рознесені, не накладаються)
    f.append(text(372, row + bh / 2 + 26, "повільно тягне фон за середовищем", size=10.5, color=MUTED))
    f.append(text(604, row + bh / 2 + 26, "перевищення над фоном → «дотик»", size=10.5, color=MUTED))

    # зовнішній кондесатор знизу до вимірювача
    f.append(text(140, row + bh / 2 + 26, "зовн. C → нижча чутливість", size=10.5, color=MUTED))

    # вихід: Q праворуч
    qx = xs[3] + bw / 2
    node_x = qx + 66
    f.append(arrow(qx, row, node_x, row))
    f.append(text(node_x + 8, row + 5, "Q — двотактний CMOS", size=12.5, bold=True, anchor="start"))
    f.append(text(node_x + 8, row + 26, "жорстка «1» і «0», підтяжка не потрібна", size=10.5,
                  color=MUTED, anchor="start"))
    return W, H, f


# ── 2. Чотири режими за перемичками A (AHLB) і B (TOG) ─────────────────────────
def fig_modes():
    W, H = 1080, 470
    f = [text(W / 2, 32, "Дві перемички на звороті задають чотири режими виходу", size=15, bold=True)]

    # осі таблиці 2×2
    x0, y0 = 300, 110          # лівий-верхній кут поля клітин
    cw, ch = 350, 130          # розмір клітини
    gx, gy = 20, 20            # проміжки

    # підписи стовпців (B / TOG) і рядків (A / AHLB)
    f.append(text(x0 + cw / 2, y0 - 40, "B розімкнена", size=13, bold=True, color=NEG))
    f.append(text(x0 + cw / 2, y0 - 22, "миттєвий (доки тримаєш)", size=11, color=MUTED))
    f.append(text(x0 + cw + gx + cw / 2, y0 - 40, "B замкнена", size=13, bold=True, color=POS))
    f.append(text(x0 + cw + gx + cw / 2, y0 - 22, "фіксація (дотик перемикає)", size=11, color=MUTED))

    f.append(text(x0 - 24, y0 + ch / 2 - 8, "A розімкнена", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(x0 - 24, y0 + ch / 2 + 10, "спокій=0, дотик=1", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 24, y0 + ch + gy + ch / 2 - 8, "A замкнена", size=13, bold=True, color=POS, anchor="end"))
    f.append(text(x0 - 24, y0 + ch + gy + ch / 2 + 10, "спокій=1, дотик=0", size=11, color=MUTED, anchor="end"))

    cells = [
        # (col, row, заголовок, підпис)
        (0, 0, "миттєвий, активний у 1", "тримаєш → 1; відпустив → 0", FILL),
        (1, 0, "фіксація, активний у 1", "дотик → 1; ще дотик → 0", "#eef7f0"),
        (0, 1, "миттєвий, активний у 0", "тримаєш → 0; відпустив → 1", "#eef2fb"),
        (1, 1, "фіксація, активний у 0", "дотик → 0; ще дотик → 1", "#f7f0ee"),
    ]
    for col, rrow, head, sub, fill in cells:
        cx = x0 + col * (cw + gx)
        cy = y0 + rrow * (ch + gy)
        f.append(rect(cx, cy, cw, ch, fill=fill, stroke=INK, sw=1.8, rx=10))
        f.append(text(cx + cw / 2, cy + 42, head, size=14, bold=True))
        f.append(text(cx + cw / 2, cy + 78, sub, size=12.5, color=MUTED))

    # заводський стан — примітка знизу
    f.append(line(x0 - 200, 440, x0 + 2 * cw + gx, 440, color="#e5e7eb", sw=1))
    f.append(text(W / 2, 462,
                  "З коробки типово: обидві розімкнені → миттєвий, активний у 1 (спокій 0, дотик 1)",
                  size=12, bold=True))
    return W, H, f


# ── 3. Підключення модуля до мікроконтролера ──────────────────────────────────
def fig_wiring():
    W, H = 980, 360
    f = [text(W / 2, 30, "Підключення TTP223-модуля: три дроти, вихід прямо в GPIO", size=15, bold=True)]

    # модуль ліворуч
    bx, by, bw, bh = 110, 95, 250, 170
    f.append(rect(bx, by, bw, bh, fill=BG, stroke=NEG, sw=2.2, rx=12))
    f.append(text(bx + bw / 2, by + 30, "TTP223", size=15, bold=True, color=NEG))
    f.append(text(bx + bw / 2, by + 50, "сенсорна кнопка", size=11, color=MUTED))
    # намічена пластинка на модулі
    f.append(rect(bx + 30, by + 70, bw - 60, 62, fill="#f0f4fb", stroke=NEG, sw=1.4, rx=8))
    f.append(text(bx + bw / 2, by + 96, "мідна пластинка", size=11, color=NEG))
    f.append(text(bx + bw / 2, by + 114, "(торкаєшся зверху)", size=10, color=MUTED))

    # три ноги праворуч від модуля
    pins = [("SIG", by + 20, INK), ("VCC 2–5.5В", by + 90, POS), ("GND", by + 150, NEG)]
    for lab, y, col in pins:
        f.append(circle(bx + bw, y, 4, fill=col, stroke=col))
        f.append(text(bx + bw - 14, y + 4, lab, size=12, anchor="end", color=col, bold=True))

    # МК праворуч
    mx, my, mw, mh = 640, 95, 250, 170
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=INK, sw=2.2, rx=14))
    f.append(text(mx + mw / 2, my + 30, "мікроконтролер", size=14, bold=True))

    def mk_pin(y, lab, col=INK):
        f.append(circle(mx, y, 4, fill=col, stroke=col))
        f.append(text(mx + 14, y + 4, lab, size=12, anchor="start", color=col))

    y_sig = my + 40
    y_v = my + 95
    y_g = my + 150
    mk_pin(y_sig, "цифр. вхід (INPUT)", INK)
    mk_pin(y_v, "3.3 або 5 В", POS)
    mk_pin(y_g, "GND", NEG)

    # дроти: SIG → GPIO
    f.append(line(bx + bw, by + 20, 500, by + 20))
    f.append(line(500, by + 20, 500, y_sig))
    f.append(line(500, y_sig, mx, y_sig))
    # VCC
    f.append(line(bx + bw, by + 90, 470, by + 90, color=POS))
    f.append(line(470, by + 90, 470, y_v, color=POS))
    f.append(line(470, y_v, mx, y_v, color=POS))
    # GND
    f.append(line(bx + bw, by + 150, 530, by + 150, color=NEG))
    f.append(line(530, by + 150, 530, y_g, color=NEG))
    f.append(line(530, y_g, mx, y_g, color=NEG))

    f.append(text(W / 2, 330, "Підтяжок і зовнішніх деталей не треба — вихід сам дає жорсткі рівні.",
                  size=11.5, color=MUTED))
    return W, H, f


# ── 4. Родина TonTouch за кількістю клавіш (для hist-вставки) ──────────────────
def fig_family():
    W, H = 1120, 470
    f = [text(W / 2, 34, "Родина TonTouch: кількість клавіш диктує спосіб виведення",
              size=15, bold=True)]

    # чотири сходинки знизу вгору; кожна ширша за попередню
    x_left = 90
    rows = [
        # (y, назва, клавіші, спосіб, колір рамки, заливка)
        (400, "TTP223", "1 клавіша", "1 біт → одна нога напряму", NEG, "#eef2fb"),
        (320, "TTP224", "4 клавіші", "нога на кожну клавішу", INK, FILL),
        (240, "TTP226", "8 клавіш", "нога на кожну клавішу (межа)", INK, FILL),
        (150, "TTP229", "до 16 клавіш", "послідовно по 2 дротах (або I²C)", POS, "#fdecea"),
    ]
    bh = 58
    for i, (y, name, keys, how, col, fill) in enumerate(rows):
        bw = 250 + i * 60
        f.append(rect(x_left, y - bh / 2, bw, bh, fill=fill, stroke=col, sw=2, rx=10))
        f.append(text(x_left + 16, y - 6, name, size=15, bold=True, color=col, anchor="start"))
        f.append(text(x_left + 16, y + 15, keys, size=12, color=MUTED, anchor="start"))
        # спосіб виведення — праворуч від рамки, з запасом, не накладається
        f.append(text(x_left + bw + 24, y + 4, how, size=12.5, anchor="start", color=INK))

    # вертикальна вісь «більше клавіш ↑» ліворуч; підпис — вертикально вздовж осі
    ax = x_left - 34
    f.append(arrow(ax, 400 + bh / 2, ax, 150 - bh / 2, color=MUTED))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" font-style="italic" transform="rotate(-90 %.1f %.1f)">'
             'більше клавіш</text>' % (ax - 16, 275, FONT, MUTED, ax - 16, 275))

    # перелом між TTP226 і TTP229 — пунктир «прямі ноги вичерпалися»
    ybr = (240 + 150) / 2 + 6
    f.append(line(x_left, ybr, x_left + 560, ybr, color=POS, sw=1.4, dash="6 5"))
    f.append(text(x_left + 570, ybr + 4, "тут прямі ноги вичерпалися → шина",
                  size=11.5, color=POS, anchor="start"))
    return W, H, f


# ── 5. Дві парадигми драйвера: миттєвий (фронти) vs фіксація (рівень) ──────────
def fig_driver_modes():
    W, H = 1180, 560
    f = [text(W / 2, 32, "Той самий рівень SIG — дві парадигми коду", size=15, bold=True)]

    # Спільна вісь часу: три дотики (сірі смуги «палець на пластинці»)
    left = 230            # де починаються траси (праворуч від підписів рівнів)
    right = 1120
    touches = [(320, 400), (560, 640), (800, 880)]   # (початок, кінець) дотику по x
    trace_h = 44

    def finger_bands(y_top, y_bot):
        return [rect(a, y_top, b - a, y_bot - y_top, fill="#f0f0f2", stroke="none", rx=0)
                for a, b in touches]

    # ── Верхня панель: МИТТЄВИЙ ───────────────────────────────────────────────
    yb = 92
    f.append(text(20, yb + 6, "Миттєвий режим", size=14, bold=True, color=NEG, anchor="start"))
    f.append(text(20, yb + 26, "(TOG розімкнена)", size=11, color=MUTED, anchor="start"))

    ty_hi = yb + 62
    ty_lo = ty_hi + trace_h
    f.extend(finger_bands(ty_hi - 8, ty_lo + 8))
    f.append(text(left - 14, ty_hi + 4, "1", size=12, bold=True, anchor="end"))
    f.append(text(left - 14, ty_lo + 4, "0", size=12, bold=True, anchor="end"))
    f.append(text(20, ty_lo + 42, "рівень тримається,", size=11, color=INK, anchor="start"))
    f.append(text(20, ty_lo + 58, "доки палець на пластинці", size=11, color=INK, anchor="start"))

    pts = [(left, ty_lo)]
    for a, b in touches:
        pts += [(a, ty_lo), (a, ty_hi), (b, ty_hi), (b, ty_lo)]
    pts += [(right, ty_lo)]
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=NEG, sw=2.4))

    a0, b0 = touches[0]
    f.append(arrow(a0, ty_hi - 16, a0, ty_hi - 3, color=POS))
    f.append(arrow(b0, ty_lo + 3, b0, ty_lo + 16, color=NEG))
    f.append(text(a0 - 8, ty_hi - 22, "торкнулися", size=10, color=POS, bold=True, anchor="end"))
    f.append(text(b0 + 8, ty_lo + 30, "відпустили", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(right, ty_hi - 22, "драйвер ловить ФРОНТИ (події)", size=11, bold=True,
                  color=INK, anchor="end"))

    # ── Роздільник ────────────────────────────────────────────────────────────
    f.append(line(20, 302, W - 20, 302, color="#e5e7eb", sw=1))

    # ── Нижня панель: ФІКСАЦІЯ ────────────────────────────────────────────────
    yb2 = 336
    f.append(text(20, yb2 + 6, "Фіксація", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(20, yb2 + 26, "(TOG замкнена)", size=11, color=MUTED, anchor="start"))

    fy_hi = yb2 + 62
    fy_lo = fy_hi + trace_h
    f.extend(finger_bands(fy_hi - 8, fy_lo + 8))
    f.append(text(left - 14, fy_hi + 4, "1", size=12, bold=True, anchor="end"))
    f.append(text(left - 14, fy_lo + 4, "0", size=12, bold=True, anchor="end"))
    f.append(text(20, fy_lo + 42, "кожен дотик перемикає", size=11, color=INK, anchor="start"))
    f.append(text(20, fy_lo + 58, "й лишає рівень", size=11, color=INK, anchor="start"))

    state = 0
    fx = [(left, fy_lo)]
    cur_y = fy_lo
    for a, b in touches:
        fx.append((a, cur_y))
        state ^= 1
        new_y = fy_hi if state else fy_lo
        fx.append((a, new_y))
        cur_y = new_y
    fx.append((right, cur_y))
    for i in range(len(fx) - 1):
        f.append(line(fx[i][0], fx[i][1], fx[i + 1][0], fx[i + 1][1], color=POS, sw=2.4))

    f.append(text(touches[0][0], fy_hi - 14, "увімкнено", size=10, color=POS, bold=True))
    f.append(text(touches[1][0], fy_lo + 30, "вимкнено", size=10, color=MUTED, bold=True))
    f.append(text(touches[2][0], fy_hi - 14, "увімкнено", size=10, color=POS, bold=True))
    f.append(text(right, fy_hi - 22, "драйвер читає РІВЕНЬ як стан", size=11, bold=True,
                  color=INK, anchor="end"))

    f.append(text(W / 2, 546,
                  "Сірі смуги — палець на пластинці. Плутати дві парадигми — головна пастка драйвера.",
                  size=11, color=MUTED))
    return W, H, f


for name, fn in [("block", fig_block),
                 ("modes", fig_modes),
                 ("wiring", fig_wiring),
                 ("family", fig_family),
                 ("driver-modes", fig_driver_modes)]:
    W, H, frags = fn()
    render(os.path.join(IMG, name + ".svg"), W, H, *frags)
    print("wrote", name + ".svg")
