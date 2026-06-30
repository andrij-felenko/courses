# -*- coding: utf-8 -*-
"""Фігури до статті «Ієрархічні схеми і листи» (book/electronics/analog/hierarchical-schematics).
Чотири фігури:
  nesting.svg   — ідея: блок-символ на верхньому листі «розкривається» у вкладений лист
  port.svg      — як сигнал перетинає межу: вивід блоку ↔ ієрархічний порт усередині (за іменем)
  reuse.svg     — повторне використання: один лист-блок «АМП» поставлено чотири рази
  flat-hier.svg — два устрої: плаский набір листів-рівних vs ієрархічне дерево
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def sheet(x, y, w, h, title, fill="#f4f6f8", stroke=INK, tcol=INK):
    """Прямокутник-«лист» із заголовком угорі."""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=2, rx=8),
           text(x + w / 2, y + 20, title, size=13, color=tcol, bold=True)]
    return "".join(out)


def pin(x, y, name, side="left", col=NEG):
    """Маленький квадратик-вивід із підписом на боці блоку."""
    s = 7
    out = [rect(x - s / 2, y - s / 2, s, s, fill="#ffffff", stroke=col, sw=1.8, rx=1)]
    if side == "left":
        out.append(text(x + 10, y + 4, name, size=11, color=col, anchor="start"))
    else:
        out.append(text(x - 10, y + 4, name, size=11, color=col, anchor="end"))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. nesting.svg — блок на верхньому листі розкривається у вкладений лист
# ════════════════════════════════════════════════════════════════════════════
def fig_nesting():
    W, H = 720, 380
    f = []
    f.append(text(W / 2, 30, "Блок-символ ховає цілий лист усередині", size=16, bold=True))

    # верхній лист із трьома блоками
    tx, ty, tw, th = 40, 60, 300, 280
    f.append(sheet(tx, ty, tw, th, "ВЕРХНІЙ ЛИСТ (система)", fill="#eef2f7"))

    # три блоки-символи
    blocks = [("Живлення", ty + 50), ("Підсилювач", ty + 130), ("АЦП", ty + 210)]
    bx, bw, bh = tx + 70, 160, 54
    yexp = None
    for name, by in blocks:
        col = FIELD if name == "Підсилювач" else INK
        f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=col, sw=2.2, rx=6))
        f.append(text(bx + bw / 2, by + bh / 2 - 2, name, size=13, color=col, bold=True))
        f.append(text(bx + bw / 2, by + bh / 2 + 15, "(лист-блок)", size=10, color=MUTED))
        # виводи блоку
        f.append(rect(bx - 4, by + 14, 8, 8, fill="#fff", stroke=NEG, sw=1.6, rx=1))
        f.append(rect(bx + bw - 4, by + 14, 8, 8, fill="#fff", stroke=NEG, sw=1.6, rx=1))
        if name == "Підсилювач":
            yexp = by + bh / 2

    # стрілка «розкрити» від блоку Підсилювач до вкладеного листа
    cx0 = bx + bw + 4
    f.append(arrow(cx0 + 6, yexp, 420, yexp, color=FIELD, sw=2.6))
    f.append(text((cx0 + 420) / 2 + 6, yexp - 12, "розкрити", size=11, color=FIELD, bold=True))
    f.append(text((cx0 + 420) / 2 + 6, yexp + 16, "(подвійний клік)", size=10, color=MUTED))

    # вкладений лист — вміст блоку «Підсилювач»
    cxx, cyy, cww, chh = 430, 120, 250, 170
    f.append(sheet(cxx, cyy, cww, chh, "ЛИСТ «Підсилювач»", fill="#eef7f0", stroke=FIELD, tcol=FIELD))
    # спрощений ОП-трикутник усередині
    ax, ay = cxx + 90, cyy + 90
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="#ffffff" stroke="%s" stroke-width="2"/>'
             % (ax, ay - 26, ax, ay + 26, ax + 54, ay, INK))
    f.append(line(ax - 40, ay - 14, ax, ay - 14, color=INK, sw=1.6))
    f.append(line(ax - 40, ay + 14, ax, ay + 14, color=INK, sw=1.6))
    f.append(line(ax + 54, ay, ax + 92, ay, color=INK, sw=1.6))
    f.append(text(ax - 18, ay - 18, "−", size=13, color=NEG, bold=True))
    f.append(text(ax - 18, ay + 24, "+", size=13, color=POS, bold=True))
    # порти вкладеного листа (за іменем збігаються з виводами блоку)
    f.append(pin(cxx + 6, cyy + 60, "IN", side="left", col=NEG))
    f.append(pin(cxx + cww - 6, cyy + 76, "OUT", side="right", col=NEG))

    body, _, _ = textbox(W / 2, 360,
                         "На верхньому листі видно лише назву й виводи; деталі живуть на власному листі блоку",
                         size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "nesting.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. port.svg — вивід блоку (батько) ↔ ієрархічний порт (дитина), збіг імен
# ════════════════════════════════════════════════════════════════════════════
def fig_port():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 30, "Сигнал перетинає межу листа за збігом імені", size=16, bold=True))

    # батьківський бік — блок із виводом
    px, py, pw, ph = 70, 90, 200, 150
    f.append(sheet(px, py, pw, ph, "БАТЬКІВСЬКИЙ ЛИСТ", fill="#eef2f7"))
    bx, by, bw, bh = px + 40, py + 55, 120, 54
    f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=INK, sw=2.2, rx=6))
    f.append(text(bx + bw / 2, by + bh / 2 + 4, "Підсилювач", size=12, color=INK, bold=True))
    # вивід блоку «OUT» праворуч
    f.append(rect(bx + bw - 5, by + 18, 10, 10, fill="#fff", stroke=NEG, sw=2, rx=1))
    f.append(text(bx + bw - 16, by + 27, "OUT", size=11, color=NEG, anchor="end", bold=True))
    f.append(text(bx + bw / 2, by - 10, "вивід блоку", size=10, color=MUTED))
    f.append(line(bx + bw + 5, by + 23, px + pw, by + 23, color=INK, sw=1.8))

    # дочірній бік — порт усередині
    cx, cy, cw, ch = 430, 90, 200, 150
    f.append(sheet(cx, cy, cw, ch, "ЛИСТ «Підсилювач»", fill="#eef7f0", stroke=FIELD, tcol=FIELD))
    # ієрархічний порт-«прапорець» OUT праворуч усередині
    fx, fy = cx + cw - 70, cy + 78
    f.append(line(cx, fy, fx, fy, color=INK, sw=1.8))
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f Z" '
             'fill="#ffffff" stroke="%s" stroke-width="2"/>'
             % (fx, fy - 12, fx + 46, fy - 12, fx + 62, fy, fx + 46, fy + 12, fx, fy + 12, NEG))
    f.append(text(fx + 28, fy + 4, "OUT", size=11, color=NEG, bold=True))
    f.append(text(cx + cw / 2 - 10, cy + 124, "ієрархічний порт", size=10, color=MUTED))
    f.append(line(cx, fy, cx - 20, fy, color=INK, sw=1.8))

    # зв'язок за іменем
    f.append(line(px + pw, by + 23, cx - 20, fy, color=POS, sw=2.4, dash="7 5"))
    body, w0, _ = textbox((px + pw + cx) / 2, (by + 23 + fy) / 2 - 44,
                          "однакове ім’я\n«OUT»\n= один ланцюг", size=11, color=POS,
                          fill="#fdecea", stroke=POS, bold=True)
    f.append(body)

    body, _, _ = textbox(W / 2, 322,
                         "Вивід на символі блоку й порт усередині листа зшиваються не дротом, а збігом імені",
                         size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "port.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. reuse.svg — один лист-блок поставлено чотири рази (повторне використання)
# ════════════════════════════════════════════════════════════════════════════
def fig_reuse():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 30, "Один лист — чотири однакові канали", size=16, bold=True))

    # джерело: єдиний лист-визначення
    sx, sy, sw, sh = 40, 90, 180, 150
    f.append(sheet(sx, sy, sw, sh, "ОДИН ЛИСТ «Канал»", fill="#eef7f0", stroke=FIELD, tcol=FIELD))
    f.append(text(sx + sw / 2, sy + 60, "R1  C1  U1", size=13, color=INK, bold=True))
    f.append(text(sx + sw / 2, sy + 84, "(намальовано раз)", size=10, color=MUTED))
    f.append(pin(sx + 6, sy + 110, "IN", side="left", col=NEG))
    f.append(pin(sx + sw - 6, sy + 110, "OUT", side="right", col=NEG))

    # чотири екземпляри
    f.append(text(470, 70, "поставлено чотири рази:", size=12, color=INK, bold=True))
    insts = [("Канал 1", "R101 C101 U101", 300),
             ("Канал 2", "R201 C201 U201", 348),
             ("Канал 3", "R301 C301 U301", 396),
             ("Канал 4", "R401 C401 U401", 444)]
    iy = 95
    iw, ih = 250, 50
    for name, des, _x in insts:
        f.append(rect(420, iy, iw, ih, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
        f.append(text(420 + 12, iy + ih / 2 + 4, name, size=12, color=FIELD, bold=True, anchor="start"))
        f.append(text(420 + iw - 12, iy + ih / 2 + 4, des, size=11, color=INK, anchor="end"))
        iy += ih + 8

    # стрілка від визначення до екземплярів
    f.append(arrow(sx + sw + 6, sy + sh / 2, 414, 150, color=FIELD, sw=2.4))
    f.append(text((sx + sw + 414) / 2 + 4, sy + sh / 2 - 12, "×4", size=14, color=FIELD, bold=True))

    body, _, _ = textbox(W / 2, 338,
                         "Правиш лист один раз — змінюються всі чотири; номери деталей розводяться автоматично (R101, R201…)",
                         size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "reuse.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. flat-hier.svg — плаский набір листів vs ієрархічне дерево
# ════════════════════════════════════════════════════════════════════════════
def fig_flat_hier():
    W, H = 720, 380
    f = []

    # ── ліворуч: плаский набір ───────────────────────────────────────────────
    f.append(text(180, 36, "Плаский набір листів", size=15, bold=True, color=NEG))
    f.append(text(180, 56, "листи-рівні, зшиті глобальними мітками", size=11, color=MUTED))
    flat = [(70, 90), (200, 90), (70, 200), (200, 200)]
    fw, fh = 110, 80
    for i, (fx, fy) in enumerate(flat, 1):
        f.append(rect(fx, fy, fw, fh, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
        f.append(text(fx + fw / 2, fy + fh / 2 + 4, "Лист %d" % i, size=12, color=NEG, bold=True))
    # глобальні мітки, що зшивають листи (пунктир між ними)
    f.append(line(180, 130, 200, 130, color=POS, sw=2, dash="5 4"))
    f.append(line(125, 170, 125, 200, color=POS, sw=2, dash="5 4"))
    f.append(line(255, 170, 255, 200, color=POS, sw=2, dash="5 4"))
    f.append(line(180, 240, 200, 240, color=POS, sw=2, dash="5 4"))
    f.append(text(180, 312, "усі рівні; зв'язок —", size=11, color=POS, anchor="middle"))
    f.append(text(180, 328, "«+5В тут = +5В там»", size=11, color=POS, anchor="middle"))

    # роздільник
    f.append(line(370, 70, 370, 340, color="#d8dce1", sw=1.5, dash="3 4"))

    # ── праворуч: ієрархічне дерево ───────────────────────────────────────────
    f.append(text(545, 36, "Ієрархічне дерево", size=15, bold=True, color=FIELD))
    f.append(text(545, 56, "верхній лист → листи-блоки → їхні листи", size=11, color=MUTED))
    # корінь
    rx, ry, rw, rh = 490, 80, 120, 46
    f.append(rect(rx, ry, rw, rh, fill="#eef7f0", stroke=FIELD, sw=2.4, rx=6))
    f.append(text(rx + rw / 2, ry + rh / 2 + 4, "Верхній", size=12, color=FIELD, bold=True))
    # двоє дітей
    kids = [(440, 190, "Блок A"), (590, 190, "Блок B")]
    kw, kh = 110, 44
    for kx, ky, nm in kids:
        f.append(line(rx + rw / 2, ry + rh, kx + kw / 2, ky, color=FIELD, sw=2))
        f.append(rect(kx, ky, kw, kh, fill="#ffffff", stroke=FIELD, sw=2, rx=6))
        f.append(text(kx + kw / 2, ky + kh / 2 + 4, nm, size=12, color=INK, bold=True))
    # онуки під Блоком A
    gx0 = 440
    gk = [(410, 290, "A.1"), (520, 290, "A.2")]
    gw, gh = 90, 40
    for gx, gy, nm in gk:
        f.append(line(gx0 + kw / 2, 190 + kh, gx + gw / 2, gy, color=FIELD, sw=1.8))
        f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=MUTED, sw=1.8, rx=6))
        f.append(text(gx + gw / 2, gy + gh / 2 + 4, nm, size=11, color=INK, bold=True))

    render(os.path.join(IMG, "flat-hier.svg"), W, H, *f)


if __name__ == "__main__":
    fig_nesting()
    fig_port()
    fig_reuse()
    fig_flat_hier()
    print("OK: 4 фігури у", IMG)
