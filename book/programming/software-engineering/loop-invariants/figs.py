# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN  = "#c07000"   # бурштин — інваріант / твердження
WFILL = "#fff3cd"


# ── three-steps: індукція — ініціалізація → збереження → завершення ───────────
# Ідея: доведення коректності циклу — це індукція з трьох кроків. База (істинно
# перед першою ітерацією), крок (тіло зберігає істинність), і вихід (інваріант +
# умова виходу дають потрібний результат). Три кроки — три окремі обов'язки.

def fig_three_steps():
    W, H = 760, 360
    p = []

    steps = [
        (130, NEG, "#eaf0fd", "1 · ІНІЦІАЛІЗАЦІЯ",
         "інваріант істинний\nПЕРЕД першою\nітерацією",
         "база індукції"),
        (W / 2, WARN, WFILL, "2 · ЗБЕРЕЖЕННЯ",
         "якщо істинний перед\nітерацією — лишається\nістинним і після",
         "крок індукції"),
        (W - 130, FIELD, "#e8f5e9", "3 · ЗАВЕРШЕННЯ",
         "інваріант + умова\nвиходу = потрібний\nрезультат",
         "висновок"),
    ]

    boxes = []
    for gx, col, fill, head, body, role in steps:
        p.append(text(gx, 70, head, size=12.5, color=col, bold=True))
        bb, bw, bh = textbox(gx, 150, body, size=11.5, fill=fill, stroke=col, sw=2.0,
                             color=INK, min_w=190)
        boxes.append((gx, bw, bh))
        p.append(bb)
        p.append(text(gx, 232, role, size=11, color=MUTED, italic=True))

    # стрілки 1→2→3
    for i in range(2):
        gx0, bw0, _ = boxes[i]
        gx1, bw1, _ = boxes[i + 1]
        p.append(arrow(gx0 + bw0 / 2, 150, gx1 - bw1 / 2, 150, color=MUTED, sw=1.8))

    note, nw, nh = textbox(W / 2, H - 60,
                           "доведено всі три → інваріант істинний на КОЖНІЙ ітерації,\nа на виході дає коректний результат",
                           size=12, bold=True, fill=FILL, stroke=INK, sw=1.8)
    p.append(note)
    p.append(text(W / 2, H - 14,
                  "це математична індукція, перенесена на цикл",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-steps.svg"), W, H, *p,
           title="Інваріант циклу: три кроки доведення коректності")


# ── search-window: інваріант двійкового пошуку — ціль завжди в [lo, hi] ───────
# Ідея: інваріант підтримує «якщо ціль у масиві, вона лежить у вікні [lo, hi]».
# Кожна ітерація відкидає половину, де цілі точно немає, і вікно стискається,
# не випускаючи ціль. Це й є властивість, що тримається перед кожним проходом.

def fig_search_window():
    W, H = 760, 360
    p = []
    n = 12
    x0, x1 = 70, W - 70
    cellw = (x1 - x0) / n

    rows = [
        (96,  0, n - 1, 5, "вхід: вікно = весь масив [0 .. 11]"),
        (176, 6, n - 1, 9, "lo=6, hi=11 — ліву половину відкинуто, ціль (якщо є) тут"),
        (256, 9, 10, 9,    "lo=9, hi=10 — вікно стиснулось, ціль усе ще всередині"),
    ]

    for cy, lo, hi, target, cap in rows:
        # усі комірки
        for i in range(n):
            cx = x0 + i * cellw
            inside = lo <= i <= hi
            fill = "#e8f5e9" if inside else "#eef0f2"
            stroke = FIELD if inside else "#cbd0d6"
            p.append(rect(cx, cy, cellw - 2, 30, fill=fill, stroke=stroke, sw=1.4, rx=3))
        # позначка цілі
        tcx = x0 + target * cellw + cellw / 2
        p.append(text(tcx, cy + 20, "★", size=15, color=POS, bold=True))
        # межі lo/hi
        lcx = x0 + lo * cellw + cellw / 2
        hcx = x0 + hi * cellw + cellw / 2
        p.append(text(lcx, cy - 6, "lo", size=10, color=NEG, bold=True))
        p.append(text(hcx, cy - 6, "hi", size=10, color=NEG, bold=True))
        # підпис рядка
        p.append(text(x0, cy + 48, cap, size=10.5, color=MUTED, anchor="start", italic=True))
        # дужка вікна під рядком
        p.append(line(x0 + lo * cellw, cy + 33, x0 + (hi + 1) * cellw - 2, cy + 33,
                      color=FIELD, sw=2.2))

    inv, iw, ih = textbox(W / 2, H - 34,
                          "ІНВАРІАНТ: якщо ціль у масиві — вона завжди у вікні [lo, hi].\n★ ніколи не випадає за зелену межу, хоч вікно й стискається",
                          size=11.5, bold=True, fill=WFILL, stroke=WARN, sw=2.0)
    p.append(inv)

    render(os.path.join(OUT, "search-window.svg"), W, H, *p,
           title="Інваріант двійкового пошуку: ціль не виходить із вікна")


# ── variant: спадна величина доводить ЗАВЕРШЕННЯ ──────────────────────────────
# Ідея: інваріант доводить коректність, але не завершення. Для завершення —
# варіант: невід'ємна ціла величина, що СТРОГО спадає щоиітерації. Спадає й
# обмежена знизу нулем → не може спадати вічно → цикл спиниться.

def fig_variant():
    W, H = 720, 360
    p = []
    base_x, base_y = 90, 250
    axis_top = 70
    # осі
    p.append(arrow(base_x, base_y, W - 50, base_y, color=INK, sw=1.6))   # час/ітерації
    p.append(arrow(base_x, base_y, base_x, axis_top, color=INK, sw=1.6))  # величина
    p.append(text(W - 50, base_y + 18, "ітерації →", size=11, color=MUTED, anchor="end"))
    p.append(text(base_x - 8, axis_top - 4, "варіант", size=11, color=MUTED, anchor="end"))
    p.append(text(base_x - 8, axis_top + 10, "(розмір вікна)", size=9, color=MUTED, anchor="end"))

    # лінія нуля
    p.append(line(base_x, base_y, W - 50, base_y, color=POS, sw=1.2, dash="4 4"))
    p.append(text(base_x - 8, base_y + 4, "0", size=11, color=POS, anchor="end", bold=True))

    # спадні стовпчики: 12 → 6 → 3 → 1 → 0
    vals = [12, 6, 3, 1, 0]
    step = (W - 50 - base_x - 40) / len(vals)
    unit = (base_y - axis_top) / 12.0
    for i, v in enumerate(vals):
        cx = base_x + 40 + i * step
        h = v * unit
        if v > 0:
            p.append(rect(cx - 16, base_y - h, 32, h, fill="#eaf0fd", stroke=NEG, sw=1.8))
            p.append(text(cx, base_y - h - 6, str(v), size=11, color=NEG, bold=True))
        else:
            p.append(text(cx, base_y - 6, "0 → СТОП", size=11, color=POS, bold=True, anchor="middle"))
        # стрілка спаду між стовпчиками
        if i > 0:
            px = base_x + 40 + (i - 1) * step
            ph = vals[i - 1] * unit
            p.append(arrow(px + 16, base_y - ph + 4, cx - 16, base_y - h - 4 if v > 0 else base_y - 14,
                           color=MUTED, sw=1.4))

    note, nw, nh = textbox(W / 2, H - 36,
                           "ВАРІАНТ: невід'ємне ціле, що СТРОГО спадає щоітерації.\nспадає + обмежений нулем знизу → спинитися мусить",
                           size=11.5, bold=True, fill=FILL, stroke=INK, sw=1.8)
    p.append(note)

    render(os.path.join(OUT, "variant.svg"), W, H, *p,
           title="Варіант: спадна величина доводить завершення")


# ── assert-placement: де в циклі стоїть assert(інваріант) і що ловить ─────────
# Ідея: інваріант із паперу переноситься в код як assert на межі ітерації. Один
# на вході в цикл (база), один наприкінці тіла (збереження). Хиба кожного вказує
# на конкретну провину: погана ініціалізація проти зламаного тіла.

def fig_assert_placement():
    W, H = 720, 380
    p = []
    cx = 300
    bw = 300

    # ініціалізація
    a, aw, ah = textbox(cx, 70, "lo = 0;  hi = n - 1;", size=12, fill=FILL,
                        stroke=INK, sw=1.6, min_w=bw)
    p.append(a)

    # assert база
    b, bw1, bh = textbox(cx, 132, "assert( інваріант )", size=12, bold=True,
                         color=NEG, fill="#eaf0fd", stroke=NEG, sw=2.0, min_w=bw)
    p.append(arrow(cx, 70 + ah / 2, cx, 132 - bh / 2, color=INK, sw=1.5))
    p.append(b)

    # рамка тіла циклу
    fy, fh = 176, 132
    p.append(rect(cx - bw / 2, fy, bw, fh, fill="#fafbfc", stroke=INK, sw=1.6))
    p.append(text(cx - bw / 2 + 8, fy + 18, "while (lo <= hi) {", size=11.5,
                  color=INK, anchor="start"))
    p.append(text(cx - bw / 2 + 20, fy + 44, "mid = lo + (hi - lo)/2;", size=10.5,
                  color=MUTED, anchor="start"))
    p.append(text(cx - bw / 2 + 20, fy + 64, "звузити [lo, hi] навколо mid", size=10.5,
                  color=MUTED, anchor="start"))

    # assert збереження наприкінці тіла
    c, cw, ch = textbox(cx, fy + fh - 18, "assert( інваріант )", size=11.5, bold=True,
                        color=WARN, fill=WFILL, stroke=WARN, sw=2.0, min_w=bw - 40)
    p.append(c)
    p.append(text(cx - bw / 2 + 8, fy + fh + 16, "}", size=11.5, color=INK, anchor="start"))

    # стрілка циклу назад
    p.append(arrow(cx + bw / 2, fy + fh - 18, cx + bw / 2 + 28, fy + fh - 18, color=MUTED, sw=1.4))
    p.append(line(cx + bw / 2 + 28, fy + fh - 18, cx + bw / 2 + 28, fy + 18, color=MUTED, sw=1.4))
    p.append(arrow(cx + bw / 2 + 28, fy + 18, cx + bw / 2, fy + 18, color=MUTED, sw=1.4))

    # пояснення провини збоку
    rx = cx + bw / 2 + 60
    p.append(circle(rx, 132, 5, fill=NEG, stroke=NEG, sw=1))
    p.append(text(rx + 14, 136, "хиба тут → погана", size=10.5, color=INK, anchor="start"))
    p.append(text(rx + 14, 150, "ІНІЦІАЛІЗАЦІЯ", size=10.5, color=NEG, anchor="start", bold=True))

    p.append(circle(rx, fy + fh - 18, 5, fill=WARN, stroke=WARN, sw=1))
    p.append(text(rx + 14, fy + fh - 22, "хиба тут → тіло", size=10.5, color=INK, anchor="start"))
    p.append(text(rx + 14, fy + fh - 8, "ЗЛАМАЛО інваріант", size=10.5, color=WARN, anchor="start", bold=True))

    note, nw, nh = textbox(W / 2, H - 30,
                           "інваріант із доведення → assert на межі ітерації:\nпадає точно там, де припущення вперше зламалося",
                           size=11.5, bold=True, fill=FILL, stroke=INK, sw=1.8)
    p.append(note)

    render(os.path.join(OUT, "assert-placement.svg"), W, H, *p,
           title="assert(інваріант) у циклі: де стоїть і що ловить")


if __name__ == "__main__":
    fig_three_steps()
    fig_search_window()
    fig_variant()
    fig_assert_placement()
    print("OK: figures written to", OUT)
