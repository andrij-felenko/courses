# -*- coding: utf-8 -*-
"""Фігури до статті «Перетворення джерел» (book/electronics/analog/source-transformation).
Три фігури:
  twins.svg     — два обличчя одного двополюсника: V-форма ⇄ I-форма, формули переходу
  endpoints.svg — ЧОМУ еквівалентні: на холостому ході й на короткому обидві дають те саме
  collapse.svg  — користь: послідовність перетворень «згортає» драбину в одне джерело
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def vsource(cx, cy, r=18, label=None, col=POS):
    """Джерело напруги: кружечок з «+/−» всередині."""
    out = [circle(cx, cy, r, fill="#ffffff", stroke=col, sw=2.0),
           text(cx, cy - 3, "+", size=14, color=col, bold=True),
           line(cx - 6, cy + 6, cx + 6, cy + 6, color=col, sw=1.6),
           text(cx, cy + 16, "−", size=14, color=col, bold=True)]
    if label:
        out.append(text(cx - r - 8, cy + 4, label, size=13, color=col, bold=True, anchor="end"))
    return "".join(out)


def isource(cx, cy, r=18, label=None, col=NEG, up=True):
    """Джерело струму: кружечок зі стрілкою всередині."""
    out = [circle(cx, cy, r, fill="#ffffff", stroke=col, sw=2.0)]
    if up:
        out.append(arrow(cx, cy + 9, cx, cy - 9, color=col, sw=2.2))
    else:
        out.append(arrow(cx, cy - 9, cx, cy + 9, color=col, sw=2.2))
    if label:
        out.append(text(cx + r + 8, cy + 4, label, size=13, color=col, bold=True, anchor="start"))
    return "".join(out)


def res_h(x0, x1, y, label=None, col=INK, above=True):
    """Горизонтальний резистор-зигзаг між (x0,y) та (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 7
    out.append(line(x0, y, x0 + seg, y, color=col, sw=1.6))
    xx = x0 + seg
    prev = (xx, y)
    for i in range(n):
        ny = y - amp if i % 2 == 0 else y + amp
        nx = xx + seg
        out.append(line(prev[0], prev[1], nx if i == n - 1 else xx + seg / 2 + (0), ny, color=col, sw=1.6)) if False else None
        # простіше: зигзаг точками
        xx += seg
    # надійніший зигзаг
    out = [line(x0, y, x0 + seg, y, color=col, sw=1.6)]
    pts = [(x0 + seg, y)]
    for i in range(n):
        px = x0 + seg + seg * (i + 0.5)
        py = y - amp if i % 2 == 0 else y + amp
        pts.append((px, py))
    pts.append((x1 - seg, y))
    for i in range(len(pts) - 1):
        out.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=col, sw=1.6))
    out.append(line(x1 - seg, y, x1, y, color=col, sw=1.6))
    if label:
        ly = y - amp - 10 if above else y + amp + 16
        out.append(text((x0 + x1) / 2, ly, label, size=12, color=col, bold=True, anchor="middle"))
    return "".join(out)


def res_v(x, y0, y1, label=None, col=INK, side="right"):
    """Вертикальний резистор-зигзаг між (x,y0) та (x,y1)."""
    n = 6
    seg = (y1 - y0) / (n + 1)
    amp = 7
    out = [line(x, y0, x, y0 + seg, color=col, sw=1.6)]
    pts = [(x, y0 + seg)]
    for i in range(n):
        py = y0 + seg + seg * (i + 0.5)
        px = x + amp if i % 2 == 0 else x - amp
        pts.append((px, py))
    pts.append((x, y1 - seg))
    for i in range(len(pts) - 1):
        out.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=col, sw=1.6))
    out.append(line(x, y1 - seg, x, y1, color=col, sw=1.6))
    if label:
        lx = x + amp + 10 if side == "right" else x - amp - 10
        an = "start" if side == "right" else "end"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=12, color=col, bold=True, anchor=an))
    return "".join(out)


def term(cx, cy, lbl, col=INK):
    return circle(cx, cy, 3.2, fill=col, stroke=col) + text(cx + 12, cy + 4, lbl, size=12, color=col, bold=True, anchor="start")


# ════════════════════════════════════════════════════════════════════════════
# 1. twins.svg — два обличчя одного двополюсника
# ════════════════════════════════════════════════════════════════════════════
def fig_twins():
    W, H = 680, 360
    f = []

    # ── ліворуч: V-форма (джерело напруги + послідовний R) ──
    f.append(rect(40, 70, 250, 210, fill="#fdecea", stroke=POS, sw=1.6, rx=12))
    f.append(text(165, 96, "V-форма", size=14, bold=True, color=POS))
    f.append(text(165, 114, "(еквівалент Тевеніна)", size=11, color=MUTED))
    # коло: джерело знизу зліва, R згори, до клем
    vx, vy = 90, 215
    f.append(vsource(vx, vy, label="V", col=POS))
    f.append(line(vx, vy - 18, vx, 150, color=INK, sw=1.6))           # вгору
    f.append(res_h(vx, 230, 150, label="R", col=INK, above=True))     # послідовний R угорі
    f.append(line(230, 150, 262, 150, color=INK, sw=1.6))             # до верхньої клеми
    f.append(line(vx, vy + 18, vx, 250, color=INK, sw=1.6))           # вниз
    f.append(line(vx, 250, 262, 250, color=INK, sw=1.6))              # до нижньої клеми
    f.append(term(262, 150, "A", col=INK))
    f.append(term(262, 250, "B", col=INK))

    # ── праворуч: I-форма (джерело струму ∥ R) ──
    f.append(rect(390, 70, 250, 210, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=12))
    f.append(text(515, 96, "I-форма", size=14, bold=True, color=NEG))
    f.append(text(515, 114, "(еквівалент Нортона)", size=11, color=MUTED))
    ix, iy = 445, 215
    f.append(isource(ix, iy, label=None, col=NEG, up=True))
    f.append(text(ix, iy + 40, "I", size=13, color=NEG, bold=True))
    f.append(line(ix, iy - 18, ix, 150, color=INK, sw=1.6))           # вгору від джерела
    f.append(line(ix, iy + 18, ix, 250, color=INK, sw=1.6))           # вниз від джерела
    # паралельний R праворуч від джерела
    rx = 545
    f.append(line(ix, 150, rx, 150, color=INK, sw=1.6))
    f.append(line(ix, 250, rx, 250, color=INK, sw=1.6))
    f.append(res_v(rx, 150, 250, label="R", col=INK, side="left"))
    # до клем
    f.append(line(rx, 150, 612, 150, color=INK, sw=1.6))
    f.append(line(rx, 250, 612, 250, color=INK, sw=1.6))
    f.append(term(612, 150, "A", col=INK))
    f.append(term(612, 250, "B", col=INK))

    # ── стрілка-міст із формулами переходу ──
    f.append(arrow(300, 165, 380, 165, color=FIELD, sw=2.6))
    f.append(arrow(380, 195, 300, 195, color=FIELD, sw=2.6))
    bb, w0, h0 = textbox(340, 300, "V = I·R     I = V / R     R — той самий",
                         size=12, color=INK, fill="#eef7f0", stroke=FIELD, bold=True)
    f.append(bb)

    f.append(text(W / 2, 40, "Один двополюсник — два рівноправні вигляди, однакові на клемах",
                  size=15, bold=True))
    render(os.path.join(IMG, "twins.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. endpoints.svg — чому еквівалентні: збігаються в двох крайніх точках
# ════════════════════════════════════════════════════════════════════════════
def fig_endpoints():
    W, H = 680, 320
    f = []
    f.append(text(W / 2, 34, "Чому рівноцінні: обидва вигляди дають те саме на обох кінцях",
                  size=15, bold=True))

    # ── ліва панель: холостий хід (клеми розімкнені) ──
    f.append(rect(40, 70, 290, 200, fill="#f7f9fb", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(185, 96, "Холостий хід  (R_load = ∞)", size=13, bold=True, color=INK))
    f.append(text(185, 118, "навантаження від’єднано — струму немає", size=11, color=MUTED))
    bb, _, _ = textbox(120, 175, "V-форма:\nна R нема падіння →\nU = V", size=11, color=POS, fill="#fdecea", stroke=POS)
    f.append(bb)
    bb, _, _ = textbox(250, 175, "I-форма:\nвесь I тече крізь R →\nU = I·R", size=11, color=NEG, fill="#eaf0fd", stroke=NEG)
    f.append(bb)
    bb, _, _ = textbox(185, 245, "V = I·R  →  напруга на клемах однакова",
                       size=11, color=INK, fill="#eef7f0", stroke=FIELD, bold=True)
    f.append(bb)

    # ── права панель: коротке (клеми замкнені) ──
    f.append(rect(350, 70, 290, 200, fill="#f7f9fb", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(495, 96, "Коротке замикання  (R_load = 0)", size=13, bold=True, color=INK))
    f.append(text(495, 118, "клеми з’єднані напряму — напруги немає", size=11, color=MUTED))
    bb, _, _ = textbox(430, 175, "V-форма:\nувесь V на R →\nI_sc = V / R", size=11, color=POS, fill="#fdecea", stroke=POS)
    f.append(bb)
    bb, _, _ = textbox(560, 175, "I-форма:\nR закорочено →\nI_sc = I", size=11, color=NEG, fill="#eaf0fd", stroke=NEG)
    f.append(bb)
    bb, _, _ = textbox(495, 245, "I = V / R  →  струм короткого однаковий",
                       size=11, color=INK, fill="#eef7f0", stroke=FIELD, bold=True)
    f.append(bb)

    f.append(text(W / 2, 304, "Дві крайні точки збігаються — а між ними обидва вигляди лінійні, тож збігаються скрізь",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "endpoints.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. collapse.svg — користь: ланцюжок перетворень згортає схему
# ════════════════════════════════════════════════════════════════════════════
def fig_collapse():
    W, H = 700, 300
    f = []
    f.append(text(W / 2, 32, "Навіщо це: ланцюжок перетворень згортає схему до одного джерела",
                  size=15, bold=True))

    boxes = [
        (60,  "V → I", "джерело\nU з R_s", POS),
        (235, "об’єднати", "R_s ∥ R_p\n(паралельні)", NEG),
        (410, "I → V", "назад у\nV з одним R", POS),
        (585, "готово", "одне\nджерело", FIELD),
    ]
    y = 150
    for i, (x, top, body, col) in enumerate(boxes):
        fill = "#eef7f0" if col == FIELD else ("#fdecea" if col == POS else "#eaf0fd")
        f.append(rect(x - 6, 78, 100, 130, fill=fill, stroke=col, sw=1.8, rx=10))
        f.append(text(x + 44, 100, top, size=13, bold=True, color=col))
        f.append(mtext(x + 44, 138, body.split("\n"), size=11, color=INK))
        if i < len(boxes) - 1:
            f.append(arrow(x + 96, y, x + 96 + 36, y, color=INK, sw=2.4))

    bb, _, _ = textbox(W / 2, 250,
                       "Кожне перетворення не міняє того, що бачить навантаження —\nале дозволяє злити сусідні елементи, які раніше «не складалися»",
                       size=11, color=INK, fill="#f4f6f8", stroke=MUTED)
    f.append(bb)
    render(os.path.join(IMG, "collapse.svg"), W, H, *f)


if __name__ == "__main__":
    fig_twins()
    fig_endpoints()
    fig_collapse()
    print("OK: 3 фігури у", IMG)
